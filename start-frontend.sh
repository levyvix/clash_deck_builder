#!/bin/bash

echo "========================================="
echo "Starting Frontend Development Server"
echo "========================================="
echo ""

cd frontend

echo "Checking if port 3000 is available..."
if netstat -ano | grep -q ":3000"; then
    echo "⚠️  Warning: Port 3000 is already in use!"
    echo "Kill the process or the server may fail to start."
    echo ""
fi

echo "Starting React development server..."
echo "This will open in your browser at http://localhost:3000"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

npm start
