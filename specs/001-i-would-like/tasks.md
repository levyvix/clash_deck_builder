# Tasks: Clash Royale Deck Builder

**Input**: Design documents from `/specs/001-i-would-like/`
**Prerequisites**: plan.md (required), research.md, data-model.md, contracts/

## Execution Flow (main)
```
1. Load plan.md from feature directory
   → If not found: ERROR "No implementation plan found"
   → Extract: tech stack, libraries, structure
2. Load optional design documents:
   → data-model.md: Extract entities → model tasks
   → contracts/: Each file → contract test task
   → research.md: Extract decisions → setup tasks
3. Generate tasks by category:
   → Setup: project init, dependencies, linting
   → Tests: contract tests, integration tests
   → Core: models, services, CLI commands
   → Integration: DB, middleware, logging
   → Polish: unit tests, performance, docs
4. Apply task rules:
   → Different files = mark [P] for parallel
   → Same file = sequential (no [P])
   → Tests before implementation (TDD)
5. Number tasks sequentially (T001, T002...)
6. Generate dependency graph
7. Create parallel execution examples
8. Validate task completeness:
   → All contracts have tests?
   → All entities have models?
   → All endpoints implemented?
9. Return: SUCCESS (tasks ready for execution)
```

## Format: `[ID] [P?] Description`
- **[P]**: Can run in parallel (different files, no dependencies)
- Include exact file paths in descriptions

## Path Conventions
- **Single project**: `src/`, `tests/` at repository root
- **Web app**: `backend/src/`, `frontend/src/`
- **Mobile**: `api/src/`, `ios/src/` or `android/src/`
- Paths shown below assume single project - adjust based on plan.md structure

## Phase 3.1: Setup
- [X] T001 Create project structure for `backend/` and `frontend/` directories.
- [X] T002 Initialize Python backend project with chosen framework (e.g., FastAPI/Flask) and UV.
- [X] T003 Initialize JavaScript/TypeScript frontend project with chosen framework (e.g., React/Vue/Svelte).
- [X] T004 [P] Configure linting and formatting tools for Python (e.g., Black, Flake8).
- [X] T005 [P] Configure linting and formatting tools for JavaScript/TypeScript (e.g., ESLint, Prettier).
- [X] T006 Set up MySQL database connection and initial schema.

## Phase 3.2: Tests First (TDD) ⚠️ MUST COMPLETE BEFORE 3.3
**CRITICAL: These tests MUST be written and MUST FAIL before ANY implementation**
- [X] T007 [P] Write contract test for backend API to fetch cards from Clash Royale API in `backend/tests/contract/test_clash_api.py`.
- [X] T008 [P] Write contract test for backend API to create a deck in `backend/tests/contract/test_decks_create.py`.
- [X] T009 [P] Write contract test for backend API to retrieve a deck in `backend/tests/contract/test_decks_get.py`.
- [X] T010 [P] Write contract test for backend API to update a deck in `backend/tests/contract/test_decks_update.py`.
- [X] T011 [P] Write contract test for backend API to delete a deck in `backend/tests/contract/test_decks_delete.py`.
- [X] T012 [P] Write integration test for "Build, Save, Retrieve, and Delete a Deck" scenario in `frontend/tests/integration/test_deck_workflow.py`.

## Phase 3.3: Core Implementation (ONLY after tests are failing)
- [X] T013 [P] Implement Card data model in `backend/src/models/card.py`.
- [X] T014 [P] Implement Deck data model in `backend/src/models/deck.py`.
- [X] T015 [P] Implement User data model in `backend/src/models/user.py`.
- [X] T016 Implement Clash Royale API service in `backend/src/services/clash_api_service.py`.
- [X] T017 Implement Deck management service (CRUD operations) in `backend/src/services/deck_service.py`.
- [X] T018 Implement backend API endpoint for fetching cards in `backend/src/api/cards.py`.
- [X] T019 Implement backend API endpoint for creating decks in `backend/src/api/decks.py`.
- [X] T020 Implement backend API endpoint for retrieving decks in `backend/src/api/decks.py`.
- [X] T021 Implement backend API endpoint for updating decks in `backend/src/api/decks.py`.
- [X] T022 Implement backend API endpoint for deleting decks in `backend/src/api/decks.py`.
- [X] T023 Implement frontend card display component in `frontend/src/components/CardDisplay.vue` or `.jsx`.
- [X] T024 Implement frontend card filtering logic and UI in `frontend/src/components/CardFilters.vue` or `.jsx`.
- [X] T025 Implement frontend deck builder component in `frontend/src/components/DeckBuilder.vue` or `.jsx`.
- [X] T026 Implement frontend saved decks list component in `frontend/src/components/SavedDecks.vue` or `.jsx`.
- [X] T027 Implement frontend routing and main application layout in `frontend/src/App.vue` or `.jsx`.

