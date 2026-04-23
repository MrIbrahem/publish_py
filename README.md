# Overview

Flask web application for publishing Wikipedia articles translated via ContentTranslation tool. Takes wikitext, refines it using the fix_refs repository, publishes to Wikipedia via MediaWiki API, and links articles to Wikidata.

**Stack**: Python 3.13, Flask, SQLAlchemy, MySQL/MariaDB, MediaWiki OAuth

## Architecture

```
src/sqlalchemy_app/
├── __init__.py           # Flask application factory (create_app)
├── config.py             # Configuration dataclasses with @lru_cache settings
├── admin/                # Admin routes and sidebar
├── public/routes/        # Public blueprints
│   ├── auth/            # OAuth authentication routes
│   ├── main/            # Homepage, reports, missing pages
│   ├── publish/         # Publishing endpoints
│   ├── refs/            # Fix refs tool
│   ├── cxtoken/         # CX Token handling
│   └── api/             # REST API endpoints
├── shared/
│   ├── services/        # Business logic services
│   ├── clients/         # External API clients (MediaWiki, Wikidata, OAuth)
│   ├── auth/            # Authentication decorators and identity
│   ├── core/            # CORS, cookies, crypto utilities
│   └── sqlalchemy_models/  # SQLAlchemy ORM models
└── sqlalchemy_models/   # Database models (pages, users, metrics, etc.)
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
| `USE_MW_OAUTH`          | No       | Enable OAuth (default: true)     |
| `CORS_ALLOWED_DOMAINS`  | No       | Comma-separated allowed domains  |

\*Required when `USE_MW_OAUTH` is enabled

## REST API

### GET `/api/publish_reports`

Retrieves publish reports with optional filtering.

**Query Parameters:**

| Parameter     | Type   | Description                      |
| ------------- | ------ | -------------------------------- |
| `year`        | number | Filter by year (e.g., `2026`)    |
| `month`       | number | Filter by month (1-12)           |
| `title`       | string | Filter by page title             |
| `user`        | string | Filter by username               |
| `lang`        | string | Filter by language code          |
| `sourcetitle` | string | Filter by source title           |
| `result`      | string | Filter by result status          |
| `select`      | string | Comma-separated fields to return |
| `limit`       | number | Maximum results to return        |

**Special Filter Values:** `not_empty`, `empty`, `>0`, `all`

**Example:**

```
GET /api/publish_reports?year=2026&user=JohnDoe&limit=100
```

**Response:**

```json
{
    "results": [
        {
            "id": 123,
            "date": "2026-01-24T10:30:00",
            "title": "Example_Page",
            "user": "JohnDoe",
            "lang": "en",
            "sourcetitle": "Source_Example",
            "result": "success",
            "data": "{}"
        }
    ],
    "count": 1
}
```

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

## How Publishing Works

Before publishing to Wikipedia, the process uses the [fix_refs](https://github.com/MrIbrahem/fix_refs_new_py) repository to make several changes to the wikitext:

-   **Fixing References:** Correcting and standardizing reference formatting
-   **Expanding Infoboxes:** Enhancing infoboxes with more relevant information
-   **Adding Categories:** Ensuring appropriate categories are assigned
-   **Other changes:** Adding and correcting other minor wikitext issues

The application then publishes to Wikipedia via MediaWiki API and optionally links articles to Wikidata via the Wikidata API.
