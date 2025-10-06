#!/bin/bash

# Script to run essential E2E tests for Clash Royale Deck Builder
# Run only the API health tests which don't require browser

echo "🧪 Running Essential E2E Tests"
echo "================================"
echo ""

# Check if services are running
echo "📡 Checking services..."
if ! curl -s http://localhost:8000/health > /dev/null; then
    echo "❌ Backend is not running on port 8000"
    echo "   Run: docker-compose up -d backend"
    exit 1
fi

if ! curl -s http://localhost:3000 > /dev/null; then
    echo "❌ Frontend is not running on port 3000"
    echo "   Run: cd frontend && npm start"
    exit 1
fi

echo "✅ Backend is running"
echo "✅ Frontend is running"
echo ""

# Run only API tests (no browser required)
echo "🚀 Running API health tests..."
npx playwright test --grep "API Health" --reporter=list --headed=false

echo ""
echo "✅ Tests complete!"
