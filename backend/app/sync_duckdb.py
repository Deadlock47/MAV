from __future__ import annotations

from .config import get_settings
from .duckdb_store import DuckDBStore


def main() -> None:
    settings = get_settings()
    store = DuckDBStore(settings.db_dir, settings.duckdb_path)
    store.ensure_ready()
    print(f"DuckDB is ready at {settings.duckdb_path}")


if __name__ == "__main__":
    main()
