from __future__ import annotations

import json
import re
from contextlib import asynccontextmanager
from functools import lru_cache
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from .config import get_settings
from .manhwa_repository import ManhwaRepository, get_manhwa_repository
from .repository import DuckDBVideoRepository, get_duckdb_store
from .schemas import (
    ManhwaChapterResponse,
    ManhwaDetailsResponse,
    ManhwaListResponse,
    VideoDetailsResponse,
    VideoListResponse,
)


@lru_cache
def get_repository() -> DuckDBVideoRepository:
    return DuckDBVideoRepository(get_duckdb_store())


@lru_cache
def get_series_repository() -> ManhwaRepository:
    return get_manhwa_repository()


@asynccontextmanager
async def lifespan(_: FastAPI):
    get_repository().ensure_ready()
    yield


app = FastAPI(
    title=get_settings().app_name,
    version="0.2.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health", tags=["System"])
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/jav/videos", response_model=VideoListResponse, tags=["JAV"])
def list_videos(
    limit: int = Query(default=18, ge=1, le=60),
    offset: int = Query(default=0, ge=0),
    q: str | None = Query(
        default=None,
        description="Filter JAV tiles by content ID, DVD ID, or title.",
    ),
) -> VideoListResponse:
    payload = get_repository().list_videos(limit=limit, offset=offset, query=q)
    return VideoListResponse.model_validate(payload)


@app.get("/api/jav/videos/{content_id}", response_model=VideoDetailsResponse, tags=["JAV"])
def get_video_details_by_content_id(content_id: str) -> VideoDetailsResponse:
    payload = get_repository().get_video_details(content_id=content_id)
    if payload is None:
        raise HTTPException(status_code=404, detail="Video not found.")
    return VideoDetailsResponse.model_validate(payload)


