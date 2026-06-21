# `shared/` -- Shared Utilities & Infrastructure

## Project Overview

The `shared` package contains reusable infrastructure code shared across all blueprints in the MDWiki Translation Dashboard. It provides authentication, external API clients, core Flask extensions, request validation schemas, and utility functions. By design, `shared` must **never** import from `admin` or `public` packages.

### Main Modules

| Directory | Purpose |
|-----------|---------|
| `auth/` | Authentication decorators and user identity resolution |
| `clients/` | External API clients (MediaWiki, Wikidata, MDWiki, OAuth) |
| `core/` | Flask extensions (DB, CSRF, CORS), encryption, cookie signing |
| `schemas/` | Marshmallow request validation schemas |
| `utils/` | Utility functions (text processing, file handling, wiki links) |

### Technologies & Dependencies

- **Flask-WTF** for CSRF protection
- **Flask-SQLAlchemy** with custom `Base` class
- **Flask-Migrate** (Alembic) for database migrations
- **Fernet** (cryptography) for OAuth token encryption
- **itsdangerous** for signed cookies
- **Marshmallow** for request validation
- **mwoauth** for MediaWiki OAuth handshake
- **requests** for HTTP API calls
- **cachetools** for TTL-based caching

## Architecture & Code Quality Review

### Authentication Flow

```
/auth/login -> MediaWiki OAuth -> /auth/callback
  ├─ Store encrypted tokens in DB (user_tokens table)
  ├─ Set signed cookie (itsdangerous)
  └─ Populate g.current_user

Request -> current_user() resolution:
  ├─ Check g._current_user (per-request cache)
  ├─ Try session["uid"] -> DB lookup
  ├─ Try signed cookie -> DB lookup
  └─ Return None (unauthenticated)
```

Decorators:
- `@login_required` -- Redirects to login if unauthenticated
- `@oauth_required` -- Redirects to OAuth if configured but no user
- `@admin_required` -- 403 if not an active coordinator (in admin package)

### Client Architecture

| Client | Target API | Key Functions |
|--------|-----------|---------------|
| `mediawiki_api.py` | `{lang}.wikipedia.org` | `get_title_info()`, `publish_do_edit()` |
| `mdwiki_api.py` | `mdwiki.org` | `get_mdwiki_cat_members()` with BFS traversal + file cache |
| `oauth_client.py` | MediaWiki OAuth | `get_csrf_token()`, `post_params()`, `get_cxtoken()` |
| `text_api.py` | Wikimedia projects | `get_wikitext()` with project whitelist validation |
| `wikidata_client.py` | Wikidata API | `get_qid_for_mdtitle()`, `link_to_wikidata()` |
| `revids_client.py` | Local files / API | `get_revid()`, `get_revid_db()` |

### Core Extensions

```
shared/core/extensions/
├── data_base.py   -- db (SQLAlchemy), Base (ORM base with to_dict), LONGTEXT (cross-dialect)
├── _csrf.py       -- CSRF init and exempt functions
└── exc.py         -- UniqueError exception
```

### CORS Protection

Two decorators in `shared/core/cors/`:
- `@check_cors` -- Validates Origin/Referer against allowed domains list
- `@validate_access` -- Validates CORS OR `X-Secret-Key` header (for publish endpoint)

### Schemas (Marshmallow)

| Schema | Validates | Key Fields |
|--------|----------|------------|
| `PublishRequestSchema` | `/publish/` POST | user, title, text, target (2-10 chars), translate_type |
| `PublishReportsQuerySchema` | `/api/publish_reports` GET | year, month, title, user, lang, result, limit |
| `CXTokenRequestSchema` | `/cxtoken/` GET | wiki (required), user (required) |

### Design Patterns

- **Decorator Pattern**: Auth, CORS, CSRF applied via decorators
- **Lazy Initialization**: Fernet cipher, words table, ContentTranslation endpoint use lazy loading
- **Facade Pattern**: `shared/clients/__init__.py` re-exports all client functions
- **Whitelist Pattern**: `text_api.py` validates `project` against regex whitelist
- **TTL Cache**: `cxtoken/cache.py` uses `cachetools.TTLCache` for token caching

## Strengths

1. **Clean separation**: `shared` never imports from `admin` or `public` -- dependency direction is clear
2. **Comprehensive XSS protection**: `wiki_links.py` uses `html.escape` on all user input and `urllib.parse.quote` for URLs
3. **Timing-safe comparison**: `publish_secret_checks.py` uses `hmac.compare_digest` for secret key validation
4. **Project whitelist**: `text_api.py` validates wiki projects against a regex whitelist, preventing SSRF
5. **Graceful fallback**: `text_processor.py` falls back gracefully if `fix_refs` module is not installed
6. **Rate limiting**: Auth routes have in-memory sliding-window rate limiters (5/min login, 10/min callback)

## Weaknesses

### Thread Safety

