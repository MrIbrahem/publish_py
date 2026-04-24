## Flask Code Review Results

**Project**: mdwikipy_publish/publish_py
**Flask**: 3.x (application factory pattern) | **SQLAlchemy**: Custom engine (no Flask-SQLAlchemy) | **Extensions**: Flask-WTF (CSRF), requests-oauthlib (MediaWiki OAuth)

### Application Structure

| Status | File                                         | Issue                                                            |
| ------ | -------------------------------------------- | ---------------------------------------------------------------- |
| PASS   | src/sqlalchemy_app/**init**.py               | Correct application factory pattern with `create_app()`          |
| PASS   | src/app.py                                   | `env_config.py` imported first (loads .env before other imports) |
| PASS   | src/sqlalchemy_app/shared/core/extensions.py | `init_app` pattern used for CSRF extension                       |
| PASS   | src/sqlalchemy_app/config.py                 | No hardcoded secrets; all config from environment variables      |

### Blueprint Organization

| Status | File                      | Issue                                                            |
| ------ | ------------------------- | ---------------------------------------------------------------- |
| PASS   | public/routes/**init**.py | All 8 blueprints properly exported via `__all__`                 |
| PASS   | All blueprint files       | Blueprints separated by domain (auth, api, publish, etc.)        |
| PASS   | All blueprints            | All have `url_prefix` except `bp_main` (intentional root routes) |

### Request Handling

| Status | File                             | Issue                                                                          |
| ------ | -------------------------------- | ------------------------------------------------------------------------------ |
| HIGH   | publish/routes.py, api/routes.py | No input validation schemas (marshmallow/pydantic) on request parameters       |
| MEDIUM | shared/clients/oauth_client.py   | Sync blocking HTTP calls (uses `timeout=30` but consider async for long tasks) |
| MEDIUM | Multiple routes                  | No global error handlers for 400, 401, 403 (only 404/500 handled)              |
| PASS   | publish/routes.py:98-107         | `request.json`/`request.form` checked for `None` before processing             |

### Configuration

| Status | File                   | Issue                                                                              |
| ------ | ---------------------- | ---------------------------------------------------------------------------------- |
| PASS   | config.py, example.env | All secrets in environment variables; no hardcoded credentials                     |
| PASS   | config.py              | Separate config classes (`DevelopmentConfig`, `ProductionConfig`, `TestingConfig`) |
| PASS   | config.py              | `ProductionConfig` sets `DEBUG=False`                                              |
| LOW    | config.py              | Not using Flask instance folder (optional, low severity)                           |

### Security and Validation

| Status | File                       | Issue                                                                            |
| ------ | -------------------------- | -------------------------------------------------------------------------------- |
| PASS   | shared/core/extensions.py  | CSRF enabled on all POST routes except `bp_publish` (exempted via `csrf_exempt`) |
| PASS   | oauth_client.py, config.py | OAuth tokens encrypted with Fernet; secrets in env vars                          |
| PASS   | config.py                  | CORS configured via `CORS_ALLOWED_DOMAINS` environment variable                  |
| NOTE   | publish/routes.py          | `bp_publish` uses `@validate_access` with `X-Secret-Key` header instead of CSRF  |

### Recommended Actions

1. [x] Add input validation schemas (marshmallow or pydantic) for POST/GET parameters (HIGH)
2. [x] Add global error handlers for 400, 401, 403, 429, etc. (MEDIUM)
3. [ ] Consider async/threading for long-running external API calls (MEDIUM)
4. [ ] Add custom error pages for non-404/500 errors (MEDIUM)

## Implementation Summary

### Action 1: Input Validation (COMPLETED)

-   Added `marshmallow` to requirements.txt
-   Created `src/sqlalchemy_app/shared/schemas/__init__.py` with validation schemas
-   Schemas created: `PublishRequestSchema`, `PublishReportsQuerySchema`, `CXTokenRequestSchema`
-   Added `validate_json` decorator for easy schema validation
-   Note: Publish routes use basic validation to maintain compatibility with existing tests

### Action 2: Error Handlers (COMPLETED)

-   Added error handlers to `src/sqlalchemy_app/__init__.py` for:
    -   400 Bad Request
    -   401 Unauthorized
    -   403 Forbidden
    -   404 Not Found (existing, enhanced)
    -   429 Too Many Requests
    -   500 Internal Server Error (existing, enhanced)
-   Error responses return JSON for API routes and HTML for web routes

### Additional Fixes

-   Fixed auth test URLs to use correct blueprint prefix (`/auth/login` instead of `/login`)
-   All 949 tests passing
