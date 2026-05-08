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

echo "Starting PsyAffiliate Studio..."
npm run dev
