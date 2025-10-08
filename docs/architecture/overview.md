# Architecture Overview

The Clash Royale Deck Builder follows a three-tier architecture with clear separation between presentation, business logic, and data layers.

## System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     Frontend (React)                     │
│                                                          │
│  ┌────────────┐  ┌────────────┐  ┌─────────────┐      │
│  │ Components │  │  Contexts  │  │  Services   │      │
│  └────────────┘  └────────────┘  └─────────────┘      │
└────────────────────────┬─────────────────────────────────┘
                        │ HTTP/REST
                        │
┌────────────────────────▼─────────────────────────────────┐
│                  Backend (FastAPI)                       │
│                                                          │
│  ┌────────────┐  ┌───────────┐  ┌────────┐  ┌────────────┐ │
│  │ API/Routes │→ │ Services  │→ │ Models │→ │  Database  │ │
│  └────────────┘  └───────────┘  └────────┘  └────────────┘ │
└────────────────────────┬─────────────────────────────────┘
                        │
┌────────────────────────▼─────────────────────────────────┐
│                   MySQL Database                         │
│                                                          │
│  ┌───────┐  ┌───────┐  ┌───────┐  ┌────────────┐      │
│  │ users │  │ cards │  │ decks │  │ deck_cards │      │
│  └───────┘  └───────┘  └───────┘  └────────────┘      │
└──────────────────────────────────────────────────────────┘
```

## Core Components

### Frontend Layer

**Technology**: React 19.2+ with TypeScript

**Responsibilities**:
- User interface rendering
- Client-side state management
- API communication
- Client-side validation
- Anonymous deck storage (localStorage)

**Key Patterns**:
- Component-based architecture
- React Hooks for state management
- Context API for global state (Auth, Onboarding)
- Service layer for business logic
- TypeScript for type safety

See [Frontend Architecture](frontend.md) for details.

### Backend Layer

**Technology**: Python 3.11+ with FastAPI

**Responsibilities**:
- API endpoint handling
- Business logic processing
- Authentication and authorization
- Data validation
- Database operations
- External API integration

**Key Patterns**:
- Layered architecture (API → Services → Models)
- Dependency injection
- Pydantic models for validation
- Async/await for I/O operations

See [Backend Architecture](backend.md) for details.

### Data Layer

**Technology**: MySQL 8.0

**Responsibilities**:
- Persistent data storage
- Data integrity enforcement
- Relational data management
- Query optimization

**Key Features**:
- Normalized schema design
- Foreign key constraints
- Indexes for performance
- Migration system for schema evolution

See [Database Architecture](database.md) for details.

## Data Flow

### Deck Creation Flow

```
1. User builds deck in UI
   ↓
2. Frontend validates deck (8 cards, max 2 evolutions)
   ↓
3. Frontend transforms to backend format
   {
     name: "My Deck",
     cards: [Card, Card, ...],
     evolution_slots: [Card, Card]
   }
   ↓
4. POST /api/decks with JWT token
   ↓
5. Backend validates request
   ↓
6. DeckService creates deck record
   ↓
7. Database stores deck + deck_cards entries
   ↓
8. Backend returns created deck
   ↓
9. Frontend transforms to component format
   {
     id: 123,
     name: "My Deck",
     slots: [{card: Card, isEvolution: false}, ...]
   }
   ↓
10. UI updates to show saved deck
```

### Authentication Flow

```
1. User clicks "Sign in with Google"
   ↓
2. Google OAuth popup opens
   ↓
3. User authenticates with Google
   ↓
4. Google returns credential token
   ↓
5. Frontend sends token to POST /api/auth/google
   ↓
6. Backend validates token with Google
   ↓
7. Backend creates/updates user in database
   ↓
8. Backend generates JWT access + refresh tokens
   ↓
9. Frontend stores tokens in localStorage
   ↓
10. Frontend sets AuthContext state
    ↓
11. UI updates to authenticated state
    ↓
