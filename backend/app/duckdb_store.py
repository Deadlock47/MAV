from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import duckdb


@dataclass(frozen=True)
class TableSource:
    key: str
    table_name: str
    parquet_path: Path
    index_columns: tuple[str, ...] = ()


class DuckDBStore:
    SNAPSHOT_TABLE = "app_source_snapshot"

    def __init__(self, db_dir: Path, duckdb_path: Path) -> None:
        self.db_dir = db_dir
        self.duckdb_path = duckdb_path
        self.sources = {
            "video": TableSource(
                key="video",
                table_name="video",
                parquet_path=db_dir / "derived_video.parquet",
                index_columns=("content_id", "dvd_id"),
            ),
            "maker": TableSource(
                key="maker",
                table_name="maker",
                parquet_path=db_dir / "derived_maker.parquet",
                index_columns=("id",),
            ),
            "label": TableSource(
                key="label",
                table_name="label",
                parquet_path=db_dir / "derived_label.parquet",
                index_columns=("id",),
            ),
            "series": TableSource(
                key="series",
                table_name="series",
                parquet_path=db_dir / "derived_series.parquet",
                index_columns=("id",),
            ),
            "site": TableSource(
                key="site",
                table_name="site",
                parquet_path=db_dir / "derived_site.parquet",
                index_columns=("id",),
            ),
            "video_actress": TableSource(
                key="video_actress",
                table_name="video_actress",
                parquet_path=db_dir / "derived_video_actress.parquet",
                index_columns=("content_id", "actress_id"),
            ),
            "actress": TableSource(
                key="actress",
                table_name="actress",
                parquet_path=db_dir / "derived_actress.parquet",
                index_columns=("id",),
            ),
            "video_actor": TableSource(
                key="video_actor",
                table_name="video_actor",
                parquet_path=db_dir / "derived_video_actor.parquet",
                index_columns=("content_id", "actor_id"),
            ),
            "actor": TableSource(
                key="actor",
                table_name="actor",
                parquet_path=db_dir / "derived_actor.parquet",
                index_columns=("id",),
            ),
            "video_director": TableSource(
                key="video_director",
                table_name="video_director",
                parquet_path=db_dir / "derived_video_director.parquet",
                index_columns=("content_id", "director_id"),
            ),
            "director": TableSource(
                key="director",
                table_name="director",
                parquet_path=db_dir / "derived_director.parquet",
                index_columns=("id",),
            ),
            "video_author": TableSource(
                key="video_author",
                table_name="video_author",
                parquet_path=db_dir / "derived_video_author.parquet",
                index_columns=("content_id", "author_id"),
            ),
            "author": TableSource(
                key="author",
                table_name="author",
                parquet_path=db_dir / "derived_author.parquet",
                index_columns=("id",),
            ),
            "video_category": TableSource(
                key="video_category",
                table_name="video_category",
                parquet_path=db_dir / "derived_video_category.parquet",
                index_columns=("content_id", "category_id"),
            ),
            "category": TableSource(
                key="category",
                table_name="category",
                parquet_path=db_dir / "derived_category.parquet",
                index_columns=("id",),
            ),
            "trailer": TableSource(
                key="trailer",
                table_name="trailer",
                parquet_path=db_dir / "source_dmm_trailer.parquet",
                index_columns=("content_id",),
            ),
            "video_histrion": TableSource(
                key="video_histrion",
                table_name="video_histrion",
                parquet_path=db_dir / "source_dmm_video_histrion.parquet",
                index_columns=("content_id", "histrion_id"),
            ),
            "histrion": TableSource(
                key="histrion",
                table_name="histrion",
                parquet_path=db_dir / "source_dmm_histrion.parquet",
                index_columns=("id",),
            ),
            "machine_translation": TableSource(
                key="machine_translation",
                table_name="machine_translation",
                parquet_path=db_dir / "machine_translation.parquet",
                index_columns=("source_ja",),
            ),
        }

    def ensure_ready(self) -> None:
        missing = [source.parquet_path.name for source in self.sources.values() if not source.parquet_path.exists()]
        if missing:
            if self.duckdb_path.exists():
                return

            missing_list = ", ".join(sorted(missing))
            raise RuntimeError(
                f"Missing parquet files in {self.db_dir}: {missing_list}. "
                "A cached DuckDB file was not found, so the database cannot be opened."
            )

        self.duckdb_path.parent.mkdir(parents=True, exist_ok=True)
        if self._needs_refresh():
            self._rebuild_database()

    def connect(self, *, read_only: bool = True) -> duckdb.DuckDBPyConnection:
        return duckdb.connect(str(self.duckdb_path), read_only=read_only)

    def table(self, key: str) -> str:
        return self.sources[key].table_name

    def _needs_refresh(self) -> bool:
        if not self.duckdb_path.exists():
            return True

        con: duckdb.DuckDBPyConnection | None = None
        try:
            con = self.connect(read_only=True)
            stored_rows = con.execute(
                f"""
                SELECT table_key, parquet_name, size_bytes, modified_ns
                FROM {self.SNAPSHOT_TABLE}
                ORDER BY table_key
                """
            ).fetchall()
        except Exception:
            return True
        finally:
            if con is not None:
                con.close()

        current_rows = sorted(
            [
                (
                    source.key,
                    source.parquet_path.name,
                    source.parquet_path.stat().st_size,
                    source.parquet_path.stat().st_mtime_ns,
                )
                for source in self._iter_sources()
            ],
            key=lambda row: row[0],
        )
        return stored_rows != current_rows

    def _rebuild_database(self) -> None:
        if self.duckdb_path.exists():
            self.duckdb_path.unlink()
        self._cleanup_db_sidecars(self.duckdb_path)

        con = duckdb.connect(str(self.duckdb_path))
        try:
            con.execute("PRAGMA threads=4")
            for source in self._iter_sources():
                parquet_sql_path = self._escape_path(source.parquet_path)
                con.execute(
                    f"""
                    CREATE TABLE {source.table_name} AS
                    SELECT *
                    FROM read_parquet('{parquet_sql_path}')
                    """
                )
                for column in source.index_columns:
                    con.execute(
                        f"""
                        CREATE INDEX idx_{source.table_name}_{column}
                        ON {source.table_name} ({column})
                        """
                    )

            con.execute(
                f"""
                CREATE TABLE {self.SNAPSHOT_TABLE} (
                    table_key VARCHAR,
                    parquet_name VARCHAR,
                    size_bytes BIGINT,
                    modified_ns BIGINT
                )
                """
            )
            con.executemany(
                f"INSERT INTO {self.SNAPSHOT_TABLE} VALUES (?, ?, ?, ?)",
                [
                    (
                        source.key,
                        source.parquet_path.name,
                        source.parquet_path.stat().st_size,
                        source.parquet_path.stat().st_mtime_ns,
                    )
                    for source in self._iter_sources()
                ],
            )
            con.execute("CHECKPOINT")
        finally:
            con.close()

    def _iter_sources(self) -> Iterable[TableSource]:
        return self.sources.values()

    def _escape_path(self, path: Path) -> str:
        return path.as_posix().replace("'", "''")

    def _cleanup_db_sidecars(self, db_path: Path) -> None:
        for path in (
            db_path.with_suffix(f"{db_path.suffix}.wal"),
            db_path.with_name(f"{db_path.name}.wal"),
        ):
            if path.exists():
                path.unlink()
