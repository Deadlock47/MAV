const { app, BrowserWindow } = require("electron");
const { spawn } = require("child_process");
const path = require("path");

const BACKEND_HOST = "127.0.0.1";
const BACKEND_PORT = Number(process.env.MAV_BACKEND_PORT || 8765);

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

  return process.platform === "win32" ? "python" : "python3";
}

function startBackend() {
  if (backendProcess) {
    return;
  }

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
}

function stopBackend() {
  if (!backendProcess) {
    return;
  }

  backendProcess.kill();
  backendProcess = null;
}

function createWindow() {
  const window = new BrowserWindow({
    width: 1520,
    height: 960,
    minWidth: 1180,
    minHeight: 760,
    backgroundColor: "#09111f",
    autoHideMenuBar: true,
    title: "MAV Desktop",
    webPreferences: {
      preload: path.join(__dirname, "preload.cjs"),
      contextIsolation: true,
      nodeIntegration: false,
    },
  });

  window.loadFile(getRendererEntry());
}

app.whenReady().then(() => {
  startBackend();
  createWindow();

  app.on("activate", () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow();
    }
  });
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
