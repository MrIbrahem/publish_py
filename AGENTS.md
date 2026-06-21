# AGENTS.md

Comprehensive instructions for AI agents and OpenCode sessions in this repository.

## Project Overview

Flask web application for publishing Wikipedia articles translated via ContentTranslation tool. Takes wikitext, refines it using the fix_refs repository, publishes to Wikipedia via MediaWiki API, and links articles to Wikidata.

**Stack**: Python 3.13, Flask, pytest, MySQL/MariaDB, MediaWiki OAuth

## Installation

```bash
# To run the application
pip install -r requirements.txt

# To run tests
pip install -r requirements-dev.txt
```

## Commands

```bash
# Run tests (excludes network tests by default, includes coverage)
pytest

# Run specific test file
pytest tests/test_services/test_mediawiki_api.py

# Run specific test class/method
pytest tests/test_services/test_text_processor.py::TestDoChangesToText

# Run with network tests
pytest -m network

# Format and lint (run before committing)
black src/ tests/
isort src/ tests/
ruff check src/ tests/
ruff format src/ tests/

# Development server
python src/app.py

# Production (Linux)
gunicorn --workers=4 --bind=0.0.0.0 --forwarded-allow-ips=* src.app:app

# Production (Windows)
waitress-serve --threads=4 --host=localhost --port=8080 src.app:app
```

## Architecture

### Entry point & Application Factory
-   `src/app.py` calls `create_app()` from `src/main_app/__init__.py`

### Key Directories & Blueprints
-   `src/main_app/public/routes/`: `bp_api`, `bp_auth`, `bp_cxtoken`, `bp_main`, `bp_publish`, `bp_fixrefs`, `bp_leaderboard`
-   `src/main_app/admin/routes/`: `bp_admin`
-   `src/main_app/db/`: Database models and services
-   `src/main_app/shared/`: Shared utilities, clients (mediawiki_api, wikidata_client, oauth_client, text_processor), and core logic.

### Configuration
-   Frozen dataclasses with `@lru_cache` singletons in `src/main_app/config.py`.
-   Access via `from main_app.config import settings`.

### Database Pattern
-   Uses Flask-SQLAlchemy for ORM.
-   Legacy database layer in `src/main_app/db/` provides retry logic and connection pooling.

### OAuth Flow
1. `/login` -> MediaWiki OAuth -> `/callback`
2. Tokens encrypted with Fernet (cryptography library), stored in database
3. Used for authenticated MediaWiki API calls

## Critical Conventions

-   **Import order**: `load_dotenv()` must be imported first (loads .env)
-   **Line length**: 120 characters (Black, isort, ruff all configured)
-   **Quotes**: Double quotes (ruff `quote-style = "double"`)
-   **CSRF**: Enabled via Flask-WTF on all POST routes
-   **fix_refs**: External dependency loaded from `FIX_REFS_PY_PATH` env var, falls back gracefully

## Environment Variables

Required: `FLASK_SECRET_KEY`, `TOOL_TOOLSDB_DBNAME`, `TOOL_TOOLSDB_HOST`, `OAUTH_MWURI`, `OAUTH_CONSUMER_KEY`, `OAUTH_CONSUMER_SECRET`, `OAUTH_ENCRYPTION_KEY`

Optional: `TOOL_TOOLSDB_USER`, `TOOL_TOOLSDB_PASSWORD`, `CORS_ALLOWED_DOMAINS`, `SPECIAL_USERS`, `FALLBACK_USER`

See `src/example.env` for template.

## Testing

-   Tests in `tests/` use `conftest.py` which sets required environment variables before imports.
-   Test markers: `@pytest.mark.unit`, `@pytest.mark.network`.
-   Tests use in-memory SQLite (`sqlite:///:memory:`) by default for unit tests.
-   `pytest.ini` excludes network tests by default (`-m "not network"`).
-   Coverage is enabled by default for `src/main_app`.
