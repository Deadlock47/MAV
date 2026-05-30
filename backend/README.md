# MAV Backend

## Run

```bash
pip install -r requirements.txt
python -m app.sync_duckdb
uvicorn app.main:app --reload
```

The API reads parquet files from `../db` by default and caches the merged DuckDB database at `backend/data/jvify.duckdb`.

## Environment overrides

- `JVIFY_DB_DIR`
  Override the parquet source directory.
- `JVIFY_DUCKDB_PATH`
  Override the cached DuckDB database path.
- `JVIFY_MANHWA_DIR`
  Override the local manhwa JSON shelf path.

If the parquet files are missing but `backend/data/jvify.duckdb` already exists, the API now uses the cached DuckDB file directly. That makes the Electron shell easier to package for desktop use.

## API surface

```text
GET /api/health

GET /api/jav/videos?limit=18&offset=0&q=hmn
GET /api/jav/videos/{content_id}
GET /api/videos/details?content_id=hmn283
GET /api/videos/details?dvd_id=HMN-283

GET /api/manhwa
GET /api/manhwa/{slug}
GET /api/manhwa/{slug}/chapters/{chapter_number}
```

## Data notes

- `db/`
  Raw parquet sources for the JAV catalog.
- `backend/data/jvify.duckdb`
  Cached DuckDB database used by the repository layer.
- `backend/data/manhwa/`
  JSON metadata per series plus optional cached chapter page manifests.

## Refresh flow

When new parquet files arrive, run:

```bash
python -m app.sync_duckdb
```

Then restart the API:

```bash
uvicorn app.main:app --reload
```
