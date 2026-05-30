from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
import os
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    app_name: str
    backend_dir: Path
    data_dir: Path
    db_dir: Path
    duckdb_path: Path
    manhwa_dir: Path
    html_cache_dir: Path


@lru_cache
def get_settings() -> Settings:
    backend_dir = Path(__file__).resolve().parents[1]
    data_dir = backend_dir / "data"
    default_db_dir = backend_dir.parent / "db"
    default_duckdb_path = data_dir / "jvify.duckdb"
    db_dir = Path(os.getenv("JVIFY_DB_DIR", default_db_dir)).resolve()
    duckdb_path = Path(os.getenv("JVIFY_DUCKDB_PATH", default_duckdb_path)).resolve()
    manhwa_dir = Path(os.getenv("JVIFY_MANHWA_DIR", data_dir / "manhwa")).resolve()

    return Settings(
        app_name="Jvify Video API",
        backend_dir=backend_dir,
        data_dir=data_dir,
        db_dir=db_dir,
        duckdb_path=duckdb_path,
        manhwa_dir=manhwa_dir,
        html_cache_dir=backend_dir / "app",
    )
