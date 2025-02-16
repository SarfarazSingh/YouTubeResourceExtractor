# youtube_api.py
import requests
import urllib.parse
import streamlit as st

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

def get_channel_id_from_video(video_url, api_key):
    """
    Extracts the video ID from a YouTube URL and returns the channel ID 
    associated with that video by calling the YouTube Data API.
    """
    parsed_url = urllib.parse.urlparse(video_url)
    query_params = urllib.parse.parse_qs(parsed_url.query)
    video_id = None
    if "v" in query_params:
        video_id = query_params["v"][0]
    else:
        # Handle shortened URLs (e.g., youtu.be)
        if parsed_url.netloc in ["youtu.be"]:
            video_id = parsed_url.path.lstrip("/")
    if not video_id:
        return None
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
        return items[0]["snippet"].get("channelId")
    return None
