# Implementation Plan: Clash Royale Deck Builder

**Branch**: `001-i-would-like` | **Date**: 2025-10-02 | **Spec**: C:\Users\enio\Documents\projetos\clash_deck_builder\specs\001-i-would-like\spec.md
**Input**: Feature specification from `C:\Users\enio\Documents\projetos\clash_deck_builder\specs\001-i-would-like\spec.md`

## Execution Flow (/plan command scope)
```
1. Load feature spec from Input path
   → If not found: ERROR "No feature spec at {path}"
2. Fill Technical Context (scan for NEEDS CLARIFICATION)
   → Detect Project Type from file system structure or context (web=frontend+backend, mobile=app+api)
   → Set Structure Decision based on project type
3. Fill the Constitution Check section based on the content of the constitution document.
4. Evaluate Constitution Check section below
   → If violations exist: Document in Complexity Tracking
   → If no justification possible: ERROR "Simplify approach first"
   → Update Progress Tracking: Initial Constitution Check
5. Execute Phase 0 → research.md
   → If NEEDS CLARIFICATION remain: ERROR "Resolve unknowns"
6. Execute Phase 1 → contracts, data-model.md, quickstart.md, agent-specific template file (e.g., `CLAUDE.md` for Claude Code, `.github/copilot-instructions.md` for GitHub Copilot, `GEMINI.md` for Gemini CLI, `QWEN.md` for Qwen Code or `AGENTS.md` for opencode).
7. Re-evaluate Constitution Check section
   → If new violations: Refactor design, return to Phase 1
   → Update Progress Tracking: Post-Design Constitution Check
8. Plan Phase 2 → Describe task generation approach (DO NOT create tasks.md)
9. STOP - Ready for /tasks command
```

**IMPORTANT**: The /plan command STOPS at step 7. Phases 2-4 are executed by other commands:
- Phase 2: /tasks command creates tasks.md
- Phase 3-4: Implementation execution (manual or via tools)

## Summary
Build a Clash Royale deck builder with a simple Material Design UI. The web application will display all cards from the Clash Royale API, allowing users to filter by various criteria. Users can build, save, rename, and delete up to 20 decks, with support for two evolution card slots and average elixir calculation. Decks will be persisted in a MySQL database.

## Technical Context
**Language/Version**: Python 3.x (Backend), JavaScript/TypeScript (Frontend)  
**Primary Dependencies**: Clash Royale API client, MySQL client, Python Web Framework (e.g., FastAPI/Flask), Frontend Framework (e.g., React/Vue/Svelte), UV  
**Storage**: MySQL  
**Testing**: pytest (Python), Frontend testing framework (e.g., Jest/Vitest)  
**Target Platform**: Web (Browser, Server)  
**Project Type**: Web (frontend + backend)  
**Performance Goals**: NEEDS CLARIFICATION (e.g., page load times, API response times)  
**Constraints**: Clash Royale API key required, all cards level 11, 2 evo spots per deck, max 20 saved decks.  
**Scale/Scope**: Single user, up to 20 saved decks.

## Constitution Check
*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **I. Clean and Modular Code**: Design will prioritize clear separation of concerns (e.g., API client, data models, UI components, database interactions).
- **II. Python 3 Best Practices**: All Python code will adhere to PEP 8, use type hints, and follow modern Pythonic patterns.
- **III. UV for Dependency Management and Execution**: All Python dependencies will be managed with UV, and Python code will be executed via `uv run`.

## Project Structure

### Documentation (this feature)
```
specs/[###-feature]/
├── plan.md              # This file (/plan command output)
├── research.md          # Phase 0 output (/plan command)
├── data-model.md        # Phase 1 output (/plan command)
├── quickstart.md        # Phase 1 output (/plan command)
├── contracts/           # Phase 1 output (/plan command)
└── tasks.md             # Phase 2 output (/tasks command - NOT created by /plan)
```

### Source Code (repository root)
```
backend/
├── src/
│   ├── api/             # Backend API endpoints
│   ├── models/          # Database models, data structures
│   ├── services/        # Business logic, Clash Royale API interaction
│   └── utils/           # Utility functions
└── tests/
    ├── unit/
    └── integration/

frontend/
├── src/
│   ├── components/      # Reusable UI components
│   ├── pages/           # Application pages/views
│   ├── services/        # Frontend data fetching, state management
│   └── utils/           # Frontend utility functions
└── tests/
    ├── unit/
    └── integration/
```

