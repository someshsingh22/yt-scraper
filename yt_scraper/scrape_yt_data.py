import os
import pickle

import requests
from pytube.streams import Stream

from yt_scraper.minitube import MiniTube


def download_stream(stream: Stream, root: str, filename: str, proxies: bool = True):
    """
    Download a stream from a minitube stream object.
    Returns the filepath of the downloaded stream.
    Skip if the file already exists.
    """
    assert (
        proxies
    ), "Proxies must be set to True to download streams. Otherwise, use pytube directly. Or revert to 0.1"
    filepath = os.path.join(root, filename)
    if os.path.exists(filepath):
        return filepath
    else:
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


def scrape_yt_data(
    id,
    db,
    CHANNEL_ROOT,
    skip=True,
    audio_only=True,
    condition=lambda x: True,
    return_yt: bool = True,
    **kwargs,
):
    if (id in db) and skip:
        if return_yt:
            return db[id], pickle.load(open(db[id]["pickle"], "rb"))
        else:
            return db[id]
    else:
        entry = {"id": id, "status": dict()}
        try:
            yt = MiniTube("https://www.youtube.com/watch?v=" + id, **kwargs)
        except Exception as e:
            entry["status"][
                "fetch_error"
            ] = f"Could not fetch https://www.youtube.com/watch?v={id} Failed with error {str(e)}"
            if return_yt:
                return entry, None
            else:
                return entry
        try:
            if not condition(yt):
                entry["status"]["condition_error"] = "Condition not met for " + id
                if return_yt:
                    return entry, yt
                else:
                    return entry
        except:
            entry["status"]["condition_error"] = "Condition cannot be checked for " + id

        mode = "Audio" if audio_only else "Video"

        try:
            if mode == "Video":
                media = (
                    yt.streams.filter(progressive=True, file_extension="mp4")
                    .order_by("resolution")
                    .desc()
                    .first()
                )
                filename = f"{id}.mp4"

            else:
                media = (
                    yt.streams.filter(only_audio=True).order_by("abr").desc().first()
                )
                filename = f"{id}.{media.mime_type.split('/')[1]}"

            download_stream(media, CHANNEL_ROOT, filename, "proxies" in kwargs)
            entry[mode] = out_path = os.path.join(CHANNEL_ROOT, filename)

        except Exception as E:
            entry["status"]["media_error"] = f"{str(E)}\n{id}\n{mode} Only"

        try:
            captions = yt.captions
            if captions.get("en"):
                entry["caption"] = {
                    "xml": captions.get("en").xml_captions,
                    "lang": "en",
                }
            elif captions.get("a.en"):
                entry["caption"] = {
                    "xml": captions.get("a.en").xml_captions,
                    "lang": "a.en",
                }
        except Exception as E:
            entry["status"]["caption_error"] = str(E) + "\n" + id

        pickle.dump(yt, open(f"{CHANNEL_ROOT}/{id}.pkl", "wb"))
        entry["pickle"] = f"{CHANNEL_ROOT}/{id}.pkl"
        try:
            entry["length"] = yt.length
        except:
            entry["length"] = None
            entry["status"]["length_error"] = "Could not extract length"
        db[id] = entry
        if return_yt:
            return entry, yt
        else:
            return entry
