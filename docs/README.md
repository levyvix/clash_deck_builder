# Documentation

This directory contains the project documentation built with MkDocs and the Material theme.

## Quick Start

```bash
# Serve documentation locally
uv run mkdocs serve

# Build static site
uv run mkdocs build

# Deploy to GitHub Pages (if configured)
uv run mkdocs gh-deploy
```

The documentation will be available at http://127.0.0.1:8001

## Documentation Structure

```
docs/
├── index.md                    # Homepage
├── getting-started/            # Getting started guides
│   ├── quickstart.md
│   ├── environment-setup.md
│   └── workflow.md
├── architecture/               # System architecture
│   ├── overview.md
│   ├── backend.md
│   ├── frontend.md
│   └── database.md
├── development/                # Development guides
│   ├── backend.md
│   ├── frontend.md
│   ├── testing.md
│   └── docker.md
├── api/                        # API reference
│   ├── overview.md
│   ├── authentication.md
│   ├── profile.md
│   ├── cards.md
│   └── decks.md
├── features/                   # Feature documentation
│   ├── deck-management.md
│   ├── evolution-cards.md
│   ├── anonymous-mode.md
│   └── google-oauth.md
└── operations/                 # Operational guides
    ├── migrations.md
    ├── deployment.md
    └── troubleshooting.md
```

## Writing Documentation

### Markdown Features

The documentation supports extended Markdown via PyMdown Extensions:

#### Code Blocks

````markdown
```python
def hello_world():
    print("Hello, World!")
```
````

#### Admonitions

```markdown
!!! note
    This is a note admonition.

!!! warning
    This is a warning admonition.

!!! tip
    This is a tip admonition.
```

#### Tabs

```markdown
=== "Python"
    ```python
    print("Hello")
    ```

=== "JavaScript"
    ```javascript
    console.log("Hello");
    ```
```

#### Tables

```markdown
| Column 1 | Column 2 |
|----------|----------|
| Value 1  | Value 2  |
```

### Navigation

Edit `mkdocs.yml` in the project root to modify the navigation structure:

```yaml
nav:
  - Home: index.md
  - Getting Started:
      - Quick Start: getting-started/quickstart.md
```

### Theme Customization

The documentation uses the Material theme. Customize in `mkdocs.yml`:

```yaml
theme:
  name: material
  palette:
    primary: deep purple
    accent: purple
```

## Building for Production

```bash
# Build static site
uv run mkdocs build

# Output will be in site/ directory
# Deploy site/ contents to your web server
```

## Local Development

```bash
# Start dev server with live reload
uv run mkdocs serve

# Access at http://127.0.0.1:8001
# Changes to markdown files will auto-reload
```

## Contributing to Documentation

1. Edit or create markdown files in `docs/`
2. Test locally with `uv run mkdocs serve`
3. Commit changes
4. Documentation will be built and deployed automatically (if CI/CD configured)

## Useful MkDocs Commands

```bash
# Create new project (already done)
uv run mkdocs new .

# Serve with custom address
uv run mkdocs serve -a 0.0.0.0:8002

# Build with strict mode (fail on warnings)
uv run mkdocs build --strict

# Clean build directory
uv run mkdocs build --clean
```

## More Information

- [MkDocs Documentation](https://www.mkdocs.org/)
- [Material Theme Documentation](https://squidfunk.github.io/mkdocs-material/)
- [PyMdown Extensions](https://facelessuser.github.io/pymdown-extensions/)
