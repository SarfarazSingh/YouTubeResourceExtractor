import streamlit as st
import pandas as pd
import requests
import re
import sys
import os
import subprocess

# Your YouTube Data API key and Channel ID for '@amitvarma'
API_KEY = "AIzaSyBgXqdHjowUANqtW6XRSJkzf7kbPD9ur5o"
CHANNEL_ID = "UCs8a-hjf6X4pa-O0orSoC8w"

# -------------------------
# Data Retrieval Functions
# -------------------------

@st.cache_data
def get_uploads_playlist_id(channel_id, api_key):
    """
    Retrieves the playlist ID of the channel's 'uploads' playlist.
    """
    url = "https://www.googleapis.com/youtube/v3/channels"
    params = {
        "part": "contentDetails",
        "id": channel_id,
        "key": api_key
    }
    response = requests.get(url, params=params)
    data = response.json()
    items = data.get("items")
    if items:
        return items[0]["contentDetails"]["relatedPlaylists"]["uploads"]
    return None

@st.cache_data
def get_videos_from_playlist(playlist_id, api_key):
    """
    Fetches all videos from the provided playlist ID.
    """
    base_url = "https://www.googleapis.com/youtube/v3/playlistItems"
    videos = []
    next_page_token = None

    while True:
        params = {
            "part": "snippet",
            "playlistId": playlist_id,
            "maxResults": 50,
            "pageToken": next_page_token,
            "key": api_key
        }
        response = requests.get(base_url, params=params)
        data = response.json()
        for item in data.get("items", []):
            snippet = item.get("snippet", {})
            resource = snippet.get("resourceId", {})
            video_id = resource.get("videoId")
            if video_id:
                videos.append({
                    "title": snippet.get("title", ""),
                    "video_id": video_id,
                    "link": f"https://www.youtube.com/watch?v={video_id}"
                })
        next_page_token = data.get("nextPageToken")
        if not next_page_token:
            break
    return videos

@st.cache_data
def get_video_description(video_id, api_key):
    """
    Retrieves the description for a given video ID.
    """
    url = "https://www.googleapis.com/youtube/v3/videos"
    params = {
        "part": "snippet",
        "id": video_id,
        "key": api_key
    }
    response = requests.get(url, params=params)
    data = response.json()
    items = data.get("items")
    if items:
        return items[0]["snippet"].get("description", "")
    return ""

def extract_resources(description):
    """
    Extracts resources and their links from a video description using regex.
    It looks for a 'USEFUL RESOURCES:' section and parses a numbered list.
    """
    resources = []
    pattern = r"USEFUL RESOURCES:\s*(.*?)\s*(?:\n\n|\Z)"
    match = re.search(pattern, description, re.DOTALL)
    if match:
        resources_section = match.group(1)
        resource_pattern = r"\d+\.\s*(.*?)\s*:\s*(https?://\S+)"
        resources = re.findall(resource_pattern, resources_section)
    return resources

def categorize_link(link, title):
    """
    Categorizes a resource based on its link and title.
    Returns one of: 'Twitter', 'Books', 'Wikipedia', 'Blogs', or 'Common'.
    """
    lwr_link = link.lower()
    lwr_title = title.lower()
    if "twitter.com" in lwr_link:
        return "Twitter"
    elif "amazon" in lwr_link or "amzn." in lwr_link:
        return "Books"
    elif "wikipedia.org" in lwr_link:
        return "Wikipedia"
    elif "blog" in lwr_link or "blog" in lwr_title:
        return "Blogs"
    elif "youtube.com" in lwr_link:
        return "Youtube"
    else:
        return "Common"

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
    # Add a category column to resources_df
    if not resources_df.empty:
        resources_df["category"] = resources_df.apply(
            lambda row: categorize_link(row["resource_link"], row["resource_title"]),
            axis=1
        )
    return videos_df, resources_df

# -------------------------
# Streamlit App UI
# -------------------------

st.set_page_config(page_title="YouTube Channel Data Viewer", layout="wide")
st.title("YouTube Channel Data Viewer")
st.write("This app scrapes YouTube channel data and displays video links along with extracted resources categorized for easier navigation.")

if st.button("Run Scraping Pipeline"):
    with st.spinner("Fetching and processing data..."):
        videos_df, resources_df = run_pipeline(API_KEY, CHANNEL_ID)
    if videos_df is not None:
        st.success(f"Found {len(videos_df)} videos!")
        # Display video links in one tab
        st.subheader("Video Links")
        st.dataframe(videos_df, use_container_width=True)

        # Display categorized resources in separate tabs if any resources are found
        if not resources_df.empty:
            st.success(f"Extracted {len(resources_df)} resources.")
            # Determine the unique categories present
            categories = sorted(resources_df["category"].unique())
            tabs = st.tabs(categories)
            for tab, cat in zip(tabs, categories):
                with tab:
                    st.subheader(f"{cat} Resources")
                    cat_df = resources_df[resources_df["category"] == cat]
                    st.dataframe(cat_df, use_container_width=True)
        else:
            st.info("No resources found in the video descriptions.")
else:
    st.info("Click the button above to run the scraping pipeline.")

# -------------------------
# Auto-launch Streamlit app if not already running under Streamlit
# -------------------------
if __name__ == "__main__":
    # Check if the app is not already being run by the Streamlit CLI
    if os.environ.get("STREAMLIT_RUN") is None:
        os.environ["STREAMLIT_RUN"] = "1"
        subprocess.run(["streamlit", "run", sys.argv[0]])
