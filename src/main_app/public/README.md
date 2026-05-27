# `public/` -- Public-Facing Blueprints

## Project Overview

The `public` package contains all public-facing Flask blueprints for the MDWiki Translation Dashboard. It implements 7 blueprints handling the main user interface, JSON API, OAuth authentication, ContentTranslation token management, article publishing, reference fixing, and leaderboards.

### Main Modules

| Directory | Blueprint | Prefix | Purpose |
|-----------|----------|--------|---------|
| `routes/api/` | `bp_api` | `/api` | JSON API endpoints for reports, stats, pages, categories |
| `routes/auth/` | `bp_auth` | `/auth` | OAuth login, callback, logout with rate limiting |
| `routes/cxtoken/` | `bp_cxtoken` | `/cxtoken` | ContentTranslation JWT token proxy |
| `routes/main/` | `bp_main` + `bp_leaderboard` | `""` + `/leaderboard` | Homepage, results tables, leaderboard |
| `routes/publish/` | `bp_publish` | `/publish` | Article publishing to Wikipedia via MediaWiki API |
| `routes/refs/` | `bp_fixrefs` | `/fixrefs` | Reference fixing tool |

### Technologies & Dependencies

- **Flask Blueprints** with CORS decorators
- **Marshmallow** for request validation
- **MediaWiki OAuth** via `mwoauth` library
- **cachetools.TTLCache** for CX token caching
- **requests** for external API calls

## Architecture & Code Quality Review

### API Blueprint (`routes/api/`)

13 JSON endpoints with consistent `{"results": ..., "count": ...}` envelope:

| Endpoint | Description |
|----------|-------------|
| `GET /api/publish_reports` | Filtered publish reports with Marshmallow validation |
| `GET /api/publish_reports_stats` | Filter dropdown options |
| `GET /api/in_process` | In-process translations with category/language data |
| `GET /api/in_process_total` | Aggregated in-process counts per user |
| `GET /api/pages_users` | User-space pages with campaign data |
| `GET /api/pages_with_views` | Pages with Wikipedia pageview counts |
| `GET /api/categories` | All category records |
| `GET /api/distinct_langs` | Distinct language codes |
| `GET /api/users_by_translations_count` | User translation counts |
| `GET /api/langs` | All language records |
| `GET /api/top_langs` | Aggregated stats per language |
| `GET /api/top_users` | Aggregated stats per user |

All endpoints decorated with `@check_cors`.

### Auth Blueprint (`routes/auth/`)

OAuth flow:
```
/auth/login  -> Generate state nonce -> mwoauth.Handshaker -> Redirect to MediaWiki
/auth/callback -> Verify state -> Complete handshake -> Store encrypted tokens -> Set signed cookie
/auth/logout -> Clear session -> Delete tokens -> Clear cookie
```

Features:
- **Rate limiting**: Sliding-window rate limiter (5/min login, 10/min callback)
- **State token signing**: OAuth state nonce signed with `itsdangerous`
- **Token encryption**: OAuth tokens encrypted with Fernet before DB storage

### Publish Blueprint (`routes/publish/`)

The core publishing workflow:
```
POST /publish/ -> Validate (CORS + secret key) -> Schema validation
  -> Look up user OAuth tokens
  -> Apply text fixes (fix_refs)
  -> Generate edit summary
  -> MediaWiki edit via OAuth
  -> Link to Wikidata
  -> Insert to DB
  -> Log report
```

Features:
- **CORS + secret key protection** (CSRF exempt)
- **Fallback user support** for Wikidata linking
- **Text processing** via `fix_refs` module
- **File-based report logging** for debugging

### Main Blueprint (`routes/main/`)

The results system (622 lines in `results_2026.py`) mirrors the PHP `Results/GetResults2026`:

```
/table -> _parse_request_args() -> results_loader_2026()
  -> get_results_2026(cat, code)
    -> missing_by_lang_and_category() (DB)
    -> exists_by_lang_and_category() (DB)
    -> get_mdwiki_cat_members() (MDWiki API)
  -> _build_missing_rows() / _build_exists_rows() / _build_inprocess_rows()
  -> Render template with HTML table rows
```

### CXToken Blueprint (`routes/cxtoken/`)

Proxy for ContentTranslation JWT tokens:
```
GET /cxtoken/?wiki=...&user=...
  -> Validate schema
  -> Check TTLCache
  -> Look up user OAuth token in DB
  -> Decrypt token
  -> Call MediaWiki CXToken API
  -> Cache and return JWT
```

### Design Patterns

