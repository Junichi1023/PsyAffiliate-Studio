#!/bin/zsh
set -e

PROJECT_DIR="/Users/user/Documents/New project/PsyAffiliate-Studio"

cd "$PROJECT_DIR"

if [ ! -d "node_modules" ] || [ ! -d "frontend/node_modules" ] || [ ! -d ".venv" ]; then
  echo "First launch setup is running..."
  npm run setup
fi

echo "Starting PsyAffiliate Studio..."
npm run dev
