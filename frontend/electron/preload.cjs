const { contextBridge } = require("electron");

const backendHost = "127.0.0.1";
const backendPort = Number(process.env.MAV_BACKEND_PORT || 8765);

contextBridge.exposeInMainWorld("desktop", {
  backendBaseUrl: `http://${backendHost}:${backendPort}`,
  platform: process.platform,
});