- **Blueprint Pattern**: Clean separation with 7 blueprints
- **Decorator Pattern**: CORS (`@check_cors`), auth (`@login_required`, `@oauth_required`), access (`@validate_access`)
- **Schema Validation**: Marshmallow schemas for request validation
- **Cache Pattern**: TTL cache for CX tokens
- **PHP Port Pattern**: Extensive comments referencing original PHP functions being ported

## Strengths

1. **Consistent API envelope**: All JSON endpoints use `{"results": ..., "count": ...}` format
2. **CORS protection**: All API endpoints decorated with `@check_cors`
3. **Rate limiting**: Auth endpoints protected with sliding-window rate limiter
4. **Schema validation**: Marshmallow schemas validate all publish/CX token requests
5. **Graceful fallback**: Text processing falls back if `fix_refs` is not installed
6. **Project whitelist**: `text_api.py` validates wiki projects against regex, preventing SSRF

## Weaknesses

### Code Duplication

1. **`results_2026.py` ~ `results_api.py`**: Both contain `_create_summary()` / `_make_summary()` and `_get_inprocess_for_missing()` / `_get_inprocess_for_titles()` with nearly identical logic.

2. **`index()` ~ `table()` in `routes/main/routes.py`**: Share the same language/campaign loading logic (lines 147-210 and 213-244).

3. **`get_top_langs()` ~ `get_top_users()` in `top_stats_routes.py`**: Nearly identical query construction differing only in grouping column.

### Code Quality

4. **622-line `results_2026.py`**: The largest file in the codebase. Should be split into smaller, focused modules.

5. **Inconsistent error message** (`routes/api/routes.py` line 388): "fetching v data" is a copy-paste leftover.

6. **Unused `random` import** in `refs/routes.py`.

## Critical Issues

### Security

> **XSS in HTML builders** (`results_api.py`): `_make_summary()` and `_make_mdwiki_cat_url()` construct raw HTML with interpolated `code` and `cat` values without `html.escape`. While filtered by callers, the functions themselves are unsafe.

> **Rate limit bypass** (`auth/routes.py`): `_client_key()` trusts `X-Forwarded-For` header, trivially spoofable by clients.

> **Duplicate flash messages in logout**: Always shows "Logout successful" even when token deletion fails.

### Bugs

> **Dead `g` assignments in logout** (`auth/routes.py` lines 290-293): Setting `g.current_user = None` after `make_response()` has no effect.

> **`validate_access` dead code** (`cors/__init__.py`): Second error branch is unreachable due to control flow.

### Performance

> **`results_2026.py` makes multiple API calls**: The results system calls `get_mdwiki_cat_members()` (HTTP to mdwiki.org) and multiple DB queries. For large categories, this can be slow. File-based caching helps but is not always effective.

## Areas That Need Attention

| Area | Priority | Details |
|------|----------|---------|
| XSS in HTML builders | **High** | Add `html.escape` to all interpolated values |
| Rate limit bypass | **Medium** | Use `request.remote_addr` or configure trusted proxies |
| Code duplication | **Medium** | Merge `results_2026.py` and `results_api.py` shared logic |
| File size | **Medium** | Split `results_2026.py` (622 lines) into smaller modules |
| Error message typo | **Low** | Fix "fetching v data" in `users_by_translations_count` |
| Dead imports | **Low** | Remove `random` from `refs/routes.py` |

## Improvement Plan

### Quick Wins
- [ ] Fix XSS by adding `html.escape()` to `_make_summary()` and `_make_mdwiki_cat_url()`
- [ ] Fix "fetching v data" error message typo
- [ ] Remove unused `random` import from `refs/routes.py`
- [ ] Fix duplicate flash messages in logout

### Medium-term Improvements
- [ ] Extract shared language/campaign loading logic from `index()` and `table()` into a helper
- [ ] Merge `_make_summary()` and `_create_summary()` into a single shared function
- [ ] Split `results_2026.py` into `results_builder.py`, `results_data.py`, `results_html.py`
- [ ] Fix rate limiting to use `request.remote_addr`

### Long-term Recommendations
- [ ] Implement server-side caching for results (Redis or in-memory with TTL)
- [ ] Add pagination to results API for large categories
- [ ] Convert results system to async for parallel API calls
- [ ] Add OpenAPI documentation for all `/api/` endpoints

## Comprehensive Review

| Metric | Score | Notes |
|--------|-------|-------|
| **Overall Rating** | **7/10** | Functional with good patterns, but duplication and XSS concerns |
| **Production Readiness** | Ready with caveats | XSS in HTML builders needs fixing |
| **Technical Debt** | **Medium** | Code duplication, large files, PHP port artifacts |
| **Risk Assessment** | **Medium** | XSS risk; rate limit bypass; slow results for large categories |
| **Maintainability** | **Medium** | Good blueprint separation, but duplicated logic increases change risk |
