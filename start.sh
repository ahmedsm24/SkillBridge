#!/bin/bash

# Start script for Resume-to-Training Module Generator

echo "🚀 Starting Resume-to-Training Module Generator..."
echo ""

# Check if backend is already running
if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null ; then
    echo "✅ Backend is already running on http://localhost:8000"
else
    echo "📦 Starting Backend..."
    cd backend
    if [ ! -d "venv" ]; then
        echo "Creating virtual environment..."
        python3 -m venv venv
    fi
    source venv/bin/activate
    pip install -q fastapi uvicorn sqlalchemy python-multipart pdfplumber pydantic pydantic-settings python-dotenv langchain langchain-openai openai 2>/dev/null || echo "Dependencies may already be installed"
    echo "✅ Backend starting on http://localhost:8000"
    python -m uvicorn src.main:app --reload --host 0.0.0.0 --port 8000 &
    cd ..
    sleep 2
fi

# Check if frontend is already running
if lsof -Pi :3000 -sTCP:LISTEN -t >/dev/null ; then
    echo "✅ Frontend is already running on http://localhost:3000"
else
    echo "📦 Starting Frontend..."
    cd frontend
    # Remove workspace dependency issues
    if [ ! -d "node_modules" ]; then
        echo "Installing frontend dependencies (this may take a minute)..."
        # Install without workspace
        npm install --no-workspaces next@14.0.4 react@18.2.0 react-dom@18.2.0 tailwindcss@3.3.6 clsx@2.0.0 tailwind-merge@2.2.0 typescript@5.3.3 @types/node@20.10.5 @types/react@18.2.45 @types/react-dom@18.2.18 eslint@8.56.0 eslint-config-next@14.0.4 autoprefixer@10.4.16 postcss@8.4.32 2>&1 | grep -v "npm WARN" || true
    fi
    echo "✅ Frontend starting on http://localhost:3000"
    npm run dev &
    cd ..
    sleep 3
fi

echo ""
echo "✨ Application is running!"
echo ""
echo "📍 Backend API: http://localhost:8000"
echo "📍 API Docs: http://localhost:8000/docs"
echo "📍 Frontend: http://localhost:3000"
echo ""
echo "Press Ctrl+C to stop all servers"
echo ""

# Wait for user interrupt
wait



