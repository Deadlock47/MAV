# Frontend Structure

## Run

```bash
npm install
npm start
```

The Electron process auto-starts the FastAPI backend from `../backend`.

## Build

```bash
npm run build
```

This creates a Windows installer through `electron-builder`.

## Layout

- `electron/`
  Electron main-process files, preload bridge, and desktop boot logic.
- `src/app/`
  Router, state, rendering, and browser-side application logic.
- `src/services/`
  API client for the local FastAPI server.
- `src/styles/`
  Shared desktop styling.
- `src/utils/`
  Small formatting helpers.

## Note

The packaged app bundles the backend source and local content files. It still expects Python and the backend dependencies to be available on the machine when the backend process is launched.