**Structure Decision**: Web application with separate `backend` and `frontend` directories.

## Phase 0: Outline & Research
1. **Extract unknowns from Technical Context** above:
   - For each NEEDS CLARIFICATION → research task
   - For each dependency → best practices task
   - For each integration → patterns task

2. **Generate and dispatch research agents**:
   - Task: "Research typical performance expectations for a web-based deck builder (e.g., page load times, API response times)."
   - Task: "Research best practices for integrating with external APIs (Clash Royale API)."
   - Task: "Research best practices for MySQL database design for deck storage."
   - Task: "Research suitable Python web frameworks (FastAPI/Flask) and frontend frameworks (React/Vue/Svelte) that align with Material Design and 'simple UI'."

3. **Consolidate findings** in `research.md` using format:
   - Decision: [what was chosen]
   - Rationale: [why chosen]
   - Alternatives considered: [what else evaluated]

**Output**: research.md with all NEEDS CLARIFICATION resolved

## Phase 1: Design & Contracts
*Prerequisites: research.md complete*

1. **Extract entities from feature spec** → `data-model.md`:
   - Entity name, fields, relationships
   - Validation rules from requirements
   - State transitions if applicable

2. **Generate API contracts** from functional requirements:
   - Backend API for managing decks (create, read, update, delete).
   - Backend API for proxying Clash Royale API calls (e.g., `/api/cards`).
   - Use standard REST patterns.
   - Output OpenAPI schema to `/contracts/`.

3. **Generate contract tests** from contracts:
   - One test file per backend API endpoint.
   - Assert request/response schemas.
   - Tests must fail (no implementation yet).

4. **Extract test scenarios** from user stories:
   - Each story → integration test scenario.
   - Quickstart test = story validation steps (e.g., Build a deck, save it, retrieve it, delete it).

5. **Update agent file incrementally** (O(1) operation):
   - Run `.specify/scripts/powershell/update-agent-context.ps1 -AgentType gemini`
     **IMPORTANT**: Execute it exactly as specified above. Do not add or remove any arguments.
   - If exists: Add only NEW tech from current plan
   - Preserve manual additions between markers
   - Update recent changes (keep last 3)
   - Keep under 150 lines for token efficiency
   - Output to repository root

**Output**: data-model.md, /contracts/*, failing tests, quickstart.md, agent-specific file

## Phase 2: Task Planning Approach
*This section describes what the /tasks command will do - DO NOT execute during /plan*

**Task Generation Strategy**:
- Load `.specify/templates/tasks-template.md` as base
- Generate tasks from Phase 1 design docs (contracts, data model, quickstart), `spec.md` (functional requirements, entities), and constitution (principles).
- Each contract → contract test task [P]
- Each entity → model creation task [P] 
- Each user story → integration test task
- Implementation tasks to make tests pass

**Ordering Strategy**:
- TDD order: Tests before implementation 
- Dependency order: Models before services before UI (Backend before Frontend)
- Mark [P] for parallel execution (independent files)

**Estimated Output**: 30-40 numbered, ordered tasks in tasks.md

**IMPORTANT**: This phase is executed by the /tasks command, NOT by /plan

## Phase 3+: Future Implementation
*These phases are beyond the scope of the /plan command*

**Phase 3**: Task execution (/tasks command creates tasks.md)  
**Phase 4**: Implementation (execute tasks.md following constitutional principles)  
**Phase 5**: Validation (run tests, execute quickstart.md, performance validation)

## Complexity Tracking
*Fill ONLY if Constitution Check has violations that must be justified*

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |


## Progress Tracking
*This checklist is updated during execution flow*

**Phase Status**:
- [X] Phase 0: Research complete (/plan command)
- [X] Phase 1: Design complete (/plan command)
- [ ] Phase 2: Task planning complete (/plan command - describe approach only)
- [ ] Phase 3: Tasks generated (/tasks command)
- [ ] Phase 4: Implementation complete
- [ ] Phase 5: Validation passed

**Gate Status**:
- [X] Initial Constitution Check: PASS
- [X] Post-Design Constitution Check: PASS
- [ ] All NEEDS CLARIFICATION resolved
- [ ] Complexity deviations documented

---
*Based on Constitution v1.1.0 - See `C:\Users\enio\Documents\projetos\clash_deck_builder\.specify\memory\constitution.md`*