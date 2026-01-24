# Copilot Instructions for publish_py

## Project Overview

This is a Python Flask web application that manages the final steps in publishing Wikipedia articles that have been translated using the ContentTranslation tool. The application:

- Takes translated text in wikitext format
- Refines it using the fix_refs repository
- Publishes articles to Wikipedia via MediaWiki API
- Links articles to Wikidata
- Provides REST API endpoints for publish reports

## Technology Stack

- **Language**: Python 3.13
- **Framework**: Flask (with Flask-WTF for CSRF protection)
- **Testing**: pytest
- **Code Formatting**: Black, isort, Ruff
- **Database**: MySQL/MariaDB (using custom database classes)
- **Authentication**: MediaWiki OAuth

## Code Style Guidelines

### Formatting

- **Line Length**: 120 characters (configured in Black, isort, and Ruff)
- **Quote Style**: Double quotes for strings
- **Import Style**: Use vertical formatting with trailing commas (isort profile: black)
- **Type Hints**: Use `from __future__ import annotations` and type hints throughout

### Code Quality Tools

Run these commands before committing:

```bash
# Format code with Black
black src/ tests/

# Sort imports with isort
isort src/ tests/

# Lint with Ruff
ruff check src/ tests/
ruff format src/ tests/
```

### Ignored Lint Rules

The following rules are intentionally ignored (see `pyproject.toml`):
- E402: Module level import not at top of file
- E225, E226, E227, E228: Whitespace around operators
- E252: Missing whitespace around parameter equals
- E501: Line too long (handled by Black)
- E224: Tab before operator
- E203: Whitespace before punctuation
- F841: Local variable assigned but never used
- F401: Module imported but unused

## Testing Guidelines

### Running Tests

```bash
# Run all tests (excluding network tests)
pytest

# Run specific test file
pytest tests/test_services/test_mediawiki_api.py

# Run with network tests
pytest -m network

# Run specific test class
pytest tests/test_services/test_text_processor.py::TestDoChangesToText
```

### Test Structure

- **Location**: All tests are in the `tests/` directory
- **Naming**: Test files follow the pattern `test_*.py` or `*Test.py`
- **Classes**: Test classes are prefixed with `Test*`
- **Functions**: Test functions are prefixed with `test_*`
- **Markers**: Use `@pytest.mark.unit` for unit tests, `@pytest.mark.network` for tests requiring network access
- **Fixtures**: Shared fixtures are in `tests/conftest.py`

### Test Configuration

- Tests use `pytest.ini` for configuration
- Maximum 25 failures before stopping (`--maxfail=25`)
- Network tests are excluded by default (`-m "not network"`)
- Verbose output with short tracebacks (`-v --tb=short`)

## Project Structure

```
src/
├── app/                    # Main application package
│   ├── __init__.py        # Flask app factory (create_app())
│   ├── config.py          # Configuration dataclasses and settings
│   ├── app_routes/        # Route blueprints
│   │   ├── api/           # REST API endpoints
│   │   ├── auth/          # OAuth authentication
│   │   ├── cxtoken/       # CX token handling
│   │   ├── main/          # Main routes
│   │   └── post/          # Publishing endpoints
│   ├── db/                # Database modules
│   │   ├── db_class.py    # Base database class
│   │   ├── db_publish_reports.py
│   │   ├── db_Pages.py
│   │   └── db_qids.py
│   ├── services/          # Business logic services
│   │   ├── mediawiki_api.py
│   │   ├── oauth_client.py
│   │   ├── revids_service.py
│   │   ├── text_processor.py
│   │   └── wikidata_client.py
│   ├── helpers/           # Utility functions
│   │   ├── cors.py
│   │   ├── files.py
│   │   └── format.py
│   └── users/             # User management
│       ├── current.py
│       └── store.py
├── app.py                 # WSGI entry point
├── env_config.py          # Environment configuration
└── log.py                 # Logging configuration
```

## Key Architectural Patterns

### Application Factory Pattern

The app uses Flask's application factory pattern. Create the app using:

```python
from app import create_app
app = create_app()
```

### Configuration Management

Configuration is managed through dataclasses in `src/app/config.py`:

