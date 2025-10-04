# Agent Guidelines for Clash Deck Builder

This document outlines essential commands and style guidelines for agentic coding in this repository.

## 1. Build/Lint/Test Commands

### Frontend (React/TypeScript)
- **Install Dependencies:** `npm install` (in `frontend/`)
- **Build:** `npm run build` (in `frontend/`)
- **Run Tests:** `npm test` (interactive), `npm run test:run` (single run) (in `frontend/`)
- **Lint:** ESLint is configured via `package.json`. Lint errors appear during `npm start`.

### Backend (Python/FastAPI)
- **Run Tests:** `uv run pytest` (in `backend/`). To run a single test file: `uv run pytest <path/to/test_file.py>`
- **Lint:** `flake8` (run with `uvx run flake8 .` in `backend/`)
- **Format:** `black` (run with `uvx run black .` in `backend/`)

## 2. Code Style Guidelines

### General
- **Formatting:** Adhere to existing formatting (Prettier for frontend, Black for Python).
- **Naming:** Follow conventional naming for variables, functions, classes (e.g., `camelCase` for JS/TS, `snake_case` for Python).
- **Error Handling:** Implement robust error handling, especially for API calls and external interactions.

### Frontend (React/TypeScript)
- **Imports:** Prefer absolute imports where configured (e.g., from `src/`).
- **Types:** Use TypeScript types consistently for clarity and maintainability.

### Backend (Python/FastAPI)
- **Imports:** Prefer absolute imports from the `src` directory.
- **Types:** Use Python type hints for function signatures and variable annotations.
