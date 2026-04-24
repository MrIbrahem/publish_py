# AGENTS.md

Compact instructions for OpenCode sessions in this repository.

## Commands

```bash
# Tests (network tests excluded by default via pytest.ini)
pytest
pytest tests/test_services/test_mediawiki_api.py
pytest tests/test_services/test_text_processor.py::TestDoChangesToText

# Run network-dependent tests
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

-   **Entry point**: `src/app.py` calls `create_app()` from `src/sqlalchemy_app/__init__.py`
-   **Blueprints** in `src/sqlalchemy_app/public/routes/` and `src/sqlalchemy_app/admin/routes/`:
    -   `bp_api`, `bp_auth`, `bp_cxtoken`, `bp_main`, `bp_publish`, `bp_fixrefs`, `bp_leaderboard`, `bp_admin`
-   **Services**: `src/sqlalchemy_app/shared/services/` (mediawiki_api, wikidata_client, oauth_client, text_processor)
-   **Config**: Frozen dataclasses with `@lru_cache` in `src/sqlalchemy_app/config.py`
    -   Access via `from sqlalchemy_app.config import settings`
-   **DB layer**: `src/sqlalchemy_app/shared/engine.py` and `sqlalchemy_models/`

## Critical Conventions

-   **Import order**: `env_config.py` must be imported first (loads .env)
-   **Line length**: 120 characters (Black, isort, ruff all configured)
-   **Quotes**: Double quotes (ruff `quote-style = "double"`)
-   **CSRF**: Enabled via Flask-WTF on all POST routes
-   **fix_refs**: External dependency loaded from `FIX_REFS_PY_PATH` env var, falls back gracefully

## Environment

Required: `FLASK_SECRET_KEY`, `TOOL_TOOLSDB_DBNAME`, `TOOL_TOOLSDB_HOST`, `OAUTH_MWURI`, `OAUTH_CONSUMER_KEY`, `OAUTH_CONSUMER_SECRET`, `OAUTH_ENCRYPTION_KEY`

Optional: `TOOL_TOOLSDB_USER`, `TOOL_TOOLSDB_PASSWORD`, `USE_MW_OAUTH`, `CORS_ALLOWED_DOMAINS`, `SPECIAL_USERS`, `FALLBACK_USER`

See `src/example.env` for template.

## Testing

-   Tests in `tests/` use `conftest.py` which sets env vars before imports
-   Test markers: `@pytest.mark.unit`, `@pytest.mark.network`
-   Tests use in-memory SQLite (`sqlite:///:memory:`)
-   `pytest.ini` excludes network tests by default (`-m "not network"`)
-   Coverage enabled by default (src/sqlalchemy_app)
