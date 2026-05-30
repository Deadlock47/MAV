from __future__ import annotations

from pydantic import BaseModel, Field


class CastMember(BaseModel):
    id: int
    image_url: str | None = None
    name_kana: str | None = None
    name_kanji: str | None = None
    name_romaji: str | None = None


class CrewMember(BaseModel):
    id: int
    name_kana: str | None = None
    name_kanji: str | None = None
    name_romaji: str | None = None


class CategoryInfo(BaseModel):
    id: int
    name_en: str | None = None
    name_en_is_machine_translation: bool = False
    name_ja: str | None = None


class GalleryImage(BaseModel):
    image_full: str | None = None
    image_thumb: str | None = None


class HistrionInfo(BaseModel):
    id: int
    name_kana: str | None = None
    name_kanji: str | None = None
    name_kanji_only: str | None = None


class VideoTileResponse(BaseModel):
    content_id: str
    dvd_id: str | None = None
    jacket_thumb_url: str | None = None
    maker_name_en: str | None = None
    maker_name_ja: str | None = None
    release_date: str | None = None
    sample_url: str | None = None
    series_name_en: str | None = None
    series_name_ja: str | None = None
    title: str
    title_en: str | None = None
    title_ja: str | None = None


class VideoListResponse(BaseModel):
    has_more: bool = False
    items: list[VideoTileResponse] = Field(default_factory=list)
    limit: int
    offset: int
    query: str | None = None


class VideoDetailsResponse(BaseModel):
    actors: list[CastMember] = Field(default_factory=list)
    actresses: list[CastMember] = Field(default_factory=list)
    authors: list[CrewMember] = Field(default_factory=list)
    categories: list[CategoryInfo] = Field(default_factory=list)
    comment_en: str | None = None
    content_id: str
    directors: list[CrewMember] = Field(default_factory=list)
    dvd_id: str | None = None
    gallery: list[GalleryImage] = Field(default_factory=list)
    histrions: list[HistrionInfo] = Field(default_factory=list)
    jacket_full_url: str | None = None
    jacket_thumb_url: str | None = None
    label_id: int | None = None
    label_name_en: str | None = None
    label_name_ja: str | None = None
    maker_id: int | None = None
    maker_name_en: str | None = None
    maker_name_ja: str | None = None
    release_date: str | None = None
    runtime_mins: int | float | None = None
    sample_url: str | None = None
    series_id: int | None = None
    series_name_en: str | None = None
    series_name_en_is_machine_translation: bool = False
    series_name_ja: str | None = None
    service_code: str | None = None
    site_id: int | None = None
    title_en: str | None = None
    title_en_is_machine_translation: bool = False
    title_en_uncensored: str | None = None
    title_ja: str | None = None


class ManhwaChapterLink(BaseModel):
    chapter_number: int | None = None
    title: str
    url: str


class ManhwaCachedChapterResponse(BaseModel):
    chapter_number: int
    number_of_pages: int = 0
    title: str | None = None


class ManhwaListItemResponse(BaseModel):
    downloaded_chapters: int = 0
    genres: list[str] = Field(default_factory=list)
    latest_chapter_title: str | None = None
    number_of_chapters: int = 0
    poster_url: str | None = None
    rating: str | None = None
    slug: str
    status: str | None = None
    title: str
    year_published: str | None = None


class ManhwaListResponse(BaseModel):
    items: list[ManhwaListItemResponse] = Field(default_factory=list)


class ManhwaDetailsResponse(BaseModel):
    all_chapters: list[ManhwaChapterLink] = Field(default_factory=list)
    alternative_names: str | None = None
    artists: list[str] = Field(default_factory=list)
    authors: list[str] = Field(default_factory=list)
    description: str | None = None
    downloaded_chapter_count: int = 0
    downloaded_chapters: list[ManhwaCachedChapterResponse] = Field(default_factory=list)
    genres: list[str] = Field(default_factory=list)
    number_of_chapters: int = 0
    poster_url: str | None = None
    publication_type: str | None = None
    published_by: str | None = None
    rating: str | None = None
    slug: str
    status: str | None = None
    tags: list[str] = Field(default_factory=list)
    title: str
    total_ratings: str | None = None
    year_published: str | None = None


class ManhwaChapterResponse(BaseModel):
    chapter_number: int
    chapter_title: str | None = None
    number_of_pages: int = 0
    pages: list[str] = Field(default_factory=list)
    series_slug: str
    series_title: str
