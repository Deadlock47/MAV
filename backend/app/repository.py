from __future__ import annotations

import datetime as dt
from functools import lru_cache
import math
from pathlib import Path
import re
from typing import Any

import duckdb

from .config import get_settings
from .duckdb_store import DuckDBStore


@lru_cache
def get_duckdb_store() -> DuckDBStore:
    settings = get_settings()
    return DuckDBStore(settings.db_dir, settings.duckdb_path)


class DuckDBVideoRepository:
    DMM_PICS_BASE = "https://pics.dmm.co.jp/"
    GALLERY_INDEX_PATTERN = re.compile(r"^(?P<prefix>.+-)(?P<index>\d+)$")

    def __init__(self, store: DuckDBStore) -> None:
        self.store = store

    def ensure_ready(self) -> None:
        self.store.ensure_ready()

    def get_video_details(
        self,
        *,
        content_id: str | None = None,
        dvd_id: str | None = None,
    ) -> dict[str, Any] | None:
        if bool(content_id) == bool(dvd_id):
            raise ValueError("Provide exactly one of content_id or dvd_id.")

        lookup_value = (content_id or dvd_id or "").strip()
        if not lookup_value:
            raise ValueError("Lookup value cannot be empty.")

        con = self.store.connect(read_only=True)
        try:
            video = self._fetch_video_row(
                con,
                content_id=content_id.strip().lower() if content_id else None,
                dvd_id=dvd_id.strip().upper() if dvd_id else None,
            )
            if video is None:
                return None

            resolved_content_id = str(video["content_id"])
            trailer = self._fetch_trailer(con, resolved_content_id)
            title_en, title_en_is_machine_translation = self._resolve_english_text(
                con,
                existing_en=video.get("title_en"),
                source_ja=video.get("title_ja"),
            )
            maker = self._fetch_named_entity(con, "maker", video.get("maker_id"))
            label = self._fetch_named_entity(con, "label", video.get("label_id"))
            series = self._fetch_named_entity(con, "series", video.get("series_id"))
            series_name_en, series_name_en_is_machine_translation = self._resolve_english_text(
                con,
                existing_en=series.get("name_en") if series else None,
                source_ja=series.get("name_ja") if series else None,
            )

            return {
                "actors": self._fetch_actors(con, resolved_content_id),
                "actresses": self._fetch_actresses(con, resolved_content_id),
                "authors": self._fetch_authors(con, resolved_content_id),
                "categories": self._fetch_categories(con, resolved_content_id),
                "comment_en": video.get("comment_en"),
                "content_id": resolved_content_id,
                "directors": self._fetch_directors(con, resolved_content_id),
                "dvd_id": video.get("dvd_id"),
                "gallery": self._build_gallery(video),
                "histrions": self._fetch_histrions(con, resolved_content_id),
                "jacket_full_url": self._build_image_url(video.get("jacket_full_url")),
                "jacket_thumb_url": self._build_image_url(video.get("jacket_thumb_url")),
                "label_id": self._optional_int(video.get("label_id")),
                "label_name_en": label.get("name_en") if label else None,
                "label_name_ja": label.get("name_ja") if label else None,
                "maker_id": self._optional_int(video.get("maker_id")),
                "maker_name_en": maker.get("name_en") if maker else None,
                "maker_name_ja": maker.get("name_ja") if maker else None,
                "release_date": video.get("release_date"),
                "runtime_mins": self._optional_runtime(video.get("runtime_mins")),
                "sample_url": video.get("sample_url") or (trailer.get("url") if trailer else None),
                "series_id": self._optional_int(video.get("series_id")),
                "series_name_en": series_name_en,
                "series_name_en_is_machine_translation": series_name_en_is_machine_translation,
                "series_name_ja": series.get("name_ja") if series else None,
                "service_code": video.get("service_code"),
                "site_id": self._optional_int(video.get("site_id")),
                "title_en": title_en,
                "title_en_is_machine_translation": title_en_is_machine_translation,
                "title_en_uncensored": None,
                "title_ja": video.get("title_ja"),
            }
        finally:
            con.close()

    def list_videos(
        self,
        *,
        limit: int = 24,
        offset: int = 0,
        query: str | None = None,
    ) -> dict[str, Any]:
        limit = max(1, min(limit, 60))
        offset = max(0, offset)
        normalized_query = (query or "").strip()

        where_sql = ""
        params: list[Any] = []
        if normalized_query:
            like_query = f"%{normalized_query}%"
            prefix_query = f"{normalized_query}%"
            where_sql = """
                WHERE
                    LOWER(v.content_id) = LOWER(?)
                    OR UPPER(COALESCE(v.dvd_id, '')) = UPPER(?)
                    OR LOWER(v.content_id) LIKE LOWER(?)
                    OR UPPER(COALESCE(v.dvd_id, '')) LIKE UPPER(?)
                    OR COALESCE(v.title_en, '') ILIKE ?
                    OR COALESCE(v.title_ja, '') ILIKE ?
            """
            params.extend(
                [
                    normalized_query,
                    normalized_query,
                    prefix_query,
                    prefix_query,
                    like_query,
                    like_query,
                ]
            )

        con = self.store.connect(read_only=True)
        try:
            rows = self._fetch_all(
                con,
                f"""
                SELECT
                    v.content_id,
                    v.dvd_id,
                    COALESCE(v.title_en, v.title_ja, v.content_id) AS title,
                    v.title_en,
                    v.title_ja,
                    v.release_date,
                    v.sample_url,
                    v.jacket_thumb_url,
                    maker.name_en AS maker_name_en,
                    maker.name_ja AS maker_name_ja,
                    series.name_en AS series_name_en,
                    series.name_ja AS series_name_ja
                FROM {self._table('video')} AS v
                LEFT JOIN {self._table('maker')} AS maker
                    ON maker.id = v.maker_id
                LEFT JOIN {self._table('series')} AS series
                    ON series.id = v.series_id
                {where_sql}
                ORDER BY v.release_date DESC NULLS LAST, v.content_id
                LIMIT ?
                OFFSET ?
                """,
                [*params, limit + 1, offset],
            )
        finally:
            con.close()

        items = rows[:limit]
        for item in items:
            item["jacket_thumb_url"] = self._build_image_url(item.get("jacket_thumb_url"))

        return {
            "has_more": len(rows) > limit,
            "items": items,
            "limit": limit,
            "offset": offset,
            "query": normalized_query or None,
        }

    def _fetch_video_row(
        self,
        con: duckdb.DuckDBPyConnection,
        *,
        content_id: str | None,
        dvd_id: str | None,
    ) -> dict[str, Any] | None:
        table = self._table("video")

        if content_id is not None:
            return self._fetch_one(
                con,
                f"""
                SELECT *
                FROM {table}
                WHERE content_id = ?
                LIMIT 1
                """,
                [content_id],
            )

        if dvd_id is not None:
            return self._fetch_one(
                con,
                f"""
                SELECT *
                FROM {table}
                WHERE dvd_id = ?
                LIMIT 1
                """,
                [dvd_id],
            )

        return None

    def _fetch_named_entity(
        self,
        con: duckdb.DuckDBPyConnection,
        table_key: str,
        entity_id: Any,
    ) -> dict[str, Any] | None:
        entity_id = self._optional_int(entity_id)
        if entity_id is None:
            return None

        return self._fetch_one(
            con,
            f"""
            SELECT CAST(id AS BIGINT) AS id, name_en, name_ja
            FROM {self._table(table_key)}
            WHERE id = ?
            LIMIT 1
            """,
            [entity_id],
        )

    def _fetch_site(
        self,
        con: duckdb.DuckDBPyConnection,
        site_id: Any,
    ) -> dict[str, Any] | None:
        site_id = self._optional_int(site_id)
        if site_id is None:
            return None

        return self._fetch_one(
            con,
            f"""
            SELECT CAST(id AS BIGINT) AS id, name
            FROM {self._table('site')}
            WHERE id = ?
            LIMIT 1
            """,
            [site_id],
        )

    def _fetch_trailer(
        self,
        con: duckdb.DuckDBPyConnection,
        content_id: str,
    ) -> dict[str, Any] | None:
        return self._fetch_one(
            con,
            f"""
            SELECT url, timestamp
            FROM {self._table('trailer')}
            WHERE content_id = ? AND url IS NOT NULL
            ORDER BY timestamp DESC NULLS LAST
            LIMIT 1
            """,
            [content_id],
        )

    def _fetch_actresses(
        self,
        con: duckdb.DuckDBPyConnection,
        content_id: str,
    ) -> list[dict[str, Any]]:
        return self._fetch_all(
            con,
            f"""
            SELECT DISTINCT
                CAST(va.actress_id AS BIGINT) AS id,
                a.name_romaji,
                a.name_kanji,
                a.name_kana,
                a.image_url
            FROM {self._table('video_actress')} AS va
            LEFT JOIN {self._table('actress')} AS a
                ON a.id = va.actress_id
            WHERE va.content_id = ?
            ORDER BY ordinality NULLS LAST, id
            """,
            [content_id],
        )

    def _fetch_actors(
        self,
        con: duckdb.DuckDBPyConnection,
        content_id: str,
    ) -> list[dict[str, Any]]:
        return self._fetch_all(
            con,
            f"""
            SELECT DISTINCT
                CAST(va.actor_id AS BIGINT) AS id,
                NULL AS name_romaji,
                a.name_kanji,
                a.name_kana,
                NULL AS image_url
            FROM {self._table('video_actor')} AS va
            LEFT JOIN {self._table('actor')} AS a
                ON a.id = va.actor_id
            WHERE va.content_id = ?
            ORDER BY ordinality NULLS LAST, id
            """,
            [content_id],
        )

    def _fetch_directors(
        self,
        con: duckdb.DuckDBPyConnection,
        content_id: str,
    ) -> list[dict[str, Any]]:
        return self._fetch_all(
            con,
            f"""
            SELECT DISTINCT
                CAST(vd.director_id AS BIGINT) AS id,
                d.name_romaji,
                d.name_kanji,
                d.name_kana
            FROM {self._table('video_director')} AS vd
            LEFT JOIN {self._table('director')} AS d
                ON d.id = vd.director_id
            WHERE vd.content_id = ?
            ORDER BY id
            """,
            [content_id],
        )

    def _fetch_authors(
        self,
        con: duckdb.DuckDBPyConnection,
        content_id: str,
    ) -> list[dict[str, Any]]:
        return self._fetch_all(
            con,
            f"""
            SELECT DISTINCT
                CAST(va.author_id AS BIGINT) AS id,
                NULL AS name_romaji,
                a.name_kanji,
                a.name_kana
            FROM {self._table('video_author')} AS va
            LEFT JOIN {self._table('author')} AS a
                ON a.id = va.author_id
            WHERE va.content_id = ?
            ORDER BY id
            """,
            [content_id],
        )

    def _fetch_categories(
        self,
        con: duckdb.DuckDBPyConnection,
        content_id: str,
    ) -> list[dict[str, Any]]:
        categories = self._fetch_all(
            con,
            f"""
            SELECT DISTINCT
                CAST(vc.category_id AS BIGINT) AS id,
                c.name_en,
                c.name_ja
            FROM {self._table('video_category')} AS vc
            LEFT JOIN {self._table('category')} AS c
                ON c.id = vc.category_id
            WHERE vc.content_id = ?
            ORDER BY id
            """,
            [content_id],
        )
        for category in categories:
            name_en, is_machine_translation = self._resolve_english_text(
                con,
                existing_en=category.get("name_en"),
                source_ja=category.get("name_ja"),
            )
            category["name_en"] = name_en
            category["name_en_is_machine_translation"] = is_machine_translation
        return categories

    def _fetch_histrions(
        self,
        con: duckdb.DuckDBPyConnection,
        content_id: str,
    ) -> list[dict[str, Any]]:
        return self._fetch_all(
            con,
            f"""
            SELECT DISTINCT
                CAST(h.id AS BIGINT) AS id,
                h.name_kanji,
                h.name_kanji_only,
                h.name_kana
            FROM {self._table('video_histrion')} AS vh
            LEFT JOIN {self._table('histrion')} AS h
                ON h.id = vh.histrion_id
            WHERE vh.content_id = ?
            ORDER BY id
            """,
            [content_id],
        )

    def _fetch_one(
        self,
        con: duckdb.DuckDBPyConnection,
        sql: str,
        params: list[Any],
    ) -> dict[str, Any] | None:
        cursor = con.execute(sql, params)
        row = cursor.fetchone()
        if row is None:
            return None

        columns = [column[0] for column in cursor.description]
        return self._normalize_row(dict(zip(columns, row)))

    def _fetch_all(
        self,
        con: duckdb.DuckDBPyConnection,
        sql: str,
        params: list[Any],
    ) -> list[dict[str, Any]]:
        cursor = con.execute(sql, params)
        rows = cursor.fetchall()
        columns = [column[0] for column in cursor.description]
        return [
            self._normalize_row(dict(zip(columns, row)))
            for row in rows
        ]

    def _normalize_row(self, row: dict[str, Any]) -> dict[str, Any]:
        return {key: self._normalize_value(value) for key, value in row.items()}

    def _normalize_value(self, value: Any) -> Any:
        if value is None:
            return None
        if isinstance(value, float) and math.isnan(value):
            return None
        if isinstance(value, (dt.datetime, dt.date)):
            return value.isoformat()
        return value

    def _optional_float(self, value: Any) -> float | None:
        if value is None:
            return None
        if isinstance(value, float) and math.isnan(value):
            return None
        return float(value)

    def _optional_runtime(self, value: Any) -> int | float | None:
        runtime = self._optional_float(value)
        if runtime is None:
            return None
        if runtime.is_integer():
            return int(runtime)
        return runtime

    def _optional_int(self, value: Any) -> int | None:
        if value is None:
            return None
        if isinstance(value, float) and math.isnan(value):
            return None
        return int(value)

    def _resolve_english_text(
        self,
        con: duckdb.DuckDBPyConnection,
        *,
        existing_en: str | None,
        source_ja: str | None,
    ) -> tuple[str | None, bool]:
        if existing_en:
            return existing_en, False
        if not source_ja:
            return None, False

        translated = self._fetch_translation(con, source_ja)
        if translated:
            return translated, True
        return None, False

    def _fetch_translation(
        self,
        con: duckdb.DuckDBPyConnection,
        source_ja: str,
    ) -> str | None:
        row = self._fetch_one(
            con,
            f"""
            SELECT target_en
            FROM {self._table('machine_translation')}
            WHERE source_ja = ?
            ORDER BY timestamp DESC NULLS LAST
            LIMIT 1
            """,
            [source_ja],
        )
        if row is None:
            return None
        return row.get("target_en")

    def _build_image_url(self, path: str | None) -> str | None:
        if not path:
            return None
        if path.startswith("http://") or path.startswith("https://"):
            return path
        if "." not in Path(path).name:
            path = f"{path}.jpg"
        return f"{self.DMM_PICS_BASE}{path}"

    def _build_gallery(self, video: dict[str, Any]) -> list[dict[str, Any]]:
        full_items = self._expand_gallery_paths(
            video.get("gallery_full_first"),
            video.get("gallery_full_last"),
        )
        thumb_items = self._expand_gallery_paths(
            video.get("gallery_thumb_first"),
            video.get("gallery_thumb_last"),
        )
        total = max(len(full_items), len(thumb_items))
        gallery: list[dict[str, Any]] = []

        for index in range(total):
            full_path = full_items[index] if index < len(full_items) else None
            thumb_path = thumb_items[index] if index < len(thumb_items) else None
            gallery.append(
                {
                    "image_full": self._build_full_gallery_url(full_path or thumb_path),
                    "image_thumb": self._build_image_url(thumb_path or full_path),
                }
            )
        return gallery

    def _build_full_gallery_url(self, path: str | None) -> str | None:
        if not path:
            return None
        normalized_path = self._normalize_full_gallery_path(path)
        return self._build_image_url(normalized_path)

    def _normalize_full_gallery_path(self, path: str) -> str:
        if path.startswith("http://") or path.startswith("https://"):
            return path

        image_path = path[:-4] if path.lower().endswith(".jpg") else path
        if "jp-" in Path(image_path).name:
            return path

        match = self.GALLERY_INDEX_PATTERN.match(image_path)
        if not match:
            return path

        prefix = match.group("prefix")
        index = match.group("index")
        return f"{prefix[:-1]}jp-{index}"

    def _expand_gallery_paths(
        self,
        first_path: str | None,
        last_path: str | None,
    ) -> list[str]:
        if not first_path:
            return []
        if not last_path or last_path == first_path:
            return [first_path]

        first_match = self.GALLERY_INDEX_PATTERN.match(first_path)
        last_match = self.GALLERY_INDEX_PATTERN.match(last_path)
        if not first_match or not last_match:
            return [first_path, last_path]

        first_prefix = first_match.group("prefix")
        last_prefix = last_match.group("prefix")
        if first_prefix != last_prefix:
            return [first_path, last_path]

        start_index = int(first_match.group("index"))
        end_index = int(last_match.group("index"))
        if end_index < start_index:
            return [first_path]

        return [f"{first_prefix}{index}" for index in range(start_index, end_index + 1)]

    def _table(self, table_key: str) -> str:
        return self.store.table(table_key)
