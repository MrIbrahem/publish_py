# `main_app/` -- Flask Application Factory

## Project Overview

`main_app` is the core Flask application package for the MDWiki Translation Dashboard. It implements the **Application Factory Pattern** to create, configure, and initialize the Flask app with all extensions, blueprints, error handlers, and template utilities.

### Main Modules

| File | Purpose |
|------|---------|
| `__init__.py` | Application factory (`create_app`), context processor, Jinja2 filters, error handlers |
| `admin/` | Admin blueprint -- coordinator dashboard, CRUD for translations, settings, QIDs |
| `config/` | Configuration dataclasses, Flask config classes, settings singleton |
| `db/` | Database models, services, and initialization (Flask-SQLAlchemy) |
| `public/` | Public-facing blueprints -- API, auth, publish, main pages, leaderboard |
| `shared/` | Shared utilities -- auth, clients, core extensions, schemas, helpers |

### Technologies & Frameworks

- **Flask** with Application Factory pattern
- **Flask-SQLAlchemy** for ORM
- **Flask-WTF** for CSRF protection
- **Flask-Migrate** (Alembic) for database migrations
- **Marshmallow** for request validation
- **MediaWiki OAuth** via `mwoauth` library
- **Fernet** encryption for stored OAuth tokens

## Architecture & Code Quality Review

### Application Factory (`create_app`)

The factory follows the canonical Flask pattern with 13 clear initialization steps:

```python
def create_app(config_class: Type) -> Flask:
    app = Flask(__name__, template_folder=..., static_folder=...)
    app.url_map.strict_slashes = False
    app.config.from_object(config_class())
    csrf_init_app(app)
    # Conditional DB init
    # Register 8 blueprints
    # Register context processor, filters, error handlers
    # Add cache-control headers
    return app
```

### Blueprint Architecture

8 blueprints are registered with clear URL prefix separation:

| Blueprint | Prefix | Purpose |
|-----------|--------|---------|
| `bp_main` | `""` | Homepage, results table, reports |
| `bp_leaderboard` | `/leaderboard` | Per-language and per-user leaderboards |
| `bp_auth` | `/auth` | OAuth login, callback, logout |
| `bp_cxtoken` | `/cxtoken` | ContentTranslation JWT tokens |
| `bp_publish` | `/publish` | Article publishing to Wikipedia |
| `bp_fixrefs` | `/fixrefs` | Reference fixing tool |
| `bp_api` | `/api` | JSON API endpoints |
| `bp_admin` | `/admin` | Admin dashboard (17 sub-blueprints) |

### Error Handling

Centralized HTTP error handlers with **content-type negotiation**:

```python
@app.errorhandler(404)
def not_found(e):
    if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html:
        return jsonify(error="Not Found"), 404
    return render_template("errors/404.html"), 404
```

Covers: 400, 401, 403, 404, 429, 500.

### Design Patterns

- **Factory Pattern**: `create_app(config_class)` -- allows different configs for dev/prod/test
- **Strategy Pattern**: Config class determines app behavior
- **Blueprint Pattern**: Modular route organization
- **Context Processor Pattern**: Template data injection (`current_user`, `is_admin`)
- **Decorator Pattern**: CSRF, CORS, auth checks applied via decorators

## Strengths

1. **Clean factory implementation**: The `create_app` function is well-organized with clear sections
2. **Conditional DB initialization**: `if app.config.get("SQLALCHEMY_DATABASE_URI")` allows the app to start without a database (useful for testing)
3. **CSRF-aware cache headers**: Auth-related routes get `no-store` cache headers to prevent CSRF token caching
4. **Content-type negotiation**: Error handlers respond with JSON or HTML based on `Accept` headers
5. **Custom test client**: `CookieHeaderClient` enables cookie-based auth testing

## Weaknesses

1. **CSRF exemption on entire `bp_publish` blueprint** (line 116): The publish endpoint is exempted from CSRF. While it uses CORS + secret key protection, the exemption should be narrowed to specific routes if possible.

2. **`is_admin` check on every request** (line 43): The context processor calls `active_coordinators()` on every template render. If this hits the database each time, it's a performance concern. Should be cached per-request or with `@lru_cache`.

3. **404 handler uses `logger.error`** (line 157): 404s are client errors and should use `logger.warning`, not `logger.error`. The 400/401/403/429 handlers correctly use `logger.warning`.

4. **Commented-out code**: Lines 104-105, 124-125, 193 contain commented-out blocks that should be cleaned up or converted to TODO comments.

5. **Missing 405 handler**: No `Method Not Allowed` handler is registered, falling through to Flask's default.

## Critical Issues

### Security

> **CSRF exemption on `bp_publish`**: The entire publish blueprint is exempted from CSRF protection. If any POST routes on this blueprint modify state without alternative protection, this could allow cross-site request forgery. The current alternative (CORS + `X-Secret-Key`) is acceptable for an API endpoint but should be documented.

### Performance

> **`active_coordinators()` in context processor**: Called on every request via `context_data()`. If this queries the database each time (rather than using the `@lru_cache` in `coordinator_service.py`), it adds unnecessary DB overhead to every page load.

### Bugs

> **Dead `g` attribute assignments**: In the auth logout handler, `g.current_user = None` and `g.is_authenticated = False` are set after `make_response()` is called. Since `g` is request-scoped and the response is already built, these assignments have no effect.

## Areas That Need Attention

| Area | Priority | Details |
|------|----------|---------|
| CSRF documentation | High | Document why `bp_publish` is exempt and what alternative protections exist |
| 404 log level | Medium | Change from `logger.error` to `logger.warning` |
| Missing 405 handler | Medium | Register a `Method Not Allowed` error handler |
| Commented-out code | Low | Remove or convert to proper TODO comments |
| Config instantiation | Low | `config_class()` in `from_object` -- verify if instantiation is needed |

## Improvement Plan

### Quick Wins
- [ ] Change 404 handler log level from `ERROR` to `WARNING`
- [ ] Add 405 Method Not Allowed error handler
- [ ] Remove commented-out code blocks
- [ ] Add docstring explaining CSRF exemption rationale on `bp_publish`

### Medium-term Improvements
- [ ] Cache `active_coordinators()` result per-request using Flask's `g` object
- [ ] Narrow CSRF exemption from entire blueprint to specific routes
- [ ] Add request logging middleware for debugging
- [ ] Add health check endpoint (`/health`) for monitoring

### Long-term Recommendations
- [ ] Extract the factory into a `create_app.py` module for cleaner separation
- [ ] Add OpenAPI/Swagger documentation for API endpoints
- [ ] Implement rate limiting on public API endpoints
- [ ] Add request ID tracking for distributed tracing

## Comprehensive Review

| Metric | Score | Notes |
|--------|-------|-------|
| **Overall Rating** | **7.5/10** | Solid factory pattern with minor security and performance concerns |
| **Production Readiness** | Ready with caveats | CSRF exemption needs documentation; performance should be verified |
| **Technical Debt** | Low-Medium | Commented-out code, missing error handlers |
| **Risk Assessment** | Medium | CSRF exemption and admin check performance are the main risks |
| **Maintainability** | High | Clear structure, good separation of concerns |
