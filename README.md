# yt_scraper

`yt_scraper` is a lightweight and research-friendly tool for scraping data from YouTube videos. It combines functionalities from `pytube` and `youtubecommentdownloader` to provide a budget-friendly solution, especially when dealing with proxies.

## Table of Contents

1. [Introduction](#introduction)
2. [Installation](#installation)
3. [Usage](#usage)

## Introduction

`yt_scraper` is designed to be a lightweight and efficient solution for researchers working with YouTube data. It utilizes the power of `pytube` for video scraping and incorporates features from `youtubecommentdownloader` for efficient comment retrieval. The tool is optimized for research scenarios and is budget-friendly, particularly when working with proxies.

## Installation

To install `yt_scraper`, use the following command:

```bash
pip install -e git+https://github.com/someshsingh22/yt-scraper.git#egg=yt_scraper
```

This will automatically install the required dependencies specified in the `requirements.txt` file.

## Usage

`yt_scraper` provides two primary components: the `scrape_yt_data` function for video scraping and the `YTMeta` class for gathering metadata.

### `scrape_yt_data` Function

This function is used to scrape data from a YouTube video. It takes various parameters, including the video ID, a database for storing scraped data, the root directory for storing downloaded media, and more. The function returns a dictionary containing scraped data and status information.

```python
from yt_scraper import scrape_yt_data

video_id = "your_video_id"
database = {}
channel_root = "your_channel_root_directory"
proxies = {
    "http": "http://your_proxy",
    "https": "https://your_proxy"
}

scraped_data, minitube_obj = scrape_yt_data(video_id, database, channel_root, proxies=proxies)
```

### `YTMeta` Class

This class gathers metadata from a YouTube video using a `pytube` YouTube object.

```python
from yt_scraper import YTMeta, MiniTube

yt_video = MiniTube("https://www.youtube.com/watch?v=your_video_id")
meta_data = YTMeta(yt_video)
```
