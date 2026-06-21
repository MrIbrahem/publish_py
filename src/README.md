# `src/` -- Application Entry Points & Logging

## Project Overview

This directory is the root package of the **MDWiki Translation Dashboard** -- a Flask web application that publishes Wikipedia articles translated via the ContentTranslation tool. The `src/` folder contains the WSGI entry points, logging configuration, and the `main_app` application package.

### Main Modules

| File | Purpose |
|------|---------|
| `app.py` | Production WSGI entry point (23 lines) |
| `app1.py` | Development WSGI entry point with `.env` loading (37 lines) |
| `logger_config.py` | Centralized logging with colored console + file handlers (117 lines) |
| `__init__.py` | Package marker (empty) |
| `main_app/` | The Flask application package (see its own README) |

### Technologies & Dependencies

- **Python 3.13** with **Flask** application factory pattern
- **PyMySQL** as the MySQL adapter (installed as MySQLdb shim)
- **python-dotenv** for development environment variable loading
- **colorlog** for colored terminal output
- **WatchedFileHandler** for log-rotation-safe file logging

## Architecture & Code Quality Review

### Entry Point Design

The project uses a clean dual-entry-point strategy:

```
app.py  (Production)  -- No .env loading, WARNING-level logging, ProductionConfig
app1.py (Development) -- .env loading, DEBUG-level logging, DevelopmentConfig, sys.path manipulation
```

Both delegate to `main_app.create_app()` with their respective config class, following the **Strategy Pattern**.

### Code Organization

- **Flat structure**: Only 3 meaningful files at this level, which is appropriate for entry points
- **Clear separation**: Entry points are minimal -- they bootstrap config, logging, and delegate to the app factory
- **`isort:skip_file`**: Both entry points use this directive because `pymysql.install_as_MySQLdb()` and `load_dotenv()` must execute before other imports

### Logging Architecture

`logger_config.py` implements a **Facade Pattern** over Python's logging system:

```
configure_logging(level)
  └─ setup_logging(level, name, log_file, error_log_file)
       ├─ StreamHandler (colored via colorlog)
       ├─ WatchedFileHandler (app.log -- all levels)
       └─ WatchedFileHandler (errors.log -- WARNING+)
```

Key design decisions:
- **`WatchedFileHandler`** instead of `FileHandler` -- automatically reopens files after external log rotation (e.g., `logrotate`)
- **Idempotent setup** -- `if project_logger.handlers: return` prevents duplicate handlers on repeated calls
- **Fallback chain** -- if log directory creation fails, falls back to console-only logging

## Strengths

- **Minimal entry points**: `app.py` is only 23 lines -- clean, focused, and easy to audit
- **Environment-aware**: Clear separation between production (env vars from Toolforge) and development (`.env` file)
- **Robust logging**: Handles directory creation, log rotation, and graceful degradation
- **SQLAlchemy log suppression**: `app1.py` correctly sets SQLAlchemy logger to WARNING to reduce noise during development

## Weaknesses

1. **Non-descriptive naming**: `app1.py` is a poor name for the development entry point. `app_dev.py` or `wsgi_dev.py` would be clearer.

2. **`sys.path` manipulation in `app1.py`**: The `sys.path.insert(0, ...)` is a code smell. A proper `pyproject.toml` with `pip install -e .` would eliminate this.

3. **Boilerplate duplication**: Both entry points share `pymysql.install_as_MySQLdb()` and the `from main_app import create_app` import. This could be extracted to a shared bootstrap function.

## Critical Issues

> **None identified.** The entry points are well-isolated and low-risk.

### Minor Issues

- **`logger_config.py` type annotation mismatch**: The `level` parameter in `setup_logging()` is annotated as `str` but called with `logging.WARNING` (an `int`). The runtime handles this via `isinstance(level, str)`, but the annotation is misleading.

- **f-string in logging call** (`app1.py` line 22): Uses `logging.warning(f"Failed to load .env file from {_env_file_path}")` instead of the preferred lazy formatting: `logging.warning("Failed to load .env file from %s", _env_file_path)`.

- **Broad exception catch** (`app1.py` line 20-22): `except Exception` around `load_dotenv()` is overly broad. `load_dotenv()` returns `False` silently if the file doesn't exist; the catch could mask unexpected errors.

## Areas That Need Attention

| Area | Status |
|------|--------|
| Missing documentation | No README existed before this one |
| Naming conventions | `app1.py` should be renamed |
| Type annotations | `logger_config.py` needs `level: str | int` fix |
| Test coverage | Entry points are not directly tested (app factory is tested separately) |

## Improvement Plan

### Quick Wins
- [ ] Rename `app1.py` to `app_dev.py` and update any scripts/docs that reference it
- [ ] Fix `setup_logging` type annotation to `level: str | int = "WARNING"`
- [ ] Replace f-string logging with `%s` lazy formatting

### Medium-term Improvements
- [ ] Extract shared bootstrap logic (`pymysql.install_as_MySQLdb()`) to a `bootstrap.py` module
- [ ] Add a `pyproject.toml` to enable `pip install -e .` and eliminate `sys.path` manipulation
- [ ] Add integration tests that verify both entry points can create an app instance

### Long-term Recommendations
- [ ] Consider a single entry point with `--dev` flag or environment-based config selection
- [ ] Add structured logging (JSON format) for production log aggregation

## Comprehensive Review

| Metric | Score | Notes |
|--------|-------|-------|
| **Overall Rating** | **8/10** | Clean, minimal, well-structured entry points |
| **Production Readiness** | Ready | Production entry point is solid |
| **Technical Debt** | Low | Minor naming and type annotation issues |
| **Risk Assessment** | Low | Entry points are isolated; failures here prevent app startup (fail-fast) |
| **Maintainability** | High | Simple files, clear purpose, minimal dependencies |
