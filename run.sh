#!/bin/bash

# Luna: AI Assistant Startup Script (Rebuilt Version)

# 1. Configuration
BACKEND_PORT=5000
FRONTEND_PORT=8000
VENV_PATH="./.venv"

echo "🚀 Starting Luna: AI Assistant..."

# 2. Cleanup existing processes on ports
echo "🧹 Checking for existing processes on ports $BACKEND_PORT and $FRONTEND_PORT..."
for port in $BACKEND_PORT $FRONTEND_PORT; do
    PID=$(lsof -t -i:$port)
    if [ ! -z "$PID" ]; then
        echo "⚠️ Killing existing process on port $port (PID: $PID)"
        kill -9 $PID
    fi
done

# 3. Start Infrastructure via Docker (Postgres + ChromaDB)
echo "📦 Starting Infrastructure (Docker: Postgres & ChromaDB)..."
docker compose up -d
if [ $? -ne 0 ]; then
    echo "❌ Failed to start Docker. Please ensure Docker is running."
    exit 1
fi

echo "⏳ Waiting for PostgreSQL to be ready..."
until docker compose exec -T postgres pg_isready -U luna_user -d luna_db > /dev/null 2>&1; do
    echo "Waiting for PostgreSQL..."
    sleep 1
done
echo "✅ PostgreSQL is ready."

# 4. Activate Virtual Environment
if [ -d "$VENV_PATH" ]; then
    echo "🐍 Activating virtual environment..."
    source "$VENV_PATH/bin/activate"
else
    echo "⚠️ Virtual environment not found at $VENV_PATH."
    exit 1
fi

# 5. Start Backend API
mkdir -p logs
echo "🤖 Starting Luna Backend (FastAPI with auto-reload) on port $BACKEND_PORT..."
uvicorn src.main:app --host 0.0.0.0 --port $BACKEND_PORT --reload > logs/server.log 2>&1 &
BACKEND_PID=$!

# Wait briefly and verify backend started
sleep 2
if ! kill -0 $BACKEND_PID 2>/dev/null; then
    echo "❌ Backend failed to start. Check logs/server.log for details."
    cat logs/server.log
    exit 1
fi

# 6. Start Frontend Server (Serving from Root)
echo "🌐 Starting Frontend Server on port $FRONTEND_PORT..."
python -m http.server $FRONTEND_PORT > logs/frontend.log 2>&1 &
FRONTEND_PID=$!

# 7. Cleanup on Exit
cleanup() {
    echo -e "\n🛑 Shutting down Luna..."
    kill $BACKEND_PID 2>/dev/null || true
    kill $FRONTEND_PID 2>/dev/null || true
    echo "✅ Done."
    exit 0
}

trap cleanup SIGINT SIGTERM EXIT

echo "✨ Luna is now running!"
echo "🔗 Backend API: http://localhost:$BACKEND_PORT/health"
echo "🔗 Frontend Site: http://localhost:$FRONTEND_PORT/www.juit.ac.in/index.html"
echo "📝 Logs: logs/server.log, logs/frontend.log"
echo "⌨️  Press Ctrl+C to stop all services."

# Monitor processes
while kill -0 $BACKEND_PID 2>/dev/null && kill -0 $FRONTEND_PID 2>/dev/null; do
    sleep 1
done
