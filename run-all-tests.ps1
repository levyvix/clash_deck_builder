# Clash Royale Deck Builder - Run All Tests
# This script runs the complete test suite across backend, frontend, and E2E

$ErrorActionPreference = "Stop"

Write-Host "========================================" -ForegroundColor Blue
Write-Host "Clash Royale Deck Builder - Test Suite" -ForegroundColor Blue
Write-Host "========================================`n" -ForegroundColor Blue

# Check if services are running
Write-Host "📋 Checking services..." -ForegroundColor Yellow

try {
    $null = Invoke-WebRequest -Uri "http://localhost:8000/health" -UseBasicParsing -TimeoutSec 2
    Write-Host "✅ Backend is running" -ForegroundColor Green
} catch {
    Write-Host "❌ Backend not running at http://localhost:8000" -ForegroundColor Red
    Write-Host "💡 Start with: docker-compose up -d backend database" -ForegroundColor Yellow
    exit 1
}

try {
    $null = Invoke-WebRequest -Uri "http://localhost:3000" -UseBasicParsing -TimeoutSec 2
    Write-Host "✅ Frontend is running`n" -ForegroundColor Green
} catch {
    Write-Host "❌ Frontend not running at http://localhost:3000" -ForegroundColor Red
    Write-Host "💡 Start with: cd frontend && npm start" -ForegroundColor Yellow
    exit 1
}

# Backend Tests
Write-Host "========================================" -ForegroundColor Blue
Write-Host "🔧 Running Backend Tests" -ForegroundColor Blue
Write-Host "========================================" -ForegroundColor Blue

Push-Location backend
try {
    uv run pytest --cov=src --cov-report=html --cov-report=term
    if ($LASTEXITCODE -ne 0) { throw "Backend tests failed" }
    Write-Host "✅ Backend tests passed`n" -ForegroundColor Green
} catch {
    Write-Host "❌ Backend tests failed`n" -ForegroundColor Red
    Pop-Location
    exit 1
}
Pop-Location

# Frontend Tests
Write-Host "========================================" -ForegroundColor Blue
Write-Host "⚛️  Running Frontend Tests" -ForegroundColor Blue
Write-Host "========================================" -ForegroundColor Blue

Push-Location frontend
try {
    npm run test:run -- --coverage --watchAll=false
    if ($LASTEXITCODE -ne 0) { throw "Frontend tests failed" }
    Write-Host "✅ Frontend tests passed`n" -ForegroundColor Green
} catch {
    Write-Host "❌ Frontend tests failed`n" -ForegroundColor Red
    Pop-Location
    exit 1
}
Pop-Location

# E2E Tests - Basic
Write-Host "========================================" -ForegroundColor Blue
Write-Host "🌐 Running E2E Tests (Basic)" -ForegroundColor Blue
Write-Host "========================================" -ForegroundColor Blue

try {
    npx playwright test e2e-deck-basic --reporter=line
    if ($LASTEXITCODE -ne 0) { throw "E2E basic tests failed" }
    Write-Host "✅ E2E basic tests passed`n" -ForegroundColor Green
} catch {
    Write-Host "❌ E2E basic tests failed`n" -ForegroundColor Red
    exit 1
}

# E2E Tests - Essential
Write-Host "========================================" -ForegroundColor Blue
Write-Host "🌐 Running E2E Tests (Essential)" -ForegroundColor Blue
Write-Host "========================================" -ForegroundColor Blue

try {
    npx playwright test e2e-essential --reporter=line
    if ($LASTEXITCODE -ne 0) { throw "E2E essential tests failed" }
    Write-Host "✅ E2E essential tests passed`n" -ForegroundColor Green
} catch {
    Write-Host "❌ E2E essential tests failed`n" -ForegroundColor Red
    exit 1
}

# Summary
Write-Host "========================================" -ForegroundColor Blue
Write-Host "✅ All Tests Passed!" -ForegroundColor Green
Write-Host "========================================`n" -ForegroundColor Blue

Write-Host "📊 Coverage Reports:" -ForegroundColor Yellow
Write-Host "  Backend:  " -NoNewline; Write-Host "backend\htmlcov\index.html" -ForegroundColor Blue
Write-Host "  Frontend: " -NoNewline; Write-Host "frontend\coverage\lcov-report\index.html" -ForegroundColor Blue
Write-Host "`n📈 Test Report:" -ForegroundColor Yellow
Write-Host "  Playwright: " -NoNewline; Write-Host "npx playwright show-report`n" -ForegroundColor Blue

exit 0