@app.get("/api/videos/details", response_model=VideoDetailsResponse, tags=["JAV"])
def get_video_details(
    content_id: str | None = Query(
        default=None,
        description="Lookup by content ID, for example hmn283.",
    ),
    dvd_id: str | None = Query(
        default=None,
        description="Lookup by DVD ID, for example HMN-283.",
    ),
) -> VideoDetailsResponse:
    try:
        payload = get_repository().get_video_details(content_id=content_id, dvd_id=dvd_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    if payload is None:
        raise HTTPException(status_code=404, detail="Video not found.")

    return VideoDetailsResponse.model_validate(payload)


@app.get("/api/manhwa", response_model=ManhwaListResponse, tags=["Manhwa"])
def list_manhwa_titles() -> ManhwaListResponse:
    payload = {"items": get_series_repository().list_titles()}
    return ManhwaListResponse.model_validate(payload)


@app.get("/api/manhwa/fetch/", tags=["DEBUG"])
async def fetch_manhwa(url: str):
    try:
        settings = get_settings()
        response = requests.get(url, timeout=30)
        response.raise_for_status()

        html_code = BeautifulSoup(response.text, "html.parser")
        parsed_html = html_code.prettify()
        output_html_path = settings.html_cache_dir / "output.html"
        with output_html_path.open("w", encoding="utf-8") as file:
            file.write(parsed_html)
        with output_html_path.open("r", encoding="utf-8") as file:
            html_content = file.read()

        soup = BeautifulSoup(html_content, "html.parser")
        metadata: dict[str, object] = {}

        title_tag = soup.find("h1")
        metadata["title"] = title_tag.get_text(strip=True) if title_tag else "N/A"

        poster_img = soup.find("img", {"class": "img-responsive", "fifu-featured": "1"})
        metadata["poster"] = (
            poster_img.get("src")
            if poster_img
            else poster_img.get("data-default-src")
            if poster_img
            else "N/A"
        )

        alternative_names = "N/A"
        for item in soup.find_all("div", {"class": "post-content_item"}):
            heading = item.find("h5")
            if heading and "Alternative" in heading.get_text():
                alternative_names = item.find("div", {"class": "summary-content"}).get_text(strip=True)
                break
        metadata["alternative_names"] = alternative_names

        authors: list[str] = []
        for item in soup.find_all("div", {"class": "post-content_item"}):
            heading = item.find("h5")
            if heading and "Author" in heading.get_text():
                authors = [link.get_text(strip=True) for link in item.find_all("a")]
                break
        metadata["authors"] = authors if authors else ["N/A"]

        artists: list[str] = []
        for item in soup.find_all("div", {"class": "post-content_item"}):
            heading = item.find("h5")
            if heading and "Artist" in heading.get_text():
                artists = [link.get_text(strip=True) for link in item.find_all("a")]
                break
        metadata["artists"] = artists if artists else ["N/A"]

        release_year = "N/A"
        for item in soup.find_all("div", {"class": "post-content_item"}):
            heading = item.find("h5")
            if heading and "Release" in heading.get_text():
                release_text = item.find("a")
                if release_text:
                    release_year = release_text.get_text(strip=True)
                break
        metadata["year_published"] = release_year

        status = "N/A"
        for item in soup.find_all("div", {"class": "post-content_item"}):
            heading = item.find("h5")
            if heading and "Status" in heading.get_text():
                status_div = item.find("div", {"class": "summary-content"})
                if status_div:
                    status = status_div.get_text(strip=True)
                break
        metadata["status"] = status

        publication_type = "N/A"
        for item in soup.find_all("div", {"class": "post-content_item"}):
            heading = item.find("h5")
            if heading and "Type" in heading.get_text():
                type_div = item.find("div", {"class": "summary-content"})
                if type_div:
                    publication_type = type_div.get_text(strip=True)
                break
        metadata["publication_type"] = publication_type

        genres: list[str] = []
        for item in soup.find_all("div", {"class": "post-content_item"}):
            heading = item.find("h5")
            if heading and "Genre" in heading.get_text():
                genres = [link.get_text(strip=True) for link in item.find_all("a")]
                break
        metadata["genres"] = genres if genres else ["N/A"]

        tags: list[str] = []
        for item in soup.find_all("div", {"class": "post-content_item"}):
            heading = item.find("h5")
            if heading and "Tag" in heading.get_text():
                tags = [link.get_text(strip=True) for link in item.find_all("a")]
                break
        metadata["tags"] = tags if tags else ["N/A"]

        summary = "N/A"
        description_div = soup.find("div", {"class": "description-summary"})
        if description_div:
            summary_text = description_div.find("div", {"class": "summary__content"})
            if summary_text:
                paragraphs = summary_text.find_all("p")
                summary = " ".join([paragraph.get_text(strip=True) for paragraph in paragraphs])
        metadata["description"] = summary

        rating = "N/A"
        rating_span = soup.find("span", {"id": "averagerate"})
        if rating_span:
            rating = rating_span.get_text(strip=True)
        metadata["rating"] = rating

        total_votes = "N/A"
        votes_span = soup.find("span", {"id": "countrate"})
        if votes_span:
            total_votes = votes_span.get_text(strip=True)
        metadata["total_ratings"] = total_votes

        chapters_list = []
        for link in soup.find_all("a", href=True):
            href = link.get("href")
            chapter_text = link.get_text(strip=True)
            if href and "/chapter-" in href and chapter_text.startswith("Chapter"):
                chapters_list.append({"title": chapter_text, "url": href})

        max_chapter = 0
        for chapter in chapters_list:
            try:
                chapter_num = int(chapter["title"].split("-")[0].replace("Chapter", "").strip())
                if chapter_num > max_chapter:
                    max_chapter = chapter_num
            except Exception:
                pass

        metadata["number_of_chapters"] = max_chapter if max_chapter > 0 else len(chapters_list)
        metadata["published_by"] = "Manga District"
        metadata["all_chapters"] = chapters_list

        manhwa_json = {
            "title": metadata.get("title"),
            "alternative_names": metadata.get("alternative_names"),
            "poster_url": metadata.get("poster"),
            "rating": metadata.get("rating"),
            "total_ratings": metadata.get("total_ratings"),
            "description": metadata.get("description"),
            "authors": metadata.get("authors"),
            "artists": metadata.get("artists"),
            "publication_type": metadata.get("publication_type"),
            "genres": metadata.get("genres"),
            "tags": metadata.get("tags"),
            "status": metadata.get("status"),
            "year_published": metadata.get("year_published"),
            "published_by": metadata.get("published_by"),
            "number_of_chapters": metadata.get("number_of_chapters"),
            "all_chapters": metadata.get("all_chapters"),
        }

        title_slug = urlparse(url).path.removeprefix("/series/")
        output_dir = settings.manhwa_dir / title_slug
        output_dir.mkdir(parents=True, exist_ok=True)

        with (output_dir / "manhwa_metadata.json").open("w", encoding="utf-8") as handle:
            json.dump(manhwa_json, handle, indent=2, ensure_ascii=False)

        return manhwa_json
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.get("/api/manhwa/chaptersDetails", tags=["DEBUG"])
async def fetch_chapters(url: str, slug: str,chapter_number: str):
    try:
        settings = get_settings()
        response = requests.get(url, timeout=30)
        response.raise_for_status()

        html_code = BeautifulSoup(response.text, "html.parser")
        parsed_html = html_code.prettify()
        chapter_output_path = settings.html_cache_dir / "ch_output.html"
        with chapter_output_path.open("w", encoding="utf-8") as file:
            file.write(parsed_html)
        with chapter_output_path.open("r", encoding="utf-8") as file:
            html_content = file.read()

        soup = BeautifulSoup(html_content, "html.parser")
        page_images = soup.find_all("img", class_="wp-manga-chapter-img")

       
        chapter_num = chapter_number

        page_urls = []
        for img in page_images:
            src = img.get("src", "").strip()
            if src:
                page_urls.append(src.replace("\n", "").replace(" ", ""))

        manhwa_json = {
            "number_of_pages": len(page_urls),
            "pages": page_urls,
            "slug": slug,
            "chapter_number": chapter_num,
        }

        output_dir = settings.manhwa_dir / slug / "chapters"
        output_dir.mkdir(parents=True, exist_ok=True)
        output_file = output_dir / f"chapter-{chapter_num}.json"
        with output_file.open("w", encoding="utf-8") as handle:
            json.dump(manhwa_json, handle, indent=2, ensure_ascii=False)

        return manhwa_json
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.get("/api/manhwa/{slug}", response_model=ManhwaDetailsResponse, tags=["Manhwa"])
def get_manhwa_details(slug: str) -> ManhwaDetailsResponse:
    payload = get_series_repository().get_title_details(slug)
    if payload is None:
        raise HTTPException(status_code=404, detail="Manhwa title not found.")
    return ManhwaDetailsResponse.model_validate(payload)


@app.get(
    "/api/manhwa/{slug}/chapters/{chapter_number}",
    response_model=ManhwaChapterResponse,
    tags=["Manhwa"],
)
async def get_manhwa_chapter(slug: str, chapter_number: int) -> ManhwaChapterResponse:
    # return f"{slug},, {chapter_number}"
    try:
        payload = get_series_repository().get_chapter_details(slug, chapter_number)
        if payload is None:
            print("payload is none")
            manhwaDetails = get_series_repository().get_title_details(slug)
            reverse_arr = (manhwaDetails["all_chapters"][::-1])
            if manhwaDetails is None:    
                raise HTTPException(status_code=404, detail="Manhwa title not found.")
            else:
                # print(reverse_arr[chapter_number - 1]["url"])
                await fetch_chapters(reverse_arr[chapter_number - 1]["url"], slug,chapter_number)
                payload = get_series_repository().get_chapter_details(slug, chapter_number)
                # print(payload)
                return ManhwaChapterResponse.model_validate(payload)
        return ManhwaChapterResponse.model_validate(payload)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
        
    # return ManhwaChapterResponse.model_validate(payload)
