# main.py
import streamlit as st
import subprocess
import sys
import os
from pipeline import run_pipeline
from youtube_api import get_channel_id_from_video

# Set Streamlit page configuration
st.set_page_config(page_title="YouTube Channel Data Viewer", layout="wide")
st.title("YouTube Channel Data Viewer")
st.write("Enter the URL of a YouTube video from your favorite podcast channel to extract all its recommendations.")

# Your YouTube Data API key (can also be moved to a config file)
API_KEY = "AIzaSyBgXqdHjowUANqtW6XRSJkzf7kbPD9ur5o"

# Text input for the YouTube video URL
video_url = st.text_input("Enter a YouTube video URL:")

if st.button("Run Scraping Pipeline") and video_url:
    st.info("Extracting channel ID from video URL...")
    channel_id = get_channel_id_from_video(video_url, API_KEY)
    if not channel_id:
        st.error("Unable to extract channel ID. Please check the URL and try again.")
    else:
        st.success(f"Channel ID extracted: {channel_id}")
        with st.spinner("Fetching and processing data..."):
            videos_df, resources_df = run_pipeline(API_KEY, channel_id)
        if videos_df is not None:
            st.success(f"Found {len(videos_df)} videos!")
            # Display video links
            st.subheader("Video Links")
            st.dataframe(videos_df, use_container_width=True)
            # Display categorized resources in separate tabs if available
            if not resources_df.empty:
                st.success(f"Extracted {len(resources_df)} resources.")
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
    st.info("Please enter a YouTube video URL and click the button to run the pipeline.")

# Auto-launch Streamlit app if not already running under Streamlit
if __name__ == "__main__":
    if os.environ.get("STREAMLIT_RUN") is None:
        os.environ["STREAMLIT_RUN"] = "1"
        subprocess.run(["streamlit", "run", sys.argv[0]])
