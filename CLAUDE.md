# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Flask web application for publishing Wikipedia articles translated via ContentTranslation tool. Takes wikitext, refines it using the fix_refs repository, publishes to Wikipedia via MediaWiki API, and links articles to Wikidata.

**Stack**: Python 3.13, Flask, pytest, MySQL/MariaDB, MediaWiki OAuth

## Commands

```bash
# Run tests (excludes network tests by default)
pytest

# Run specific test file
pytest tests/test_services/test_mediawiki_api.py

# Run with network tests
pytest -m network

# Format and lint
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
from app_main import create_app
app = create_app()
```

### Key Directories
- `src/app_main/app_routes/` - Flask blueprints (api, auth, cxtoken, main, post, refs)
- `src/app_main/db/` - Database classes inheriting from `db_class.py`
- `src/app_main/services/` - External integrations (mediawiki_api, wikidata_client, oauth_client, text_processor)
- `src/app_main/users/` - User context and storage

### Configuration
Frozen dataclasses with `@lru_cache` singletons in `src/app_main/config.py`. Access via `from app_main.config import settings`.

### Database Pattern
Base `Database` class with context managers and connection pooling. Teardown handler closes connections.

### OAuth Flow
1. `/login` -> MediaWiki OAuth -> `/callback`
2. Tokens encrypted with Fernet, stored in database
3. Used for authenticated MediaWiki API calls

## Important Conventions

- **Import order**: `env_config.py` must be imported first (loads .env)
- **Line length**: 120 characters
- **Quotes**: Double quotes
- **CSRF protection**: Enabled via Flask-WTF
- **External dependency**: fix_refs_new_py loaded from external repo or `FIX_REFS_PY_PATH`

## Environment Variables

Required: `FLASK_SECRET_KEY`, `DB_NAME`, `DB_HOST`, `DB_USER`, `DB_PASSWORD`, `OAUTH_MWURI`, `OAUTH_CONSUMER_KEY`, `OAUTH_CONSUMER_SECRET`, `OAUTH_ENCRYPTION_KEY`

Optional: `USE_MW_OAUTH`, `CORS_ALLOWED_DOMAINS`, `SPECIAL_USERS`, `FALLBACK_USER`

See `src/example.env` for template.
