import os
import pickle
import random
import time

import requests
from pytube import YouTube


def download_stream(stream, root, filename, proxies=True):
    if proxies:
        filepath = os.path.join(root, filename)
        response = requests.get(stream.url, stream=True)
        if response.status_code == 200:
            with open(filepath, "wb") as file:
                for chunk in response.iter_content(chunk_size=1024):
                    if chunk:
                        file.write(chunk)
            return filepath
        else:
            print(f"Failed to download the stream. Status code: {response.status_code}")
            return None
    else:
        stream.download(root, filename)


def scrape_yt_data(
    id,
    db,
    CHANNEL_ROOT,
    skip=True,
    audio_only=True,
    condition=lambda x: True,
    **kwargs,
):
    if (id in db) and skip:
        return db[id]
    else:
        entry = {"id": id, "status": dict()}
        yt = YouTube("https://www.youtube.com/watch?v=" + id, **kwargs)
        if not condition(yt):
            entry["status"]["condition_error"] = "Condition not met"
            return entry

        try:
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
                    download_stream(
                        video, CHANNEL_ROOT, f"{id}.mp4", "proxies" in kwargs
                    )
                    entry["video"] = f"{CHANNEL_ROOT}/{id}.mp4"
            else:
                if os.path.exists(f"{CHANNEL_ROOT}/{id}.webm"):
                    entry["audio"] = f"{CHANNEL_ROOT}/{id}.webm"
                else:
                    audio = (
                        yt.streams.filter(only_audio=True)
                        .order_by("abr")
                        .desc()
                        .first()
                    )
                    download_stream(
                        audio,
                        CHANNEL_ROOT,
                        f"{id}.{audio.mime_type.split('/')[1]}",
                        "proxies" in kwargs,
                    )
                    entry[
                        "audio"
                    ] = f"{CHANNEL_ROOT}/{id}.{audio.mime_type.split('/')[1]}"
        except Exception as E:
            entry["status"]["media_error"] = str(E)
            if audio_only:
                entry["status"]["media_error"] += "\nAudio Only"
            else:
                entry["status"]["media_error"] += "\nVideo Only"

        try:
            captions = yt.captions
            if captions.get_by_language_code("en"):
                entry["caption"] = {
                    "xml": captions.get_by_language_code("en").xml_captions,
                    "lang": "en",
                }
            elif captions.get_by_language_code("a.en"):
                entry["caption"] = {
                    "xml": captions.get_by_language_code("a.en").xml_captions,
                    "lang": "a.en",
                }
        except Exception as E:
            entry["status"]["caption_error"] = str(E)

        pickle.dump(yt, open(f"{CHANNEL_ROOT}/{id}.pkl", "wb"))
        entry["pickle"] = f"{CHANNEL_ROOT}/{id}.pkl"
        entry["length"] = yt.length
        db[id] = entry
        time.sleep(random.random() / 2) if "proxies" in kwargs else time.sleep(
            random.random() * 2
        )
        return entry
