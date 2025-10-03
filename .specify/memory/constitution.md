<!--
Version change: 1.0.0 -> 1.1.0
List of modified principles:
- III. UV for Dependency Management and Execution (New)
Added sections: None
Removed sections: None
Templates requiring updates:
- .specify/templates/plan-template.md: ⚠ pending (Constitution Check section needs to be updated to reflect new principles)
- .specify/templates/spec-template.md: ✅ updated
- .specify/templates/tasks-template.md: ✅ updated
- .gemini/commands/analyze.toml: ✅ updated
- .gemini/commands/clarify.toml: ✅ updated
- .gemini/commands/implement.toml: ✅ updated
- .gemini/commands/plan.toml: ✅ updated
- .gemini/commands/specify.toml: ✅ updated
- .gemini/commands/tasks.toml: ✅ updated
Follow-up TODOs: None
-->
# clash_deck_builder Constitution

## Core Principles

### I. Clean and Modular Code
All code MUST be written to be clean, readable, and modular. Modules MUST have a single responsibility and well-defined interfaces. This promotes reusability, testability, and maintainability.

### II. Python 3 Best Practices
All Python code MUST adhere to Python 3 best practices, including PEP 8 for style, appropriate use of type hints, and modern Pythonic constructs. This ensures consistency, quality, and leverages the full capabilities of the language.

### III. UV for Dependency Management and Execution
All Python project dependencies MUST be managed exclusively using UV. Dependencies MUST be added via `uv add` and Python code MUST be executed via `uv run`. This ensures consistent and efficient dependency management and execution across all environments.

## Governance
This constitution supersedes all other practices. Amendments require documentation, approval, and a migration plan. All pull requests and code reviews MUST verify compliance with these principles.

**Version**: 1.1.0 | **Ratified**: 2025-10-02 | **Last Amended**: 2025-10-02