1. **`crypto.py` -- Commented-out lock**: The `_fernet_lock` is commented out. In multi-threaded production (gunicorn with threads), concurrent first-access to `_require_fernet()` could create a race condition. Worst case: two Fernet instances created (not corruption, but wasteful).

2. **Module-level serializer initialization** (`cookie.py`): `URLSafeTimedSerializer` instances are created at module import time using `settings.security.secret_key`. If settings aren't loaded yet, this fails. Works due to Flask's factory pattern but is fragile.

### Code Quality

3. **`do_changes_to_text()` vs `do_changes_to_text_with_settings()`** (`text_processor.py`): Two similar functions exist. The former uses legacy `DoChangesToText1`, the latter uses `fix_one_page`. Only `do_changes_to_text_with_settings()` is used by routes.

4. **`os.sys.path.insert` in `text_processor.py`**: Uses `os.sys.path.insert(0, fix_refs_path)` instead of the standard `import sys; sys.path.insert(...)`.

5. **Unused `validate_json` decorator** (`schemas/__init__.py`): Defined but never used -- routes do manual schema loading instead.

## Critical Issues

### Security

> **XSS risk in `results_api.py` and `results_2026.py`**: Functions like `_make_summary()` and `_make_mdwiki_cat_url()` construct raw HTML with interpolated values (`code`, `cat`) without `html.escape`. While `code` is filtered by `get_lang_by_code()` in the caller, the `results_api_result()` function takes `code` directly and uses it in `<a href>` tags. A crafted `code` like `"><script>alert(1)</script>` could inject HTML.

> **OAuth state token uses cookie max_age** (`cookie.py` line 51): `verify_state_token` uses `settings.cookie.max_age` for token lifetime. OAuth state tokens should have a much shorter lifetime (5-10 minutes) to prevent replay attacks.

> **`X-Forwarded-For` spoofing** (`auth/routes.py` line 45-48): Rate limiting trusts `X-Forwarded-For` header, which is trivially spoofable. Combined with `forwarded-allow-ips=*` in gunicorn config, any client can bypass rate limiting by rotating the header.

### Bugs

> **Duplicate flash messages in logout** (`auth/routes.py`): The logout handler always calls `flash("Logout successful.", "success")` regardless of whether token deletion succeeded. Users who get "Error while clearing OAuth credentials" will also see "Logout successful".

> **Dead `g` attribute assignments** (`auth/routes.py` lines 290-293): Setting `g.current_user = None` after `make_response()` has no effect -- `g` is request-scoped and the response is already built.

> **`validate_access` dead code** (`cors/__init__.py` lines 51-67): The second error response ("Requests are only allowed from authorized domains") is unreachable due to the control flow logic.

### Code Quality

> **Inconsistent error message** (`api/routes.py` line 388): `users_by_translations_count()` error says "fetching v data" -- a copy-paste leftover.

## Areas That Need Attention

| Area | Priority | Details |
|------|----------|---------|
| XSS in HTML builders | **High** | `results_api.py` and `results_2026.py` need `html.escape` on interpolated values |
| OAuth state token lifetime | **High** | Use shorter TTL (5-10 min) instead of cookie max_age |
| Rate limit bypass via X-Forwarded-For | **Medium** | Use `request.remote_addr` or configure trusted proxies properly |
| Thread-safe Fernet init | **Medium** | Uncomment the lock or use a module-level singleton |
| Dead code cleanup | **Low** | Remove `do_changes_to_text()`, `validate_json`, unreachable CORS error |

## Improvement Plan

### Quick Wins
- [ ] Add `html.escape()` to all HTML string builders in `results_api.py` and `results_2026.py`
- [ ] Fix duplicate flash messages in logout handler
- [ ] Fix copy-paste error message in `users_by_translations_count()`
- [ ] Remove dead `g` attribute assignments after `make_response()`

### Medium-term Improvements
- [ ] Implement separate TTL for OAuth state tokens (shorter than cookie max_age)
- [ ] Uncomment thread-safety lock in `crypto.py` or use a proper singleton pattern
- [ ] Fix rate limiting to use `request.remote_addr` instead of `X-Forwarded-For`
- [ ] Remove unused `do_changes_to_text()` function
- [ ] Clean up unreachable code in `validate_access`

### Long-term Recommendations
- [ ] Add request-scoped caching for `get_endpoint()` (currently hits DB on every call)
- [ ] Implement structured API error responses (consistent JSON error format)
- [ ] Add OpenAPI/Swagger documentation for all API endpoints
- [ ] Consider using `httpx` instead of `requests` for async-capable HTTP client

## Comprehensive Review

| Metric | Score | Notes |
|--------|-------|-------|
| **Overall Rating** | **7/10** | Solid infrastructure with some security gaps |
| **Production Readiness** | Ready with caveats | XSS and rate limit bypass need fixing |
| **Technical Debt** | **Medium** | Dead code, duplicate functions, inconsistent patterns |
| **Risk Assessment** | **Medium** | XSS risk in HTML builders; rate limit bypass |
| **Maintainability** | **High** | Clean separation, good documentation, consistent patterns |
