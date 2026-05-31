import re
import sys
from urllib.parse import quote, urljoin

import requests
from bs4 import BeautifulSoup




if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


def get_m3u8_links(dvd_id):
    BASE_URL = "https://javtrailers.com"
    dvd_id = dvd_id.strip().upper()
    search_url = f"{BASE_URL}/search/{quote(dvd_id)}"

    search_response = requests.get(search_url, timeout=30)
    search_response.raise_for_status()

    search_soup = BeautifulSoup(search_response.text, "html.parser")
    video_url = None

    for video_link in search_soup.select("a.video-link[href]"):
        if dvd_id in video_link.get_text(" ", strip=True).upper():
            video_url = urljoin(search_response.url, video_link["href"])
            break

    if not video_url:
        return []

    video_response = requests.get(video_url, timeout=30)
    video_response.raise_for_status()

    m3u8_links = []
    pattern = r'https?:\\?/\\?/[^"\'<>\s]+?\.m3u8[^"\'<>\s]*'

    for match in re.findall(pattern, video_response.text):
        clean_link = match.replace("\\/", "/")
        if clean_link not in m3u8_links:
            m3u8_links.append(clean_link)

    return m3u8_links

def get_video_urls(dvd_id):
    from urllib.parse import quote_plus, urljoin

    import requests
    from bs4 import BeautifulSoup

    base_url = "https://javseen.tv"
    search_url = f"{base_url}/search/video/?s={quote_plus(dvd_id)}"
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/125.0 Safari/537.36"
        )
    }

    response = requests.get(search_url, headers=headers, timeout=30)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    video_urls = []

    for link in soup.select("a.thumbnail[href]"):
        video_url = urljoin(base_url, link["href"])
        if video_url not in video_urls:
            video_urls.append(video_url)
        if len(video_urls) == 3:
            break

    return video_urls