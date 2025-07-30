#!/bin/bash
set -e  # Exit on error

# Startup script for Acta Diurna Docker container

echo "🚀 Starting Acta Diurna..."
echo "=================================="

# Set default port if not provided
export PORT=${PORT:-8000}

echo "📡 Port: $PORT"
echo "🌍 Environment: ${ENVIRONMENT:-development}"
echo "🗄️ Database: ${MONGO_URL:0:30}..."

# Verify backend directory exists
if [ ! -d "/app/backend" ]; then
    echo "❌ Backend directory not found!"
    exit 1
fi

# Verify frontend build exists
if [ ! -d "/app/frontend/build" ]; then
    echo "⚠️  Frontend build directory not found - API only mode"
fi

# Start FastAPI server with static file serving
echo "🔥 Starting FastAPI server..."
cd /app/backend

# Use exec to replace shell process and handle signals properly
exec uvicorn server:app \
    --host 0.0.0.0 \
    --port $PORT \
    --workers 1