- `Settings`: Main settings dataclass (singleton via `@lru_cache`)
- `DbConfig`: Database configuration
- `OAuthConfig`: MediaWiki OAuth settings
- `CookieConfig`: Cookie settings
- `CorsConfig`: CORS configuration
- `UsersConfig`: User-related settings

Access settings using:

```python
from app.config import settings
db_config = settings.database_data
```

### Database Pattern

Database classes inherit from a base class in `db_class.py`. Each table has its own class:

- `DbPublishReports`: Manages publish reports
- `DbPages`: Handles page data
- `DbQids`: Manages Wikidata QIDs

Database connections are managed with context managers and closed after each request using `close_cached_db()`.

### Blueprint Pattern

Routes are organized into blueprints:

- `bp_api`: REST API endpoints (`/api/*`)
- `bp_auth`: OAuth authentication
- `bp_cxtoken`: CX token endpoints
- `bp_main`: Main routes
- `bp_post`: Publishing endpoints

## Environment Variables

Required environment variables (see `src/example.env`):

- `FLASK_SECRET_KEY`: Flask session secret key
- `DB_NAME`: Database name
- `DB_HOST`: Database host
- `DB_USER`: Database username
- `DB_PASSWORD`: Database password
- `OAUTH_MWURI`: MediaWiki OAuth URI
- `OAUTH_CONSUMER_KEY`: OAuth consumer key
- `OAUTH_CONSUMER_SECRET`: OAuth consumer secret
- `OAUTH_ENCRYPTION_KEY`: Encryption key for OAuth tokens

Optional environment variables:

- `USE_MW_OAUTH`: Enable/disable MediaWiki OAuth (default: true)
- `CORS_ALLOWED_DOMAINS`: Comma-separated list of allowed CORS domains
- `SPECIAL_USERS`: User mapping for alternate usernames
- `FALLBACK_USER`: Default user for retry operations

## API Endpoints

### GET `/api/publish_reports`

Retrieve publish reports with filtering options.

**Query Parameters**:
- `year`: Filter by year
- `month`: Filter by month (1-12)
- `title`: Filter by page title
- `user`: Filter by username
- `lang`: Filter by language code
- `sourcetitle`: Filter by source title
- `result`: Filter by result status
- `select`: Comma-separated fields to return
- `limit`: Maximum results to return

## Common Tasks

### Adding a New Route

1. Create a new module in the appropriate blueprint directory
2. Define route using the blueprint decorator
3. Import and register in the blueprint's `__init__.py`

### Adding a New Database Table

1. Create a new class in `src/app/db/` inheriting from the base database class
2. Define table structure and methods
3. Add table initialization in app factory if needed

### Adding a New Service

1. Create a new module in `src/app/services/`
2. Implement service functions
3. Add tests in `tests/test_services/`

### Working with OAuth

- OAuth is handled by `src/app/services/oauth_client.py`
- Tokens are encrypted using `src/app/crypto.py`
- User data is stored using `src/app/users/store.py`
- Current user context is available via `src/app/users/current.py`

## Important Notes

- **File Skipping**: The `# isort:skip_file` comment in `app.py` is intentional to control import order
- **Environment Configuration**: `env_config.py` must be imported first to load environment variables
- **CSRF Protection**: Enabled by default using Flask-WTF
- **CORS**: Configured to allow specific domains (medwiki.toolforge.org, mdwikicx.toolforge.org)
- **Logging**: Configured in `log.py` with console logger
- **Database Connections**: Always use context managers and ensure connections are closed

## Git Ignore Patterns

The `.gitignore` excludes:
- `*.pyc`: Python bytecode
- `.env`: Environment files
- `/old`: Old code directory
- `/data/logs`: Log files
- `*.json` (except specific files)
- Test files and temporary PHP files

## Documentation

- API documentation: `docs/api.md`
- OpenAPI specification: `docs/openapi.yaml`
- README: `README.md`

## Special Considerations

### User Handling

- Some users have alternate usernames mapped in configuration
- Certain users don't get hashtags on their own pages
- Fallback user is used for retry operations

### Text Processing

The application uses an external `fix_refs` repository to:
- Fix and standardize reference formatting
- Expand infoboxes
- Add categories
- Make other wikitext corrections

### Wikidata Integration

After successful publication, articles are linked to Wikidata using the `wikidata_client.py` service.
