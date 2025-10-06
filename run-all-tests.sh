#!/bin/bash

# Clash Royale Deck Builder - Run All Tests
# This script runs the complete test suite across backend, frontend, and E2E

set -e  # Exit on error

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Clash Royale Deck Builder - Test Suite${NC}"
echo -e "${BLUE}========================================${NC}\n"

# Check if services are running
echo -e "${YELLOW}📋 Checking services...${NC}"

if ! curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo -e "${RED}❌ Backend not running at http://localhost:8000${NC}"
    echo -e "${YELLOW}💡 Start with: docker-compose up -d backend database${NC}"
    exit 1
fi

if ! curl -s http://localhost:3000 > /dev/null 2>&1; then
    echo -e "${RED}❌ Frontend not running at http://localhost:3000${NC}"
    echo -e "${YELLOW}💡 Start with: cd frontend && npm start${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Backend is running${NC}"
echo -e "${GREEN}✅ Frontend is running${NC}\n"

# Backend Tests
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}🔧 Running Backend Tests${NC}"
echo -e "${BLUE}========================================${NC}"

cd backend
if uv run pytest --cov=src --cov-report=html --cov-report=term; then
    echo -e "${GREEN}✅ Backend tests passed${NC}\n"
else
    echo -e "${RED}❌ Backend tests failed${NC}\n"
    exit 1
fi
cd ..

# Frontend Tests
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}⚛️  Running Frontend Tests${NC}"
echo -e "${BLUE}========================================${NC}"

cd frontend
if npm run test:run -- --coverage --watchAll=false; then
    echo -e "${GREEN}✅ Frontend tests passed${NC}\n"
else
    echo -e "${RED}❌ Frontend tests failed${NC}\n"
    exit 1
fi
cd ..

# E2E Tests - Basic
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}🌐 Running E2E Tests (Basic)${NC}"
echo -e "${BLUE}========================================${NC}"

if npx playwright test e2e-deck-basic --reporter=line; then
    echo -e "${GREEN}✅ E2E basic tests passed${NC}\n"
else
    echo -e "${RED}❌ E2E basic tests failed${NC}\n"
    exit 1
fi

# E2E Tests - Essential
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}🌐 Running E2E Tests (Essential)${NC}"
echo -e "${BLUE}========================================${NC}"

if npx playwright test e2e-essential --reporter=line; then
    echo -e "${GREEN}✅ E2E essential tests passed${NC}\n"
else
    echo -e "${RED}❌ E2E essential tests failed${NC}\n"
    exit 1
fi

# Summary
echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}✅ All Tests Passed!${NC}"
echo -e "${BLUE}========================================${NC}\n"

echo -e "${YELLOW}📊 Coverage Reports:${NC}"
echo -e "  Backend:  ${BLUE}backend/htmlcov/index.html${NC}"
echo -e "  Frontend: ${BLUE}frontend/coverage/lcov-report/index.html${NC}"
echo -e "\n${YELLOW}📈 Test Report:${NC}"
echo -e "  Playwright: ${BLUE}npx playwright show-report${NC}\n"

exit 0
