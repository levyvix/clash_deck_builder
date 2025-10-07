# Clash Royale Deck Builder

Welcome to the Clash Royale Deck Builder documentation! This is a web application for building and managing Clash Royale decks with card filtering, deck persistence, and Google OAuth authentication.

## Core Features

- **Deck Building**: Interactive drag-and-drop interface for creating decks
- **Evolution Cards**: Support for up to 2 evolution card slots per deck
- **Card Filtering**: Advanced filtering by rarity, type, elixir cost, and more
- **Deck Management**: Save up to 20 decks per authenticated user
- **Anonymous Mode**: Build decks without authentication using localStorage
- **Google OAuth**: Seamless authentication with Google Sign-In
- **Real-time Calculations**: Automatic average elixir cost calculation
- **Responsive Design**: Works on desktop and mobile devices

## Core Business Rules

- Maximum **20 saved decks** per user
- Decks support up to **2 evolution card slots**
- **Real-time average elixir calculation**
- All deck data persists in **MySQL database**

## Technology Stack

### Backend
- **Python 3.11+** with **UV package manager**
- **FastAPI** with Uvicorn ASGI server
- **MySQL 8.0** database
- **httpx** for external API calls
- **pytest** for testing

### Frontend
- **React 19.2+** with TypeScript
- **React Router DOM** for routing
- **Jest + React Testing Library** for testing

### External Integrations
- **Clash Royale API** for card data
- **Google OAuth** for user authentication

## Quick Links

- [Quick Start Guide](getting-started/quickstart.md) - Get up and running quickly
- [Environment Setup](getting-started/environment-setup.md) - Configure your development environment
- [Architecture Overview](architecture/overview.md) - Understand the system design
- [API Reference](api/overview.md) - Backend API documentation
- [Development Guide](development/backend.md) - Learn how to contribute

## Project Structure

```
clash_deck_builder/
├── backend/           # Python FastAPI backend
├── frontend/          # React TypeScript frontend
├── database/          # MySQL schema and migrations
├── docs/             # This documentation
└── docker-compose.yml # Container orchestration
```

## Getting Help

- Check the [Troubleshooting Guide](operations/troubleshooting.md)
- Review the [Development Workflow](getting-started/workflow.md)
- See [Common Development Patterns](development/backend.md#common-patterns)

## Contributing

This project follows a standard branching strategy:
- Main branch: `main`
- Feature branches created from `main`
- PRs merge back into `main`

See [Development Workflow](getting-started/workflow.md) for details.
