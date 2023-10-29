import json
import pickle
import re
import logging


class YTMeta:
    def __init__(self, pkl):
        self.pkl = pkl
        self.yt = pickle.load(open(pkl, "rb"))
        self.set_chapters()
        self.set_likes()
        self.views = self.yt.views
        self.length = self.yt.length
        self.set_replays()

    def set_likes(self):
        try:
            like_template = r"[0-9]{1,3},?[0-9]{0,3},?[0-9]{0,3} like"
            str_likes = re.search(like_template, str(self.yt.initial_data)).group(0)
            self.likes = int(str_likes.split(" ")[0].replace(",", ""))
        except:
            logging.error("Cannot Retrieve Likes for " + self.pkl)
            self.likes = None

    def set_replays(self):
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

    def set_chapters(self):
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

    def export(self):
        export = self.__dict__
        export.pop("yt")
        return export
