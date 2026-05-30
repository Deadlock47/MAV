import { app, BrowserWindow } from "electron";
import path from "path";
import { fileURLToPath } from "url";
// const { app, BrowserWindow } = require("electron");
// const { spawn } = require("child_process");
import spawn from "cross-spawn";
// const path = require("path");
// import path from path;

const BACKEND_HOST = "127.0.0.1";
const BACKEND_PORT = Number(process.env.MAV_BACKEND_PORT || 8765);

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

let backendProcess = null;

function getRendererEntry() {
  return path.join(__dirname, "..", "src", "index.html");
}

function getBackendDirectory() {
  if (app.isPackaged) {
    return path.join(process.resourcesPath, "backend");
  }

  return path.join(__dirname, "..", "..", "backend");
}

function resolvePythonCommand() {
  if (process.env.MAV_PYTHON_PATH) {
    return process.env.MAV_PYTHON_PATH;
  }

  // On Windows, try python first, then python3
  // On Unix, try python3 first, then python
  if (process.platform === "win32") {
    return "python";
  }
  return "python3";
}
function createWindow() {
  const win = new BrowserWindow({
    width: 1200,
    height: 800,
    webPreferences: {
      contextIsolation: true,
      nodeIntegration: false,
    },
  });

  win.loadURL("http://localhost:5173");

  // For production:
  // win.loadFile(path.join(__dirname, "../dist/index.html"));
}

function startBackend() {
  if (backendProcess) {
    return;
  }

  console.log("[backend] Starting backend server...");
  console.log(`[backend] Using Python command: ${resolvePythonCommand()}`);
  console.log(`[backend] Backend directory: ${getBackendDirectory()}`);

  backendProcess = spawn(
    resolvePythonCommand(),
    [
      "-m",
      "uvicorn",
      "app.main:app",
      "--host",
      BACKEND_HOST,
      "--port",
      String(BACKEND_PORT),
    ],
    {
      cwd: getBackendDirectory(),
      env: {
        ...process.env,
        PYTHONIOENCODING: "utf-8",
      },
      stdio: ["ignore", "pipe", "pipe"],
      windowsHide: true,
    }
  );

  backendProcess.stdout.on("data", (chunk) => {
    const message = chunk.toString().trimEnd();
    if (message) {
      console.log(`[backend] ${message}`);
    }
  });

  backendProcess.stderr.on("data", (chunk) => {
    const message = chunk.toString().trimEnd();
    if (message) {
      console.error(`[backend] ${message}`);
    }
  });

  backendProcess.on("error", (error) => {
    console.error("[backend] failed to launch", error);
  });

  backendProcess.on("exit", (code, signal) => {
    if (!app.isQuitting) {
      console.warn(`[backend] exited early (code=${code}, signal=${signal})`);
    }
    backendProcess = null;
  });

  console.log(`[backend] Attempting to start server at http://${BACKEND_HOST}:${BACKEND_PORT}`);
}

function stopBackend() {
  if (!backendProcess) {
    return;
  }

  backendProcess.kill();
  backendProcess = null;
}

app.whenReady()
  .then(() => {
    startBackend();
    createWindow();
  })
  .catch((error) => {
    console.error("Failed to initialize app:", error);
    process.exit(1);
  });

app.on("before-quit", () => {
  app.isQuitting = true;
  stopBackend();
});

app.on("window-all-closed", () => {
  if (process.platform !== "darwin") {
    app.quit();
  }
});

// Handle uncaught exceptions
process.on("uncaughtException", (error) => {
  console.error("Uncaught Exception:", error);
  process.exit(1);
});

// Handle unhandled promise rejections
process.on("unhandledRejection", (reason, promise) => {
  console.error("Unhandled Rejection at:", promise, "reason:", reason);
  process.exit(1);
});