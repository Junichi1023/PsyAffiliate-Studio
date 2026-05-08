#!/bin/zsh
set -e

PROJECT_DIR="/Users/user/Documents/New project/PsyAffiliate-Studio"

cd "$PROJECT_DIR"

if [ ! -d "node_modules" ] || [ ! -d "frontend/node_modules" ] || [ ! -d ".venv" ]; then
  echo "First launch setup is running..."
  npm run setup
fi

FRONTEND_PIDS=$(lsof -tiTCP:5173 -sTCP:LISTEN 2>/dev/null || true)
if [ -n "$FRONTEND_PIDS" ]; then
  echo "Stopping an existing local frontend process on port 5173..."
  kill $FRONTEND_PIDS 2>/dev/null || true
  sleep 1
fi

if lsof -tiTCP:8000 -sTCP:LISTEN >/dev/null 2>&1; then
  HEALTH_APP=$(curl -s http://127.0.0.1:8000/api/health | /usr/bin/python3 -c 'import json,sys; print(json.load(sys.stdin).get("app",""))' 2>/dev/null || true)
  if [ "$HEALTH_APP" != "PsyAffiliate Studio" ]; then
    echo "Stopping a different local backend process on port 8000..."
    BACKEND_PIDS=$(lsof -tiTCP:8000 -sTCP:LISTEN 2>/dev/null || true)
    kill $BACKEND_PIDS 2>/dev/null || true
    sleep 1
  fi
fi

echo "Starting PsyAffiliate Studio..."
npm run dev
