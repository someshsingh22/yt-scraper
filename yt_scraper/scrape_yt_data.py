import os
import pickle
import random
import time

from pytube import YouTube


def scrape_yt_data(id, db, CHANNEL_ROOT, skip=True, audio_only=True):
    if (id in db) and skip:
        return db[id]
    else:
        entry = dict()
        yt = YouTube("https://www.youtube.com/watch?v=" + id)
        if not audio_only:
            if os.path.exists(f"{CHANNEL_ROOT}/{id}.mp4"):
                entry["video"] = f"{CHANNEL_ROOT}/{id}.mp4"
            else:
                video = (
                    yt.streams.filter(progressive=True, file_extension="mp4")
                    .order_by("resolution")
                    .desc()
                    .first()
                )
                video.download(
                    CHANNEL_ROOT,
                    filename=f"{id}.mp4",
                )
                entry["video"] = f"{CHANNEL_ROOT}/{id}.mp4"
        else:
            if os.path.exists(f"{CHANNEL_ROOT}/{id}.webm"):
                entry["audio"] = f"{CHANNEL_ROOT}/{id}.webm"
            else:
                audio = (
                    yt.streams.filter(only_audio=True).order_by("abr").desc().first()
                )
                audio.download(
                    CHANNEL_ROOT,
                    filename=f"{id}.{audio.mime_type.split('/')[1]}",
                )
                entry["audio"] = f"{CHANNEL_ROOT}/{id}.{audio.mime_type.split('/')[1]}"
        entry["caption"] = yt.captions.get_by_language_code("en").xml_captions
        pickle.dump(yt, open(f"{CHANNEL_ROOT}/{id}.pkl", "wb"))
        entry["pickle"] = f"{CHANNEL_ROOT}/{id}.pkl"
        entry["length"] = yt.length
        db[id] = entry
        time.sleep(random.random() * 2)
        return entry
