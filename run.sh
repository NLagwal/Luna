#!/bin/bash

# Luna: AI Assistant Startup Script

# 1. Configuration
BACKEND_PORT=5000
FRONTEND_PORT=8080
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

# 3. Start ChromaDB via Docker
echo "📦 Starting ChromaDB (Docker)..."
docker compose up -d
if [ $? -ne 0 ]; then
    echo "❌ Failed to start Docker. Please ensure Docker is running."
    exit 1
fi

# 4. Activate Virtual Environment
if [ -d "$VENV_PATH" ]; then
    echo "🐍 Activating virtual environment..."
    source "$VENV_PATH/bin/activate"
else
    echo "⚠️ Virtual environment not found at $VENV_PATH. Please run 'python -m venv .venv && pip install -r requirements.txt' first."
    exit 1
fi

# 5. Start Backend API
echo "🤖 Starting Luna Backend (FastAPI) on port $BACKEND_PORT..."
python app.py > backend.log 2>&1 &
BACKEND_PID=$!

# 6. Start Frontend Server
echo "🌐 Starting Frontend Server on port $FRONTEND_PORT..."
python -m http.server $FRONTEND_PORT > frontend.log 2>&1 &
FRONTEND_PID=$!

# 7. Cleanup on Exit
cleanup() {
    echo -e "\n🛑 Shutting down Luna..."
    kill $BACKEND_PID
    kill $FRONTEND_PID
    docker compose stop
    echo "✅ Done."
    exit
}

trap cleanup SIGINT SIGTERM

echo "✨ Luna is now running!"
echo "🔗 Backend API: http://localhost:$BACKEND_PORT"
echo "🔗 Frontend Site: http://localhost:$FRONTEND_PORT/www.juit.ac.in/index.html"
echo "📝 Logs are being written to backend.log and frontend.log"
echo "⌨️  Press Ctrl+C to stop all services."

# Keep the script running
wait
