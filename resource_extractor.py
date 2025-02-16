# resource_extractor.py
import re

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
    Returns one of: 'Twitter', 'Books', 'Wikipedia', 'Blogs', 'Youtube', or 'Common'.
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
