# System Architecture

This document provides an overview of the Clash Royale Deck Builder's system architecture, components, and their interactions.

## High-Level Architecture

```mermaid
graph TD
    A[Frontend] <-->|HTTPS| B[API Gateway]
    B <--> C[Auth Service]
    B <--> D[Deck Service]
    B <--> E[Card Service]
    D <--> F[(MySQL Database)]
    E <--> G[Clash Royale API]
    E <--> H[Redis Cache]
```

## Core Components

### 1. Frontend (React)
- **Purpose**: User interface for deck building and management
- **Technologies**:
  - React 19.2+
  - TypeScript
  - React Router DOM
  - Redux for state management
  - Styled Components

### 2. Backend Services (FastAPI)

#### API Gateway
- **Purpose**: Entry point for all client requests
- **Responsibilities**:
  - Request routing
  - Authentication/Authorization
  - Rate limiting
  - Request/Response validation

#### Auth Service
- **Purpose**: Handle user authentication and authorization
- **Features**:
  - Google OAuth integration
  - JWT token generation/validation
  - User session management

#### Deck Service
- **Purpose**: Manage deck-related operations
- **Features**:
  - CRUD operations for decks
  - Deck validation
  - Average elixir calculation
  - Evolution card management

#### Card Service
- **Purpose**: Provide card data and metadata
- **Features**:
  - Card data retrieval
  - Caching layer
  - Card filtering and search

## Data Flow

### Deck Creation Flow
```mermaid
sequenceDiagram
    participant U as User
    participant F as Frontend
    participant A as API Gateway
    participant D as Deck Service
    participant DB as Database
    
    U->>F: Creates deck
    F->>A: POST /api/decks
    A->>A: Validate JWT
    A->>D: Forward request
    D->>D: Validate deck
    D->>DB: Save deck
    DB-->>D: Confirm save
    D-->>A: Return created deck
    A-->>F: 201 Created
    F-->>U: Show success
```

### Card Data Flow
```mermaid
sequenceDiagram
    participant U as User
    participant F as Frontend
    participant A as API Gateway
    participant C as Card Service
    participant R as Redis
    participant CR as Clash Royale API
    
    U->>F: View cards
    F->>A: GET /api/cards
    A->>C: Forward request
    C->>R: Check cache
    alt Cache hit
        R-->>C: Return cached data
    else Cache miss
        C->>CR: Fetch cards
        CR-->>C: Return cards
        C->>R: Cache response
    end
    C-->>A: Return cards
    A-->>F: 200 OK
    F-->>U: Display cards
```

## Data Storage

### MySQL Database
- **Schema**:
  ```sql
  -- Users table
  CREATE TABLE users (
      id INT AUTO_INCREMENT PRIMARY KEY,
      google_id VARCHAR(255) UNIQUE,
      email VARCHAR(255) UNIQUE,
      name VARCHAR(255),
      avatar TEXT,
      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
      updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
  );

  -- Decks table
  CREATE TABLE decks (
      id INT AUTO_INCREMENT PRIMARY KEY,
      user_id INT,
      name VARCHAR(100),
      cards JSON,
      evolutions JSON,
      average_elixir FLOAT,
      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
      updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
      FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
  );
  ```

### Redis Cache
- **Purpose**: Improve performance for frequently accessed data
- **Cached Data**:
  - Card data (24-hour TTL)
  - User sessions
  - Rate limiting counters

## Security

### Authentication
- JWT-based authentication
- Google OAuth 2.0 integration
- Secure token storage (HTTP-only cookies)

### Authorization
- Role-based access control (RBAC)
- Resource ownership validation
- Rate limiting per IP/User

### Data Protection
- All sensitive data encrypted at rest
- HTTPS for all communications
- Input validation and sanitization
- CORS policy enforcement

## Performance Considerations

### Caching Strategy
- Client-side caching (browser cache)
- Server-side caching (Redis)
- ETag support for efficient cache validation

### Database Optimization
- Indexes on frequently queried fields
- Connection pooling
- Query optimization

## Monitoring and Logging

### Logging
- Structured logging with log levels
- Request/Response logging
- Error tracking

### Monitoring
- Health check endpoints
- Performance metrics
- Error tracking integration

## Deployment Architecture

### Development
- Local development with Docker Compose
- Hot-reload for frontend and backend
- Local MySQL and Redis instances

### Production
- Containerized deployment with Docker
- Load balancing
- Auto-scaling
- Database replication
- CDN for static assets

## Future Considerations

### Scalability
- Database sharding
- Read replicas
- Microservices architecture

### Features
- Real-time deck sharing
- Deck win-rate tracking
- AI-powered deck suggestions
- Tournament support
