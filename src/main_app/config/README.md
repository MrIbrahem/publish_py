# `config/` -- Application Configuration

## Project Overview

The `config` package provides the configuration system for the MDWiki Translation Dashboard. It uses **frozen dataclasses** composed into a singleton `Settings` object, with Flask-specific config classes that derive from it. All sensitive values are loaded from environment variables.

### Main Modules

| File | Purpose |
|------|---------|
| `__init__.py` | Re-exports all config classes and the `settings` singleton |
| `classes.py` | 9 frozen dataclasses defining the configuration schema |
| `flask_config.py` | Flask config classes (Development, Production, Testing) with SQLAlchemy URI builder |
| `main_settings.py` | Settings singleton loader -- `@lru_cache` based, reads from env vars |

### Technologies & Dependencies

- **Python frozen dataclasses** (`@dataclass(frozen=True)`) for immutable config
- **`@lru_cache(maxsize=1)`** for singleton pattern
- **python-dotenv** for development `.env` loading (handled by entry point)
- **PyMySQL** for SQLAlchemy URI construction

## Architecture & Code Quality Review

### Configuration Hierarchy

```
Settings (root frozen dataclass)
├── DbConfig          -- database connection (name, host, user, password)
├── Paths             -- filesystem paths (data, logs, reports, JSON files)
├── CookieConfig      -- auth cookie settings (name, max_age, secure, httponly)
├── SessionConfig     -- Flask session key names
├── OAuthConfig       -- MediaWiki OAuth credentials
├── CorsConfig        -- allowed CORS domains
├── UsersConfig       -- special user mappings, fallback user
├── SecurityConfig    -- Flask 3.1+ secret key settings
└── Top-level fields  -- publish_secret_code, user_agent, revids_api_url, etc.
```

### Loading Flow

```
app.py/app1.py
  └─ config.main_settings.settings  (module-level singleton)
       └─ get_settings()  (@lru_cache)
            ├─ _load_security_config()  -> SecurityConfig
            ├─ _load_database_config()  -> DbConfig
            ├─ _load_oauth_config()     -> OAuthConfig
            ├─ _get_paths()             -> Paths
            ├─ load_cookie_config()     -> CookieConfig
            └─ load_special_users()     -> UsersConfig
```

### Flask Config Classes

```python
Config (base)          -- Pulls from settings singleton, builds SQLALCHEMY_URI
├── DevelopmentConfig  -- DEBUG=True, SQLALCHEMY_ECHO=True
├── ProductionConfig   -- Strict cookie settings
└── TestingConfig      -- CSRF disabled, SQLite in-memory DB
```

### Design Patterns

- **Singleton Pattern**: `settings = get_settings()` with `@lru_cache(maxsize=1)` ensures one instance
- **Frozen Dataclasses**: Immutable configuration prevents accidental mutation
- **Strategy Pattern**: Flask config classes determine app behavior per environment
- **Builder Pattern**: `build_sqlalchemy_uri()` constructs the DB connection string

## Strengths

1. **Immutable configuration**: Frozen dataclasses prevent accidental mutation at runtime
2. **Clean composition**: `Settings` is composed of focused sub-configs, not a monolithic dict
3. **Environment-based**: All secrets come from env vars, never hardcoded
4. **Fail-fast**: `get_settings()` raises `RuntimeError` if `FLASK_SECRET_KEY` is empty
5. **SQLite compatibility**: `TestingConfig` uses SQLite in-memory for fast tests
6. **Comprehensive type safety**: Every config value has a proper type annotation

## Weaknesses

1. **Duplicate `Settings` in `__all__`**: `config/__init__.py` line 24 and line 36 both export `"Settings"`
2. **`DbConfig.to_dict()` leaks password**: The `to_dict()` method includes the `password` field, which could be logged accidentally
3. **`_get_paths()` creates directories at import time**: The log directory is created as a side effect of loading settings, which is unexpected for a config loader
4. **No validation of path existence**: `_get_paths()` expands env vars and `~` but doesn't validate that the paths are accessible

## Critical Issues

### Security

> **`DbConfig.to_dict()` includes password**: If this dict is ever logged or serialized (e.g., in error responses), the database password would be exposed. Consider excluding `password` from `to_dict()` or masking it.

> **`TestingConfig` hardcodes secret key**: `"test-secret-key-not-for-production"` is acceptable for tests but must never be used in production. The `ProductionConfig` correctly reads from env vars.

### Reliability

> **`_get_paths()` creates directories at import time**: If the directory creation fails (permissions, disk full), the settings singleton will fail to initialize, preventing the app from starting. This should be deferred to app startup.

## Areas That Need Attention

| Area | Priority | Details |
|------|----------|---------|
| Password in `to_dict()` | **High** | Exclude or mask `password` field |
| Duplicate `__all__` entry | **Low** | Remove duplicate `"Settings"` from `config/__init__.py` |
| Directory creation side effect | **Medium** | Move to app startup or make explicit |
| Path validation | **Low** | Add accessibility checks for critical paths |
| Missing env var documentation | **Low** | Document which env vars are required vs optional |

## Improvement Plan

### Quick Wins
- [ ] Remove duplicate `"Settings"` from `config/__init__.py` `__all__`
- [ ] Mask password in `DbConfig.to_dict()` (return `"***"` instead of actual value)
- [ ] Add docstrings to loader functions

### Medium-term Improvements
- [ ] Move directory creation from `_get_paths()` to an explicit `init_paths()` call during app startup
- [ ] Add env var validation with helpful error messages (e.g., "Set TOOL_TOOLSDB_HOST in .env")
- [ ] Add optional env var support with documented defaults

### Long-term Recommendations
- [ ] Consider using `pydantic-settings` for automatic env var parsing and validation
- [ ] Add configuration diff logging (log which settings differ from defaults on startup)
- [ ] Support configuration hot-reload for non-sensitive settings

## Comprehensive Review

| Metric | Score | Notes |
|--------|-------|-------|
| **Overall Rating** | **8.5/10** | Clean, well-structured, type-safe configuration |
| **Production Readiness** | Ready | Proper env var loading, fail-fast on missing secrets |
| **Technical Debt** | Low | Minor issues only (duplicate export, password leak) |
| **Risk Assessment** | Low | Frozen dataclasses prevent accidental mutation |
| **Maintainability** | High | Clear structure, good composition, comprehensive types |
