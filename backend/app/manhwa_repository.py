from __future__ import annotations

import json
import re
from functools import lru_cache
from pathlib import Path
from typing import Any

from .config import get_settings


CHAPTER_FILE_PATTERN = re.compile(r"chapter-(?P<number>\d+)\.json$", re.IGNORECASE)
CHAPTER_TITLE_PATTERN = re.compile(r"Chapter\s+(?P<number>\d+)", re.IGNORECASE)


@lru_cache
def get_manhwa_repository() -> "ManhwaRepository":
    return ManhwaRepository(get_settings().manhwa_dir)


class ManhwaRepository:
    def __init__(self, root_dir: Path) -> None:
        self.root_dir = root_dir

    def list_titles(self) -> list[dict[str, Any]]:
        items: list[dict[str, Any]] = []
        if not self.root_dir.exists():
            return items

        for series_dir in sorted(path for path in self.root_dir.iterdir() if path.is_dir()):
            metadata = self._read_json(series_dir / "manhwa_metadata.json")
            if metadata is None:
                continue

            cached_chapters = self._list_cached_chapters(series_dir, metadata)
            all_chapters = metadata.get("all_chapters") or []
            items.append(
                {
                    "downloaded_chapters": len(cached_chapters),
                    "genres": metadata.get("genres") or [],
                    "latest_chapter_title": all_chapters[0]["title"] if all_chapters else None,
                    "number_of_chapters": metadata.get("number_of_chapters") or len(all_chapters),
                    "poster_url": metadata.get("poster_url"),
                    "rating": metadata.get("rating"),
                    "slug": series_dir.name,
                    "status": metadata.get("status"),
                    "title": metadata.get("title") or self._humanize_slug(series_dir.name),
                    "year_published": metadata.get("year_published"),
                }
            )

        items.sort(key=lambda item: (-item["number_of_chapters"], item["title"].lower()))
        return items

    def get_title_details(self, slug: str) -> dict[str, Any] | None:
        series_dir = self.root_dir / slug
        metadata = self._read_json(series_dir / "manhwa_metadata.json")
        if metadata is None:
            return None

        cached_chapters = self._list_cached_chapters(series_dir, metadata)
        all_chapters = [
            {
                "chapter_number": self._extract_chapter_number(chapter.get("title"), chapter.get("url")),
                "title": chapter.get("title", "Untitled chapter"),
                "url": chapter.get("url", ""),
            }
            for chapter in metadata.get("all_chapters") or []
        ]

        return {
            "all_chapters": all_chapters,
            "alternative_names": metadata.get("alternative_names"),
            "artists": metadata.get("artists") or [],
            "authors": metadata.get("authors") or [],
            "description": metadata.get("description"),
            "downloaded_chapter_count": len(cached_chapters),
            "downloaded_chapters": cached_chapters,
            "genres": metadata.get("genres") or [],
            "number_of_chapters": metadata.get("number_of_chapters") or len(all_chapters),
            "poster_url": metadata.get("poster_url"),
            "publication_type": metadata.get("publication_type"),
            "published_by": metadata.get("published_by"),
            "rating": metadata.get("rating"),
            "slug": slug,
            "status": metadata.get("status"),
            "tags": metadata.get("tags") or [],
            "title": metadata.get("title") or self._humanize_slug(slug),
            "total_ratings": metadata.get("total_ratings"),
            "year_published": metadata.get("year_published"),
        }

    def get_chapter_details(self, slug: str, chapter_number: int) -> dict[str, Any] | None:
        details = self.get_title_details(slug)
        if details is None:
            return None

        chapter_path = self.root_dir / slug / "chapters" / f"chapter-{chapter_number}.json"
        chapter_data = self._read_json(chapter_path)
        if chapter_data is None:
            return None

        chapter_title = None
        for chapter in details["all_chapters"]:
            if chapter.get("chapter_number") == chapter_number:
                chapter_title = chapter.get("title")
                break

        return {
            "chapter_number": chapter_number,
            "chapter_title": chapter_title,
            "number_of_pages": chapter_data.get("number_of_pages") or len(chapter_data.get("pages") or []),
            "pages": chapter_data.get("pages") or [],
            "series_slug": slug,
            "series_title": details["title"],
        }

    def _list_cached_chapters(self, series_dir: Path, metadata: dict[str, Any]) -> list[dict[str, Any]]:
        chapters_dir = series_dir / "chapters"
        if not chapters_dir.exists():
            return []

        title_lookup = {
            chapter["chapter_number"]: chapter["title"]
            for chapter in [
                {
                    "chapter_number": self._extract_chapter_number(item.get("title"), item.get("url")),
                    "title": item.get("title", "Untitled chapter"),
                }
                for item in metadata.get("all_chapters") or []
            ]
            if chapter["chapter_number"] is not None
        }

        cached: list[dict[str, Any]] = []
        for chapter_file in sorted(chapters_dir.glob("chapter-*.json"), reverse=True):
            match = CHAPTER_FILE_PATTERN.match(chapter_file.name)
            if not match:
                continue

            chapter_number = int(match.group("number"))
            chapter_data = self._read_json(chapter_file) or {}
            cached.append(
                {
                    "chapter_number": chapter_number,
                    "number_of_pages": chapter_data.get("number_of_pages") or len(chapter_data.get("pages") or []),
                    "title": title_lookup.get(chapter_number),
                }
            )

        cached.sort(key=lambda chapter: chapter["chapter_number"], reverse=True)
        return cached

    def _extract_chapter_number(self, title: str | None, url: str | None) -> int | None:
        for value, pattern in (
            (title, CHAPTER_TITLE_PATTERN),
            (url, re.compile(r"chapter-(?P<number>\d+)", re.IGNORECASE)),
        ):
            if not value:
                continue
            match = pattern.search(value)
            if match:
                return int(match.group("number"))
        return None

    def _humanize_slug(self, slug: str) -> str:
        return slug.replace("-", " ").replace("_", " ").title()

    def _read_json(self, path: Path) -> dict[str, Any] | None:
        if not path.exists():
            return None
        with path.open("r", encoding="utf-8") as handle:
            return json.load(handle)
