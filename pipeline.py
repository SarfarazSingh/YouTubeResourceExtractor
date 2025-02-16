# pipeline.py
import pandas as pd
import streamlit as st
from youtube_api import get_uploads_playlist_id, get_videos_from_playlist, get_video_description
from resource_extractor import extract_resources, categorize_link

@st.cache_data
def run_pipeline(api_key, channel_id):
    """
    Runs the entire scraping pipeline:
      - Retrieves the uploads playlist ID.
      - Fetches all videos.
      - For each video, gets the description and extracts resources.
    Returns two DataFrames: one for videos and one for resources.
    """
    playlist_id = get_uploads_playlist_id(channel_id, api_key)
    if not playlist_id:
        st.error("Failed to retrieve the uploads playlist ID.")
        return None, None

    videos = get_videos_from_playlist(playlist_id, api_key)
    all_resources = []
    for video in videos:
        description = get_video_description(video["video_id"], api_key)
        resources = extract_resources(description)
        for title, link in resources:
            all_resources.append({
                "video_title": video["title"],
                "video_link": video["link"],
                "resource_title": title,
                "resource_link": link
            })

    videos_df = pd.DataFrame(videos)
    resources_df = pd.DataFrame(all_resources)

    if not resources_df.empty:
        resources_df["category"] = resources_df.apply(
            lambda row: categorize_link(row["resource_link"], row["resource_title"]),
            axis=1
        )

    return videos_df, resources_df
