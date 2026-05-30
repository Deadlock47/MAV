# MAV (Manhwa & JAV Viewer)

A full-stack desktop application for browsing JAV (Japanese Adult Video) catalog and Manhwa series with a React + Electron frontend and FastAPI backend.

## 📁 Project Structure

### `backend/`
**Backend API server** - FastAPI application serving JAV catalog and Manhwa data.

**Contents:**
- `app/` - FastAPI application code
  - `main.py` - Entry point with API routes
  - `repository.py` - Data access layer
  - `duckdb_store.py` - DuckDB cache management
  - `schemas.py` - Data schemas
  - `manhwa_repository.py` - Manhwa data handling
- `data/` - Runtime data cache
  - `jvify.duckdb` - Cached DuckDB database (generated on first run)
  - `manhwa/` - Manhwa JSON metadata and cached chapter manifests
- `requirements.txt` - Python dependencies
- `package.json` - Node.js metadata

**Run Backend:**
```bash
cd backend
pip install -r requirements.txt
python -m app.sync_duckdb          # Sync parquet files to DuckDB cache (first time)
uvicorn app.main:app --reload      # Start dev server (http://localhost:8000)
```

**API Endpoints:**
```
GET /api/health                          - Health check
GET /api/jav/videos?limit=18&offset=0   - List JAV videos
GET /api/jav/videos/{content_id}        - Get video details
GET /api/videos/details?content_id=hmn  - Get video by content ID
GET /api/manhwa                          - List all manhwa series
GET /api/manhwa/{slug}                   - Get manhwa series details
GET /api/manhwa/{slug}/chapters/{num}   - Get chapter pages
```

**Environment Variables:**
- `JVIFY_DB_DIR` - Override parquet source directory (default: `../db`)
- `JVIFY_DUCKDB_PATH` - Override DuckDB cache path (default: `backend/data/jvify.duckdb`)
- `JVIFY_MANHWA_DIR` - Override manhwa JSON path (default: `backend/data/manhwa`)

---

### `frontend-react/`
**Desktop UI** - React + Electron Vite application providing desktop UI.

**Contents:**
- `src/` - React source code
  - `components/` - Reusable React components
  - `pages/` - Page components
  - `assets/` - Static assets (images, svgs)
  - `App.jsx` - Main app component
  - `main.jsx` - React entry point
- `electron/` - Electron main process
  - `main.js` - Electron app entry point
  - `preload.js` - Preload script for IPC
- `public/` - Static public files
- `package.json` - Node.js dependencies and scripts
- `vite.config.js` - Vite configuration
- `tailwind.config.js` - Tailwind CSS configuration

**Run Frontend (Development):**
```bash
cd frontend-react
npm install
npm run dev    # Start dev server (http://localhost:5173) + Electron window
```

**Run Frontend (Production):**
```bash
cd frontend-react
npm run build   # Build optimized bundle
npm start       # Launch Electron app from built assets
```

---

### `db/`
**Data Store** - Parquet files containing JAV catalog metadata.

**Contents:**
- `derived_video.parquet` - Video catalog (main dataset)
- `machine_translation.parquet` - Translation data
- `source_dmm_trailer.parquet` - DMM trailer metadata
- `derived_video_category.parquet` - Category mappings
- `derived_video_actress.parquet` - Actress information
- `derived_video_actor.parquet` - Actor information

**Purpose:** Raw data source for the backend. Synced to DuckDB cache on startup.

---

### `.gitignore`
Git ignore rules to prevent large binary files from being tracked:
- `*.parquet`, `*.duckdb` - Large data files
- `**/node_modules/` - Dependency folders
- `**/dist/`, `**/build/` - Build outputs
- `**/__pycache__/` - Python cache
- `.env` - Environment variables

---

## 🚀 Quick Start

### Full Stack Setup (Backend + Frontend)

**Terminal 1 - Backend:**
```bash
cd backend
pip install -r requirements.txt
python -m app.sync_duckdb
uvicorn app.main:app --reload
```

**Terminal 2 - Frontend:**
```bash
cd frontend-react
npm install
npm run dev
```

This will:
1. Start API on `http://localhost:8000`
2. Start Vite dev server on `http://localhost:5173`
3. Launch Electron desktop window connected to the API

---

## 📋 Prerequisites

- **Python 3.8+** - For backend
- **Node.js 16+** - For frontend
- **pip & npm** - Package managers

---

## 🛠️ Development

### Backend Development
- Hot reload enabled with `--reload` flag
- Modify `app/*.py` to see changes instantly
- DuckDB cache syncs on startup if parquet files changed

### Frontend Development
- Hot reload enabled with Vite
- Modify `src/` files to see changes in Electron window
- Tailwind CSS live compilation

### Data Refresh
If parquet files in `db/` are updated:
```bash
cd backend
python -m app.sync_duckdb  # Re-sync parquet to DuckDB
# Then restart the API
```

---

## 📦 Build & Deployment

### Build Frontend
```bash
cd frontend-react
npm run build      # Creates dist/ folder
npm start          # Run Electron with built app
```

### Build Electron Installer
```bash
cd frontend-react
npm run build
# Installer output goes to dist/
```

---

## 🗂️ File Structure Summary

```
MAV/
├── backend/              # FastAPI backend server
│   ├── app/              # Application code
│   ├── data/             # Runtime cache & metadata
│   ├── requirements.txt   # Python dependencies
│   └── README.md         # Backend docs
├── frontend-react/       # React + Electron desktop app
│   ├── src/              # React components & pages
│   ├── electron/         # Electron main process
│   ├── public/           # Static assets
│   └── package.json      # Node dependencies
├── db/                   # Parquet data files
│   ├── derived_video.parquet
│   ├── machine_translation.parquet
│   └── ...
└── .gitignore            # Git ignore rules
```

---

## 🔗 Key Commands

| Command | Location | Purpose |
|---------|----------|---------|
| `pip install -r requirements.txt` | `backend/` | Install Python deps |
| `python -m app.sync_duckdb` | `backend/` | Sync parquet → DuckDB |
| `uvicorn app.main:app --reload` | `backend/` | Start API server |
| `npm install` | `frontend-react/` | Install Node deps |
| `npm run dev` | `frontend-react/` | Start dev server + Electron |
| `npm run build` | `frontend-react/` | Build optimized bundle |
| `npm start` | `frontend-react/` | Launch Electron app |

---

## 📝 Notes

- **Backend**: Uses FastAPI + DuckDB for caching parquet files
- **Frontend**: React 19 with Vite bundler + Electron for desktop
- **Styling**: Tailwind CSS
- **Data**: Parquet files auto-synced to DuckDB on first backend run
- **Desktop**: Electron shell wraps React app for standalone desktop deployment

---

## 🤝 Contributing

1. Backend: Modify `backend/app/` and restart API
2. Frontend: Modify `frontend-react/src/` (hot reload works)
3. Data: Update parquet files in `db/` and run `python -m app.sync_duckdb`

---

**Last Updated:** May 30, 2026
