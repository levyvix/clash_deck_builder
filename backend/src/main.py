# backend/src/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from .utils.config import settings
from .utils.database import initialize_database, initialize_schema, close_database
from .api import cards, decks
from .exceptions.handlers import EXCEPTION_HANDLERS


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    print(f"Starting {settings.app_name} v{settings.app_version}")
    print(f"Debug mode: {settings.debug}")
    
    try:
        # Initialize database connection pool
        initialize_database()
        print("Database connection pool initialized")
        
        # Initialize database schema
        initialize_schema()
        print("Database schema initialized")
        
    except Exception as e:
        print(f"Warning: Failed to initialize database: {e}")
        if settings.debug:
            print("Running in debug mode - continuing without database")
        else:
            print("Database initialization failed in production mode")
            raise
    
    yield
    
    # Shutdown
    print("Shutting down application")
    try:
        close_database()
        print("Database connections closed")
    except Exception as e:
        print(f"Warning: Error closing database connections: {e}")


def create_app() -> FastAPI:
    """FastAPI application factory."""
    
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        debug=settings.debug,
        lifespan=lifespan
    )
    
    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE"],
        allow_headers=["*"],
    )
    
    # Register exception handlers
    for exception_class, handler in EXCEPTION_HANDLERS.items():
        app.add_exception_handler(exception_class, handler)
    
    # Register API routers
    app.include_router(cards.router, prefix="/cards", tags=["cards"])
    app.include_router(decks.router, prefix="/decks", tags=["decks"])
    
    @app.get("/")
    async def root():
        """Root endpoint for health check."""
        return {
            "message": f"Welcome to {settings.app_name}",
            "version": settings.app_version,
            "status": "healthy"
        }
    
    @app.get("/health")
    async def health_check():
        """Health check endpoint."""
        return {"status": "healthy", "version": settings.app_version}
    
    return app


# Create the FastAPI application instance
app = create_app()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    )