const { app, BrowserWindow } = require("electron");
const { spawn } = require("node:child_process");
const http = require("node:http");
const path = require("node:path");
const net = require("node:net");

let backendProcess = null;

const projectRoot = path.resolve(__dirname, "..");
const backendDir = path.join(projectRoot, "backend");
const venvPython = path.join(projectRoot, ".venv", "bin", "python");

function isPortOpen(port, host = "127.0.0.1") {
  return new Promise((resolve) => {
    const socket = new net.Socket();
    socket.setTimeout(500);
    socket.once("connect", () => {
      socket.destroy();
      resolve(true);
    });
    socket.once("timeout", () => {
      socket.destroy();
      resolve(false);
    });
    socket.once("error", () => resolve(false));
    socket.connect(port, host);
  });
}

function isPsyAffiliateBackend(port = 8000, host = "127.0.0.1") {
  return new Promise((resolve) => {
    const request = http.get({ host, port, path: "/api/health", timeout: 800 }, (response) => {
      let body = "";
      response.on("data", (chunk) => {
        body += chunk;
      });
      response.on("end", () => {
        try {
          const parsed = JSON.parse(body);
          resolve(parsed.app === "PsyAffiliate Studio");
        } catch {
          resolve(false);
        }
      });
    });
    request.on("timeout", () => {
      request.destroy();
      resolve(false);
    });
    request.on("error", () => resolve(false));
  });
}

function stopProcessOnPort(port) {
  if (process.platform !== "darwin") {
    return Promise.resolve();
  }
  return new Promise((resolve) => {
    const command = spawn("zsh", ["-lc", `PIDS=$(lsof -tiTCP:${port} -sTCP:LISTEN 2>/dev/null || true); [ -n "$PIDS" ] && kill $PIDS 2>/dev/null || true`], {
      stdio: "ignore",
    });
    command.on("close", () => resolve());
    command.on("error", () => resolve());
  });
}

async function startBackend() {
  if (process.env.PSYAFFILIATE_EXTERNAL_BACKEND === "true") {
    return;
  }
  if (await isPortOpen(8000)) {
    if (await isPsyAffiliateBackend()) {
      return;
    }
    await stopProcessOnPort(8000);
    await new Promise((resolve) => setTimeout(resolve, 700));
  }

  const python = process.platform === "win32" ? "python" : venvPython;
  backendProcess = spawn(
    python,
    ["-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8000"],
    {
      cwd: backendDir,
      env: {
        ...process.env,
        PYTHONUNBUFFERED: "1",
      },
      stdio: "inherit",
    },
  );
}

async function createWindow() {
  await startBackend();

  const window = new BrowserWindow({
    width: 1320,
    height: 860,
    minWidth: 1100,
    minHeight: 720,
    title: "PsyAffiliate Studio",
    webPreferences: {
      contextIsolation: true,
      nodeIntegration: false,
    },
  });

  await window.loadURL(process.env.VITE_DEV_SERVER_URL || "http://127.0.0.1:5173");
}

app.whenReady().then(createWindow);

app.on("window-all-closed", () => {
  if (process.platform !== "darwin") {
    app.quit();
  }
});

app.on("before-quit", () => {
  if (backendProcess) {
    backendProcess.kill();
    backendProcess = null;
  }
});

app.on("activate", () => {
  if (BrowserWindow.getAllWindows().length === 0) {
    createWindow();
  }
});
