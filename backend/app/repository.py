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
        tags: list[str] | None = None,
        actress: list[str] | None = None,
        studio: str | None = None,
        release_date: date | None = None,
        dvd_only: bool = False,
    ) -> dict[str, Any]:
        limit = max(1, min(limit, 500))
        offset = max(0, offset)
        normalized_query = (query or "").strip()
        normalized_tags = [tag.strip() for tag in (tags or []) if tag.strip()]
        normalized_actress = [name.strip() for name in (actress or []) if name.strip()]
        normalized_studio = (studio or "").strip()
        normalized_release_date = release_date

        params: list[Any] = []
        joins: list[str] = []
        where_clauses: list[str] = []

        if normalized_query:
            like_query = f"%{normalized_query}%"
            prefix_query = f"{normalized_query}%"
            where_clauses.append(
                "(" + " OR ".join([
                    "LOWER(v.content_id) = LOWER(?)",
                    "UPPER(COALESCE(v.dvd_id, '')) = UPPER(?)",
                    "LOWER(v.content_id) LIKE LOWER(?)",
                    "UPPER(COALESCE(v.dvd_id, '')) LIKE UPPER(?)",
                    "COALESCE(v.title_en, '') ILIKE ?",
                    "COALESCE(v.title_ja, '') ILIKE ?",
                ]) + ")"
            )
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

        if normalized_tags:
            joins.append(
                f"LEFT JOIN {self._table('video_category')} AS vc ON vc.content_id = v.content_id"
            )
            joins.append(
                f"LEFT JOIN {self._table('category')} AS c ON c.id = vc.category_id"
            )
            tag_conditions: list[str] = []
            for tag in normalized_tags:
                tag_conditions.append(
                    "(" + " OR ".join([
                        "COALESCE(c.name_en, '') ILIKE ?",
                        "COALESCE(c.name_ja, '') ILIKE ?",
                    ]) + ")"
                )
                params.extend([f"%{tag}%", f"%{tag}%"])
            where_clauses.append("(" + " OR ".join(tag_conditions) + ")")

        if normalized_actress:
            joins.append(
                f"LEFT JOIN {self._table('video_actress')} AS va ON va.content_id = v.content_id"
            )
            joins.append(
                f"LEFT JOIN {self._table('actress')} AS a ON a.id = va.actress_id"
            )
            actress_conditions: list[str] = []
            for name in normalized_actress:
                actress_conditions.append(
                    "(" + " OR ".join([
                        "COALESCE(a.name_romaji, '') ILIKE ?",
                        "COALESCE(a.name_kanji, '') ILIKE ?",
                        "COALESCE(a.name_kana, '') ILIKE ?",
                    ]) + ")"
                )
                params.extend([f"%{name}%", f"%{name}%", f"%{name}%"])
            where_clauses.append("(" + " OR ".join(actress_conditions) + ")")

        if normalized_studio:
            joins.append(
                f"LEFT JOIN {self._table('label')} AS label ON label.id = v.label_id"
            )
            studio_like = f"%{normalized_studio}%"
            where_clauses.append(
                "(" + " OR ".join([
                    "COALESCE(maker.name_en, '') ILIKE ?",
                    "COALESCE(maker.name_ja, '') ILIKE ?",
                    "COALESCE(label.name_en, '') ILIKE ?",
                    "COALESCE(label.name_ja, '') ILIKE ?",
                ]) + ")"
            )
            params.extend([studio_like, studio_like, studio_like, studio_like])

        if normalized_release_date is not None:
            where_clauses.append("CAST(v.release_date AS DATE) < ?")
            params.append(normalized_release_date.isoformat())

        if dvd_only:
            where_clauses.append("v.dvd_id IS NOT NULL")

        where_sql = ""
        if where_clauses:
            where_sql = "WHERE " + " AND ".join(where_clauses)

        join_sql = "\n".join(joins)
        con = self.store.connect(read_only=True)
        try:
            rows = self._fetch_all(
                con,
                f"""
                SELECT DISTINCT
                    v.content_id,
                    v.dvd_id,
                    COALESCE(v.title_en, v.title_ja, v.content_id) AS title,
                    v.title_en,
                    v.title_ja,
                    v.release_date,
                    v.sample_url,
                    v.jacket_full_url,
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
                {join_sql}
                {where_sql}
                ORDER BY v.release_date DESC NULLS LAST, v.content_id
                LIMIT ?
                OFFSET ?
                """,
                [*params, limit + 1, offset],
            )

            items = rows[:limit]
            for item in items:
                item["jacket_full_url"] = self._build_image_url(item.get("jacket_full_url"))
                item["jacket_thumb_url"] = self._build_image_url(item.get("jacket_thumb_url"))
                if item.get("title_en") is None and item.get("title_ja"):
                    title_en, _ = self._resolve_english_text(
                        con,
                        existing_en=None,
                        source_ja=item.get("title_ja"),
                    )
                    item["title_en"] = title_en
        finally:
            con.close()

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
        actresses = self._fetch_all(
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
        for actress in actresses:
            if not actress.get("name_romaji") and actress.get("name_kanji"):
                name_romaji, _ = self._resolve_english_text(
                    con,
                    existing_en=None,
                    source_ja=actress.get("name_kanji"),
                )
                if not name_romaji:
                    name_romaji = self._transliterate_kana_to_romaji(actress.get("name_kanji"))
                actress["name_romaji"] = name_romaji
        return actresses

    def _fetch_actors(
        self,
        con: duckdb.DuckDBPyConnection,
        content_id: str,
    ) -> list[dict[str, Any]]:
        actors = self._fetch_all(
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
        for actor in actors:
            if not actor.get("name_romaji") and actor.get("name_kana"):
                name_romaji, _ = self._resolve_english_text(
                    con,
                    existing_en=None,
                    source_ja=actor.get("name_kana"),
                )
                if not name_romaji:
                    name_romaji = self._transliterate_kana_to_romaji(actor.get("name_kana"))
                actor["name_romaji"] = name_romaji
        return actors

    def _fetch_directors(
        self,
        con: duckdb.DuckDBPyConnection,
        content_id: str,
    ) -> list[dict[str, Any]]:
        directors = self._fetch_all(
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
        for director in directors:
            if not director.get("name_romaji") and director.get("name_kana"):
                name_romaji, _ = self._resolve_english_text(
                    con,
                    existing_en=None,
                    source_ja=director.get("name_kana"),
                )
                if not name_romaji:
                    name_romaji = self._transliterate_kana_to_romaji(director.get("name_kana"))
                director["name_romaji"] = name_romaji
        return directors

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

    def _transliterate_kana_to_romaji(self, text: str) -> str | None:
        if not text:
            return None

        def normalize_katakana(s: str) -> str:
            normalized = []
            for ch in s:
                if "ァ" <= ch <= "ン":
                    normalized.append(chr(ord(ch) - 0x60))
                else:
                    normalized.append(ch)
            return "".join(normalized)

        kana = normalize_katakana(text.strip())

        kana_map = {
            "あ": "a", "い": "i", "う": "u", "え": "e", "お": "o",
            "か": "ka", "き": "ki", "く": "ku", "け": "ke", "こ": "ko",
            "さ": "sa", "し": "shi", "す": "su", "せ": "se", "そ": "so",
            "た": "ta", "ち": "chi", "つ": "tsu", "て": "te", "と": "to",
            "な": "na", "に": "ni", "ぬ": "nu", "ね": "ne", "の": "no",
            "は": "ha", "ひ": "hi", "ふ": "fu", "へ": "he", "ほ": "ho",
            "ま": "ma", "み": "mi", "む": "mu", "め": "me", "も": "mo",
            "や": "ya", "ゆ": "yu", "よ": "yo",
            "ら": "ra", "り": "ri", "る": "ru", "れ": "re", "ろ": "ro",
            "わ": "wa", "を": "wo", "ん": "n",
            "が": "ga", "ぎ": "gi", "ぐ": "gu", "げ": "ge", "ご": "go",
            "ざ": "za", "じ": "ji", "ず": "zu", "ぜ": "ze", "ぞ": "zo",
            "だ": "da", "ぢ": "ji", "づ": "zu", "で": "de", "ど": "do",
            "ば": "ba", "び": "bi", "ぶ": "bu", "べ": "be", "ぼ": "bo",
            "ぱ": "pa", "ぴ": "pi", "ぷ": "pu", "ぺ": "pe", "ぽ": "po",
            "きゃ": "kya", "きゅ": "kyu", "きょ": "kyo",
            "しゃ": "sha", "しゅ": "shu", "しょ": "sho",
            "ちゃ": "cha", "ちゅ": "chu", "ちょ": "cho",
            "にゃ": "nya", "にゅ": "nyu", "にょ": "nyo",
            "ひゃ": "hya", "ひゅ": "hyu", "ひょ": "hyo",
            "みゃ": "mya", "みゅ": "myu", "みょ": "myo",
            "りゃ": "rya", "りゅ": "ryu", "りょ": "ryo",
            "ぎゃ": "gya", "ぎゅ": "gyu", "ぎょ": "gyo",
            "じゃ": "ja", "じゅ": "ju", "じょ": "jo",
            "ぢゃ": "ja", "ぢゅ": "ju", "ぢょ": "jo",
            "びゃ": "bya", "びゅ": "byu", "びょ": "byo",
            "ぴゃ": "pya", "ぴゅ": "pyu", "ぴょ": "pyo",
            "ふぁ": "fa", "ふぃ": "fi", "ふぇ": "fe", "ふぉ": "fo",
            "ゔぁ": "va", "ゔぃ": "vi", "ゔ": "vu", "ゔぇ": "ve", "ゔぉ": "vo",
            "っ": "",
            "ー": "-",
            "。": ".", "、": ",", "・": " ", "「": "", "」": "", "『": "", "』": "",
        }

        # Add katakana sequence mappings too.
        for key, value in list(kana_map.items()):
            if all("ぁ" <= ch <= "ゖ" for ch in key):
                katakana_key = "".join(chr(ord(ch) + 0x60) for ch in key)
                kana_map[katakana_key] = value

        def last_vowel(romaji: str) -> str:
            for ch in reversed(romaji):
                if ch in "aeiou":
                    return ch
            return ""

        result: list[str] = []
        i = 0
        while i < len(kana):
            if kana[i] == "っ" and i + 1 < len(kana):
                next_seq = kana[i + 1:i + 3]
                if next_seq in kana_map:
                    consonant = kana_map[next_seq][0]
                else:
                    next_seq = kana[i + 1]
                    consonant = kana_map.get(next_seq, "")[0] if kana_map.get(next_seq) else ""
                if consonant:
                    result.append(consonant)
                i += 1
                continue

            pair = kana[i:i + 2]
            if pair in kana_map:
                romaji = kana_map[pair]
                if romaji == "-" and result:
                    result.append(last_vowel(result[-1]))
                else:
                    result.append(romaji)
                i += 2
                continue

            single = kana[i]
            romaji = kana_map.get(single)
            if romaji == "-" and result:
                result.append(last_vowel(result[-1]))
            elif romaji is not None:
                result.append(romaji)
            else:
                result.append(single)
            i += 1

        romaji_text = "".join(result)
        return romaji_text.replace("nn", "n")

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
