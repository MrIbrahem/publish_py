# Overview

Flask web application for mdwiki tools.

## Endpoints

-   read [docs/merge.md](docs/merge.md) for more informations

### Publish endpoint

publishing Wikipedia articles translated via ContentTranslation tool. Takes wikitext, refines it using the fix_refs repository, publishes to Wikipedia via MediaWiki API, and links articles to Wikidata.

**Stack**: Python 3.13, Flask, SQLAlchemy, MySQL/MariaDB, MediaWiki OAuth

## Architecture

```
src/main_app/
├── __init__.py
├── config.py
├── admin/
├── public/routes/
src/
├── main_app/
│   ├── __init__.py                 # Flask application factory (create_app)
│   ├── config/                     # App Configuration
│   ├── db/
│   │   ├── models/                 # Database models (pages, users, metrics, etc.)
│   │   ├── services/               # Business logic services
│   │   ├── __init__.py
│   │   ├── exceptions.py
│   │   └── README.md
│   │
│   ├── admin/                      # Admin blueprints
│   │   ├── routes/
│   │   │   └── __init__.py
│   │   └── __init__.py
│   │
│   ├── public/                     # Public blueprints
│   │   │   ├── api/                # REST API endpoints
│   │   │   ├── auth/               # OAuth authentication routes
│   │   │   ├── cxtoken/            # CX Token handling
│   │   │   ├── main/
│   │   │   ├── publish/            # Publishing endpoints
│   │   │   ├── refs/               # Fix refs tool
│   │   │   └── td/
│   │   ├── __init__.py
│   │   └── README.md
│   │
│   ├── shared/
│   │   ├── auth/                   # Authentication decorators and identity
│   │   ├── clients/                # External API clients (MediaWiki, Wikidata, OAuth)
│   │   ├── core/                   # CORS, cookies, crypto utilities
│   │   ├── schemas/
│   │   ├── utils/
│   │   ├── __init__.py
│   │   └── README.md
│   └── README.md
├── static/
│   ├── css/
│   ├── js/
│   └── favicon.svg
├── templates/
├── __init__.py
├── app.py
├── logger_config.py
└── README.md

```

## Configuration

Environment variables (see `src/example.env` for template):

| Variable                | Required | Description                      |
| ----------------------- | -------- | -------------------------------- |
| `FLASK_SECRET_KEY`      | Yes      | Secret key for Flask sessions    |
| `TOOL_TOOLSDB_DBNAME`   | Yes      | Database name                    |
| `TOOL_TOOLSDB_HOST`     | Yes      | Database host                    |
| `TOOL_TOOLSDB_USER`     | No       | Database user                    |
| `TOOL_TOOLSDB_PASSWORD` | No       | Database password                |
| `OAUTH_MWURI`           | Yes\*    | MediaWiki OAuth URI              |
| `OAUTH_CONSUMER_KEY`    | Yes\*    | OAuth consumer key               |
| `OAUTH_CONSUMER_SECRET` | Yes\*    | OAuth consumer secret            |
| `OAUTH_ENCRYPTION_KEY`  | Yes\*    | Fernet encryption key for tokens |
| `CORS_ALLOWED_DOMAINS`  | No       | Comma-separated allowed domains  |

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

# Production in linux
gunicorn --workers=4 --bind=0.0.0.0 --forwarded-allow-ips=* src.app:app

# Production in windows
pip install waitress
waitress-serve --threads=4 --host=localhost --port=8080 src.app1:app

```

## How Publishing Works

Before publishing to Wikipedia, the process uses the [fix_refs](https://github.com/MrIbrahem/fix_refs_new_py) repository to make several changes to the wikitext:

-   **Fixing References:** Correcting and standardizing reference formatting
-   **Expanding Infoboxes:** Enhancing infoboxes with more relevant information
-   **Adding Categories:** Ensuring appropriate categories are assigned
-   **Other changes:** Adding and correcting other minor wikitext issues

The application then publishes to Wikipedia via MediaWiki API and optionally links articles to Wikidata via the Wikidata API.

## Development UI Testing

The admin area normally requires the authenticated user to exist as an
active row in the coordinators table (`is_active_coordinator`, checked on
every login and on every `@admin_required` route).

For local UI testing (manual or automated — Playwright, Selenium, etc.),
this requirement can be bypassed **only** under `DevelopmentConfig`:

1. Start the app in development mode:

   ```bash
   flask --app src.app1 run
   ```

2. Set the bypass environment variable before starting:

   ```bash
   UI_TEST_BYPASS_COORDINATOR_CHECK=true flask --app src.app1 run
   ```

When enabled, any authenticated user is treated as an active coordinator
without needing a real row in the coordinators table. Every bypass use is
logged as a warning, so it's easy to spot in development logs.

**This bypass is permanently disabled under `ProductionConfig`.** Setting
`UI_TEST_BYPASS_COORDINATOR_CHECK=true` in a production environment has
no effect — the flag is only honored when the app is configured with
`DevelopmentConfig`. It must never be treated as a production
authorization mechanism.
