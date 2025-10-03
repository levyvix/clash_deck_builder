#!/bin/bash

echo "========================================="
echo "Starting Backend API Server"
echo "========================================="
echo ""

cd backend

echo "Checking if port 8000 is available..."
if netstat -ano | grep -q ":8000"; then
    echo "⚠️  Warning: Port 8000 is already in use!"
    echo "Kill the process or the server may fail to start."
    echo ""
fi

echo "Starting FastAPI server with uvicorn..."
echo "API will be available at http://localhost:8000"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

uv run uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
