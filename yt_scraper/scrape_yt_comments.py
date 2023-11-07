from youtube_comment_downloader.downloader import *

class PytubeCommentDownloader(YoutubeCommentDownloader):
    def __init__(self):
        super().__init__()

    def get_comments_from_pytube(
        self, pytube_obj, sort_by=SORT_BY_POPULAR, language="en", sleep=0.1
    ):
        html = pytube_obj.watch_html
        ytcfg = json.loads(self.regex_search(html, YT_CFG_RE, default=""))
        if not ytcfg:
            return  # Unable to extract configuration
        if language:
            ytcfg["INNERTUBE_CONTEXT"]["client"]["hl"] = language

        data = json.loads(self.regex_search(html, YT_INITIAL_DATA_RE, default=""))

        item_section = next(self.search_dict(data, "itemSectionRenderer"), None)
        renderer = (
            next(self.search_dict(item_section, "continuationItemRenderer"), None)
            if item_section
            else None
        )
        if not renderer:
            # Comments disabled?
            return

        sort_menu = next(self.search_dict(data, "sortFilterSubMenuRenderer"), {}).get(
            "subMenuItems", []
        )
        if not sort_menu:
            # No sort menu. Maybe this is a request for community posts?
            section_list = next(self.search_dict(data, "sectionListRenderer"), {})
            continuations = list(self.search_dict(section_list, "continuationEndpoint"))
            # Retry..
            data = self.ajax_request(continuations[0], ytcfg) if continuations else {}
            sort_menu = next(
                self.search_dict(data, "sortFilterSubMenuRenderer"), {}
            ).get("subMenuItems", [])
        if not sort_menu or sort_by >= len(sort_menu):
            raise RuntimeError("Failed to set sorting")
        continuations = [sort_menu[sort_by]["serviceEndpoint"]]

        while continuations:
            continuation = continuations.pop()
            response = self.ajax_request(continuation, ytcfg)

            if not response:
                break

            error = next(self.search_dict(response, "externalErrorMessage"), None)
            if error:
                raise RuntimeError("Error returned from server: " + error)

            actions = list(
                self.search_dict(response, "reloadContinuationItemsCommand")
            ) + list(self.search_dict(response, "appendContinuationItemsAction"))
            for action in actions:
                for item in action.get("continuationItems", []):
                    if action["targetId"] in [
                        "comments-section",
                        "engagement-panel-comments-section",
                        "shorts-engagement-panel-comments-section",
                    ]:
                        # Process continuations for comments and replies.
                        continuations[:0] = [
                            ep for ep in self.search_dict(item, "continuationEndpoint")
                        ]
                    if (
                        action["targetId"].startswith("comment-replies-item")
                        and "continuationItemRenderer" in item
                    ):
                        # Process the 'Show more replies' button
                        continuations.append(
                            next(self.search_dict(item, "buttonRenderer"))["command"]
                        )

            for comment in reversed(
                list(self.search_dict(response, "commentRenderer"))
            ):
                result = {
                    "cid": comment["commentId"],
                    "text": "".join(
                        [c["text"] for c in comment["contentText"].get("runs", [])]
                    ),
                    "time": comment["publishedTimeText"]["runs"][0]["text"],
                    "author": comment.get("authorText", {}).get("simpleText", ""),
                    "channel": comment["authorEndpoint"]["browseEndpoint"].get(
                        "browseId", ""
                    ),
                    "votes": comment.get("voteCount", {}).get("simpleText", "0"),
                    "photo": comment["authorThumbnail"]["thumbnails"][-1]["url"],
                    "heart": next(self.search_dict(comment, "isHearted"), False),
                    "reply": "." in comment["commentId"],
                }

                try:
                    result["time_parsed"] = dateparser.parse(
                        result["time"].split("(")[0].strip()
                    ).timestamp()
                except AttributeError:
                    pass

                paid = (
                    comment.get("paidCommentChipRenderer", {})
                    .get("pdgCommentChipRenderer", {})
                    .get("chipText", {})
                    .get("simpleText")
                )
                if paid:
                    result["paid"] = paid

                yield result
            time.sleep(sleep)
