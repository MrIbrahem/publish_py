# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Flask web application for publishing Wikipedia articles translated via ContentTranslation tool. Takes wikitext, refines it using the fix_refs repository, publishes to Wikipedia via MediaWiki API, and links articles to Wikidata.

**Stack**: Python 3.13, Flask, pytest, MySQL/MariaDB, MediaWiki OAuth

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

# Production
gunicorn --workers=4 --bind=0.0.0.0 --forwarded-allow-ips=* src.app:app
```

## Architecture

### Application Factory

```python
from sqlalchemy_app import create_app
app = create_app()
```

### Key Directories

-   `src/sqlalchemy_app/app_routes/` - Flask blueprints: `bp_api`, `bp_auth`, `bp_cxtoken`, `bp_main`, `bp_post`, `bp_fixrefs`
-   `src/sqlalchemy_app/db/` - Database classes inheriting from `db_driver.py` (`DbPublishReports`, `DbPages`, `DbQids`)
-   `src/sqlalchemy_app/services/` - External integrations (mediawiki_api, wikidata_client, oauth_client, text_processor)
-   `src/sqlalchemy_app/users/` - User context (`current.py`) and storage (`store.py`)

### Configuration

Frozen dataclasses with `@lru_cache` singletons in `src/sqlalchemy_app/config.py`. Access via `from sqlalchemy_app.config import settings`.

### Database Pattern

Base `Database` class in `db_driver.py` provides:

-   Context manager support (`with Database(config) as db:`)
-   Automatic retry with exponential backoff for transient errors
-   Connection pooling via thread-local cache
-   Safe variants (`fetch_query_safe`, `execute_query_safe`) that log errors instead of raising

### OAuth Flow

1. `/login` -> MediaWiki OAuth -> `/callback`
2. Tokens encrypted with Fernet (cryptography library), stored in database
3. Used for authenticated MediaWiki API calls

## Important Conventions

-   **Import order**: `env_config.py` must be imported first (loads .env)
-   **Line length**: 120 characters
-   **Quotes**: Double quotes
-   **CSRF protection**: Enabled via Flask-WTF on all POST routes
-   **External dependency**: `fix_refs` module loaded from `FIX_REFS_PY_PATH` env var or falls back gracefully

## Environment Variables

Required: `FLASK_SECRET_KEY`, `TOOL_TOOLSDB_DBNAME`, `TOOL_TOOLSDB_HOST`, `OAUTH_MWURI`, `OAUTH_CONSUMER_KEY`, `OAUTH_CONSUMER_SECRET`, `OAUTH_ENCRYPTION_KEY`

Optional: `TOOL_TOOLSDB_USER`, `TOOL_TOOLSDB_PASSWORD`, `USE_MW_OAUTH`, `CORS_ALLOWED_DOMAINS`, `SPECIAL_USERS`, `FALLBACK_USER`

See `src/example.env` for template.

## Test Configuration

Tests in `tests/` use fixtures from `conftest.py` which sets required environment variables before imports. Test markers: `@pytest.mark.unit`, `@pytest.mark.network`. Coverage is enabled by default.