12. Future API calls include "Authorization: Bearer {token}"
```

## Communication Patterns

### Frontend ↔ Backend

**Protocol**: HTTP/REST over JSON

**Authentication**: JWT Bearer tokens

**Endpoints**:
- `/api/auth/*` - Authentication
- `/api/cards/*` - Card data
- `/api/decks/*` - Deck management
- `/api/profile/*` - User profile

**Error Handling**:
- Backend returns standardized error responses
- Frontend service layer handles retries and errors
- User-friendly error messages displayed in UI

### Backend ↔ Database

**Protocol**: MySQL Protocol via mysql-connector-python

**Connection**: Connection pooling via `db_manager`

**Pattern**: Direct SQL queries (not ORM)

**Transactions**: Used for multi-step operations (deck creation)

### Backend ↔ External APIs

**Clash Royale API**:
- Used for card data ingestion
- Cached in local database
- Periodic sync via script

**Google OAuth**:
- Token validation during login
- User profile data retrieval

## Key Architectural Decisions

### Why FastAPI?

- **Performance**: ASGI-based, async support
- **Developer Experience**: Auto-generated docs, type hints
- **Validation**: Built-in Pydantic models
- **Modern**: Native async/await support

### Why React 19.2+?

- **Component Model**: Reusable, testable components
- **TypeScript**: Type safety and better IDE support
- **Ecosystem**: Rich library ecosystem
- **Performance**: Virtual DOM, optimizations

### Why MySQL?

- **Reliability**: Mature, battle-tested RDBMS
- **Performance**: Good for read-heavy workloads
- **Features**: Full ACID compliance, strong consistency
- **Familiarity**: Wide adoption, good tooling

### Why Not SQLAlchemy?

- **Simplicity**: Direct SQL is clearer for this use case
- **Performance**: No ORM overhead
- **Control**: Full control over queries
- **Learning**: Easier for team without ORM experience

### Why UV Package Manager?

- **Speed**: 10-100x faster than pip
- **Reliability**: Better dependency resolution
- **Modern**: Built in Rust, actively maintained
- **Simplicity**: Single tool for all Python workflows

## Scalability Considerations

### Current State (Single Server)

```
Frontend (nginx) → Backend (uvicorn) → MySQL
```

**Limitations**:
- Single point of failure
- Limited by single server resources
- No horizontal scaling

### Future Scaling Path

**Phase 1: Database Scaling**
```
Frontend → Backend → MySQL Primary
                   ↓
                 MySQL Replicas (read)
```

**Phase 2: Backend Scaling**
```
Frontend → Load Balancer → Backend 1 → MySQL
                        ↓→ Backend 2 → MySQL
                        ↓→ Backend 3 → MySQL
```

**Phase 3: Caching Layer**
```
Frontend → Backend → Redis Cache → MySQL
```

**Phase 4: CDN for Frontend**
```
User → CDN (static assets) → Origin Server
    ↓
    API Server → Backend Services
```

## Security Architecture

### Authentication

- Google OAuth for identity
- JWT tokens for sessions
- Refresh token rotation
- Secure token storage (httpOnly cookies recommended)

### Authorization

- User-scoped resources (decks belong to users)
- JWT claims for user identification
- Backend validates all operations

### Data Protection

- Password hashing (for future non-OAuth users)
- SQL injection prevention (parameterized queries)
- XSS protection (React's built-in escaping)
- CORS configuration

### API Security

- HTTPS in production (terminate at load balancer)
- Rate limiting (future enhancement)
- Input validation (Pydantic models)
- Error messages don't leak sensitive data

## Technology Constraints

### Must Use

- **Python 3.11+** (backend compatibility)
- **React 19.2+** (frontend features)
- **MySQL 8.0** (database compatibility)
- **UV** (package management)

### Must Avoid

- SQLAlchemy or other ORMs
- pip/poetry for Python packages
- Class components in React (use functional + hooks)

## Related Documentation

- [Backend Architecture](backend.md) - Detailed backend structure
- [Frontend Architecture](frontend.md) - Detailed frontend structure
- [Database Architecture](database.md) - Database schema and design
- [API Reference](../api/overview.md) - API endpoints and contracts
