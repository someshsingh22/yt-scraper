import os
import pickle
import random
import time
import requests

from pytube import YouTube


def download_stream(url, filepath):
    try:
        # Send an HTTP GET request to the stream URL
        response = requests.get(url, stream=True)

        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            # Open a local file for writing the stream
            with open(filepath, "wb") as file:
                # Iterate through the content of the response and write it to the file
                for chunk in response.iter_content(chunk_size=1024):
                    if chunk:
                        file.write(chunk)

            return filepath  # Return the local file path if successful
        else:
            print(f"Failed to download the stream. Status code: {response.status_code}")
    except Exception as e:
        print(f"An error occurred: {e}")

    return None  # Return None if the download fails


def scrape_yt_data(
    id,
    db,
    CHANNEL_ROOT,
    skip=True,
    audio_only=True,
    condition=lambda x: x.length < 1000,
    **kwargs,
):
    if (id in db) and skip:
        return db[id]
    else:
        entry = dict()
        yt = YouTube("https://www.youtube.com/watch?v=" + id, **kwargs)
        if not condition(yt):
            return None
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
                if "proxies" in kwargs:
                    downloaded = download_stream(
                        video.url, os.path.join(CHANNEL_ROOT, f"{id}.mp4")
                    )
                    if downloaded:
                        entry["video"] = f"{CHANNEL_ROOT}/{id}.mp4"
                    else:
                        return video.url
                else:
                    video.download()
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
        if not entry["caption"]:
            entry["auto_caption"] = yt.captions.get_by_language_code(
                "a.en"
            ).xml_captions
        else:
            entry["auto_caption"] = None
        pickle.dump(yt, open(f"{CHANNEL_ROOT}/{id}.pkl", "wb"))
        entry["pickle"] = f"{CHANNEL_ROOT}/{id}.pkl"
        entry["length"] = yt.length
        db[id] = entry
        time.sleep(random.random() * 2)
        return entry
