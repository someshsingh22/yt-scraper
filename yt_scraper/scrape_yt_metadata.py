import json
import logging
import re

from yt_scraper.minitube import MiniTube


class YTMeta:
    def __init__(self, yt_obj: MiniTube):
        """
        Initialize YTMeta object.

        Parameters:
        - yt_obj (MiniTube): A MiniTube YouTube object representing the video.
        """
        self.yt = yt_obj
        self.set_chapters()
        self.set_likes()
        self.views = self.yt.views
        self.length = self.yt.length
        self.set_replays()

    def set_likes(self) -> None:
        """
        Set the number of likes for the video.
        """
        try:
            like_template = r"[0-9]{1,3},?[0-9]{0,3},?[0-9]{0,3} like"
            str_likes = re.search(like_template, str(self.yt.initial_data)).group(0)
            self.likes = int(str_likes.split(" ")[0].replace(",", ""))
        except:
            logging.error("Cannot Retrieve Likes for " + self.pkl)
            self.likes = None

    def set_replays(self) -> None:
        """
        Set the replay information for the video.
        """
        html = self.yt.watch_html
        start = html.find('"markers":[{')
        if start == -1:
            self.replays = None
            return None
        html = html[start:]
        hmap = json.loads("{" + html[: html.find("}],")] + "}]}")
        if "title" in json.dumps(hmap):
            self.replays = None
            return None
        self.replays = [f["intensityScoreNormalized"] for f in hmap["markers"]]

    def set_chapters(self) -> None:
        """
        Set the chapter information for the video.
        """
        html = self.yt.watch_html
        start = html.find('"chapters":[')
        if start == -1:
            self.chapters = None
            return None
        html = "{" + html[start:]
        end = html.find("}]}}}],")
        try:
            stamps = json.loads(html[:end] + "}]}}}]}")
        except json.JSONDecodeError as e:
            stamps = json.loads(html[: html.find("}}}}],")] + "}}}}]}")
        self.chapters = [
            {
                "chapter": ch["chapterRenderer"]["title"]["simpleText"],
                "start": ch["chapterRenderer"]["timeRangeStartMillis"] // 1000,
            }
            for ch in stamps["chapters"]
        ]

    def export(self) -> dict:
        """
        Export the YTMeta object as a dictionary, excluding the 'yt' attribute.

        Returns:
        - dict: Dictionary containing YTMeta attributes.
        """
        export = self.__dict__
        export.pop("yt")
        return export