## Phase 3.4: Integration
- [X] T028 Connect backend Deck service to MySQL database.
- [X] T029 Integrate frontend with backend API for card fetching.
- [X] T030 Integrate frontend with backend API for deck management.
- [X] T031 Implement error handling for API calls (frontend and backend).
- [X] T032 Implement UI for displaying API errors.

## Phase 3.5: Polish
- [X] T033 [P] Write unit tests for backend data models.
- [X] T034 [P] Write unit tests for backend services.
- [X] T035 [P] Write unit tests for frontend components.
- [X] T036 Implement performance optimizations (if needed, based on research).
- [X] T037 Update `docs/api.md` with backend API documentation.
- [X] T038 Update `README.md` with setup and usage instructions.

## Dependencies
- Setup (T001-T006) before Tests (T007-T012)
- Tests (T007-T012) before Core Implementation (T013-T027)
- Core Implementation (T013-T027) before Integration (T028-T032)
- Integration (T028-T032) before Polish (T033-T038)
- T013, T014, T015 block T017, T019, T020, T021, T022, T028
- T016 blocks T018, T029
- T017 blocks T019, T020, T021, T022, T028, T030
- T018 blocks T023, T024, T029
- T019, T020, T021, T022 block T025, T026, T030

## Parallel Example
```
# Launch T004-T005 together:
Task: "Configure linting and formatting tools for Python (e.g., Black, Flake8)"
Task: "Configure linting and formatting tools for JavaScript/TypeScript (e.g., ESLint, Prettier)"

# Launch T007-T012 together:
Task: "Write contract test for backend API to fetch cards from Clash Royale API in `backend/tests/contract/test_clash_api.py`."
Task: "Write contract test for backend API to create a deck in `backend/tests/contract/test_decks_create.py`."
Task: "Write contract test for backend API to retrieve a deck in `backend/tests/contract/test_decks_get.py`."
Task: "Write contract test for backend API to update a deck in `backend/tests/contract/test_decks_update.py`."
Task: "Write contract test for backend API to delete a deck in `backend/tests/contract/test_decks_delete.py`."
Task: "Write integration test for "Build, Save, Retrieve, and Delete a Deck" scenario in `frontend/tests/integration/test_deck_workflow.py`."

# Launch T013-T015 together:
Task: "Implement Card data model in `backend/src/models/card.py`."
Task: "Implement Deck data model in `backend/src/models/deck.py`."
Task: "Implement User data model in `backend/src/models/user.py`."

# Launch T033-T035 together:
Task: "Write unit tests for backend data models."
Task: "Write unit tests for backend services."
Task: "Write unit tests for frontend components."
```

## Notes
- [P] tasks = different files, no dependencies
- Verify tests fail before implementing
- Commit after each task
- Avoid: vague tasks, same file conflicts

## Task Generation Rules
*Applied during main() execution*

1. **From Contracts**:
   - Each contract file → contract test task [P]
   - Each endpoint → implementation task
   
2. **From Data Model**:
   - Each entity → model creation task [P]
   - Relationships → service layer tasks
   
3. **From User Stories**:
   - Each story → integration test [P]
   - Quickstart scenarios → validation tasks

4. **Ordering**:
   - Setup → Tests → Models → Services → Endpoints → Polish
   - Dependencies block parallel execution

## Validation Checklist
*GATE: Checked by main() before returning*

- [ ] All contracts have corresponding tests
- [ ] All entities have model tasks
- [ ] All tests come before implementation
- [ ] Parallel tasks truly independent
- [ ] Each task specifies exact file path
- [ ] No task modifies same file as another [P] task
