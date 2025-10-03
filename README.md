# Clash Royale Deck Builder

This project implements a Clash Royale deck builder with a simple UI, allowing users to build, save, and manage their decks.

## Features
- Display all Clash Royale cards with correct rarity and formatting.
- Filter cards by elixir, name, rarity, arena, and type.
- Build decks with up to 2 evolution card slots and average elixir calculation.
- Save, rename, and delete up to 20 decks.
- Persistence of decks in a MySQL database.

## Setup and Installation

### Prerequisites
- Python 3.x
- Node.js and npm
- MySQL database
- Clash Royale API Key

### Backend Setup
1.  Navigate to the `backend` directory:
    ```bash
    cd backend
    ```
2.  Install Python dependencies using UV:
    ```bash
    uv install
    ```
3.  Configure your MySQL database connection in `backend/src/utils/config.py`.
4.  Apply the initial database schema:
    ```bash
    # Execute the SQL in backend/src/models/schema.sql in your MySQL client
    ```
5.  Set your Clash Royale API key as an environment variable or directly in `backend/src/services/clash_api_service.py`.

### Frontend Setup
1.  Navigate to the `frontend` directory:
    ```bash
    cd frontend
    ```
2.  Install Node.js dependencies:
    ```bash
    npm install
    ```
3.  Set the backend API base URL in `frontend/.env` (e.g., `REACT_APP_API_BASE_URL=http://localhost:8000`).

## Running the Application

### Start Backend
1.  Navigate to the `backend` directory:
    ```bash
    cd backend
    ```
2.  Run the FastAPI application:
    ```bash
    uv run uvicorn main:app --reload
    ```
    (You might need to create a `main.py` file that imports your API routers)

### Start Frontend
1.  Navigate to the `frontend` directory:
    ```bash
    cd frontend
    ```
2.  Start the React development server:
    ```bash
    npm start
    ```

## Development

### Linting and Formatting
- **Python**: `uv run black .` and `uv run flake8 .`
- **JavaScript/TypeScript**: `npm run lint` (or similar, configured by create-react-app)

### Testing
- **Python**: `uv run pytest`
- **JavaScript/TypeScript**: `npm test`
