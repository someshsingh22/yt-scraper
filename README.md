# yt-scraper
Large Scale YouTube Scraper

## Usage

Here's how you can use the functions provided by MyPackage:


### Scraping Videos/Audios

```python
from yt_scraper import scrape_yt_data


# Define the root directories
CHANNEL_ROOT = "SAVE/DATA/HERE"

if __name__ == "__main__":
    # Initialize an empty database
    db = {}

    # Replace this with your video ID
    video_id = "YOUR_VIDEO_ID"

    # Scrape YouTube data for the specified video
    scrape_yt_data(video_id, db, CHANNEL_ROOT, skip=False, audio_only=False)
```

### Scraping Metadata (Likes, Views, Duration, Replay Graph ..)
```python
from yt_scraper import YTMeta


print YTMeta("SAVE/DATA/HERE/$id.pkl").export()
```

### Scraping Comments
```python
from yt_scraper import PytubeCommentDownloader


pyt = PytubeCommentDownloader()
pkl = pickle.load("SAVE/DATA/HERE/$id.pkl")
gen = pyt.get_comments_from_pytube(pkl)
for idx in range(5):
    comment = next(gen)
```