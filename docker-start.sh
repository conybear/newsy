#!/bin/bash

# Startup script for Acta Diurna Docker container

echo "🚀 Starting Acta Diurna..."
echo "=================================="

# Set default port if not provided
export PORT=${PORT:-8000}

echo "📡 Port: $PORT"
echo "🌍 Environment: ${ENVIRONMENT:-development}"
echo "🗄️ Database: ${MONGO_URL:0:20}..."

# Start FastAPI server with static file serving
echo "🔥 Starting FastAPI server..."
cd backend
exec uvicorn server:app \
    --host 0.0.0.0 \
    --port $PORT \
    --workers 1