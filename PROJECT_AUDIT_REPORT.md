# MDWiki Translation Dashboard -- Project Audit Report

**Audit Date**: 2026-05-27
**Auditor**: Senior Software Architect & Technical Auditor
**Scope**: Full codebase analysis across `src/` (8 subfolders, 100+ Python files, 16 PHP files)

---

## Executive Summary

The **MDWiki Translation Dashboard** is a Flask web application that publishes Wikipedia articles translated via the ContentTranslation tool. It takes wikitext, refines references using the `fix_refs` module, publishes to Wikipedia via the MediaWiki API, and links articles to Wikidata. A parallel PHP codebase handles translation progress reporting against the same database.

**Stack**: Python 3.13, Flask (Application Factory), Flask-SQLAlchemy, Marshmallow, MediaWiki OAuth, Fernet encryption, MySQL/MariaDB (production), SQLite (testing).

**Architecture**: Clean layered design with 8 Flask blueprints, a service layer (~60 CRUD functions), frozen dataclass configuration, and a shared infrastructure package. The codebase is a partial PHP-to-Python rewrite where publishing lives in Python and results reporting remains partially in PHP.

**Bottom line**: The application is functional and deployed on Toolforge, but has **critical security gaps** (missing admin route protection, XSS in HTML builders, hardcoded PHP credentials) and **significant technical debt** (massive code duplication across service and route layers). It requires immediate security hardening before it can be considered production-ready.

---

## Project Health Assessment

| Dimension | Rating | Assessment |
|-----------|--------|------------|
| **Overall Code Quality** | 6.5/10 | Good patterns exist (factory, service layer, frozen config) but undermined by duplication and copy-paste bugs |
| **Maintainability** | 5.5/10 | High duplication (4+ service pairs at 90%+ similarity) makes changes risky; a single edit often needs to be replicated in 2-4 files |
| **Scalability** | 6/10 | Connection pooling configured (pool_size=5, max_overflow=10); but `active_coordinators()` DB call on every request and unbounded result sets are concerns |
| **Security Posture** | 4/10 | 8+ admin routes unprotected; XSS in HTML builders; rate limit bypass; hardcoded PHP credentials; OAuth state token reuse |
| **Production Readiness** | Partial | Core publishing workflow works; admin dashboard has critical access control gaps; PHP code not deployable standalone |

### Per-Module Scores

| Module | Score | Key Issue |
|--------|-------|-----------|
| `src/` (entry points) | 8/10 | Clean, minimal -- minor naming issue |
| `main_app/` (factory) | 7.5/10 | CSRF exemption needs documentation |
| `config/` | 8.5/10 | Excellent frozen dataclass design |
| `db/` | 6.5/10 | Massive duplication, broken `_main_service.py` |
| `admin/` | 5/10 | **Critical**: missing `@admin_required` on 8+ files |
| `public/` | 7/10 | XSS in HTML builders, rate limit bypass |
| `shared/` | 7/10 | Thread-safety concern in crypto, good patterns |
| `results_api_php_code/` | 4/10 | Hardcoded credentials, SQL error exposure |

---

## Cross-Project Analysis

### Shared Architectural Patterns

The codebase follows consistent patterns across modules:

1. **Application Factory** (`create_app` with config class injection)
2. **Blueprint Pattern** (8 top-level + 17 admin sub-blueprints)
3. **Service-Module Pattern** (free functions per table, not classes)
4. **Decorator Pattern** (`@admin_required`, `@check_cors`, `@validate_access`, `@login_required`)
5. **Frozen Dataclass Config** (immutable `Settings` singleton via `@lru_cache`)
6. **Cross-Dialect Support** (`LONGTEXT` TypeDecorator for MySQL/SQLite compatibility)

### Repeated Weaknesses

| Weakness | Affected Modules | Frequency |
|----------|-----------------|-----------|
| Code duplication (90%+ similarity) | `db/`, `admin/`, `public/` | 8+ file pairs |
| Missing `@admin_required` decorator | `admin/` | 8 route files |
| XSS via raw HTML string interpolation | `public/`, `admin/` | 4+ functions |
| f-string in logging calls | All modules | 20+ instances |
| Copy-paste log messages | `admin/` | 3 files |
| Dead imports | `admin/`, `public/` | 5+ files |
| Inconsistent error types (`ValueError` vs `LookupError`) | `db/services/` | All 25 services |

### Common Technical Debt

1. **Service layer duplication**: `page_service.py` / `user_page_service.py` (~90%), `qid_service.py` / `qid_others_service.py` (~95%), analytics services (~80%), user-role services (~85%). A broken `_main_service.py` was an abandoned attempt at a generic service.

2. **Admin route duplication**: `translated.py` / `translated_users.py` (~95%), `coordinators.py` / `full_translators.py` / `users_no_inprocess.py` (~85%).

3. **Results logic duplication**: `results_2026.py` / `results_api.py` share `_make_summary()` and `_get_inprocess_*()` with near-identical logic.

4. **PHP-Python parallel codebase**: The same domain logic (missing/exists/inprocess computation) exists in both PHP and Python, sharing the same database. This doubles the maintenance burden.

### Dependency Issues

| Dependency | Concern |
|------------|---------|
| `fix_refs` | External module loaded via `sys.path` manipulation from `FIX_REFS_PY_PATH` env var; graceful fallback exists but removes core functionality |
| `pymysql` | Installed as MySQLdb shim via `pymysql.install_as_MySQLdb()` -- works but is a compatibility hack |
| `mwoauth` | Third-party MediaWiki OAuth library; no version pinning documented |
| `cachetools` | TTL cache for CX tokens; no eviction monitoring |

### Integration Concerns

1. **PHP-Python database coupling**: Both codebases write to the same tables without coordination. The Python app inserts into `pages`; the PHP code reads from it. No migration strategy exists for retiring PHP.

2. **External API dependencies**: The app depends on `mdwiki.org`, `{lang}.wikipedia.org`, `wikidata.org`, and a revids API. No circuit breakers or retry logic exists for any of these.

3. **`fix_refs` module**: Core text processing depends on an external module loaded at runtime via path manipulation. If the module is missing, text processing silently degrades.

---

## Critical Findings

### HIGH-RISK: Missing Admin Route Protection

**8+ admin route files lack `@admin_required`**, allowing unauthenticated users to:

| Route | Impact |
|-------|--------|
| `POST /admin/add/` | Add arbitrary translation records to the database |
| `POST /admin/pages_users_to_main/fix_it` | Promote user pages to main namespace |
| `POST /admin/translated/edit` | Edit or delete published translation records |
| `POST /admin/translated_users/edit` | Edit or delete user-space translations |
| `POST /admin/tt/` and `POST /admin/tt/add` | Modify translate type configurations |
| `POST /admin/qids/` and `POST /admin/qids_others/` | Modify Wikidata QID mappings |
| `GET /admin/reports`, `/process`, `/process_total` | Access admin data without authentication |

**Severity**: Critical. Any internet user can modify application data.

### HIGH-RISK: XSS in HTML Builders

Functions in `results_api.py` and `results_2026.py` construct HTML via f-string interpolation without `html.escape`:

```python
# Unsafe -- code/cat values injected directly into HTML
def _make_summary(code, cat, ...):
    return f'<a href="...">{code}</a>...'  # XSS if code contains HTML
```

While callers currently filter `code` through `get_lang_by_code()`, the functions themselves are unsafe and the filtering is not guaranteed at the function boundary.

**Severity**: High. A crafted `code` parameter could inject arbitrary JavaScript.

### HIGH-RISK: Hardcoded Credentials in PHP

`load_env.php` contains plaintext database credentials (`root11`), OAuth secrets, and encryption keys committed to the repository.

**Severity**: High if the repository is public or credentials are reused.

### MEDIUM-RISK: Rate Limit Bypass

Auth rate limiting trusts `X-Forwarded-For` header, which is trivially spoofable. Combined with `forwarded-allow-ips=*` in gunicorn, any client can bypass the 5/min login and 10/min callback limits.

### MEDIUM-RISK: OAuth State Token Lifetime

`verify_state_token()` uses `settings.cookie.max_age` (designed for long-lived auth cookies) for OAuth state tokens. State tokens should expire in 5-10 minutes to prevent replay attacks.

### MEDIUM-RISK: SQL Error Exposure (PHP)

`mdwiki_sql.php` echoes SQL error messages directly to the browser, leaking database structure and query details.

### LOW-RISK: Broken `_main_service.py`

Contains syntax errors (`db.sessionquery` instead of `db.session.query`) and imports a non-existent `BaseDb` class. Currently unused but indicates an abandoned refactoring effort.

### LOW-RISK: `UnboundLocalError` in `tt.py`

If `int(tt_id_raw)` raises, the except block references `tt_id` which was never assigned, causing a crash.

---

## Strengths

### Strong Engineering Decisions

1. **Frozen dataclass configuration**: `Settings` is immutable, composed of focused sub-configs, and loaded once via `@lru_cache`. This prevents accidental mutation and provides comprehensive type safety.

2. **Cross-dialect testing support**: The `LONGTEXT` TypeDecorator and `TestingConfig` with SQLite in-memory enable fast test execution without MySQL.

3. **View-backed ORM**: Automatic SQL VIEW creation from model metadata (`table.info["is_view"]`) is an elegant solution for complex read models.

4. **Parameterized raw SQL**: All complex queries use `sqlalchemy.text()` with named parameters (`:cat`, `:lang`). Zero SQL injection risk.

5. **Timing-safe secret comparison**: `hmac.compare_digest` for publish secret key validation.

6. **Project whitelist for SSRF prevention**: `text_api.py` validates wiki projects against a regex whitelist before making HTTP requests.

### Reusable Components

1. **`QidsModel`**: A parameterized blueprint class that serves both `qids` and `qids_others` tables -- the best reuse pattern in the codebase.

2. **`admin_required` decorator**: Clean authentication + coordinator check with per-request caching via Flask's `g` object.

3. **Service layer facade**: `db/services/__init__.py` re-exports ~60 functions, providing a clean public API for database operations.

4. **Marshmallow schemas**: `PublishRequestSchema`, `PublishReportsQuerySchema`, and `CXTokenRequestSchema` provide consistent request validation.

### Well-Structured Modules

1. **`config/`** (8.5/10): Cleanest module -- frozen dataclasses, singleton pattern, fail-fast validation.
2. **`src/`** (8/10): Minimal entry points with clear production/development separation.
3. **`shared/`** (7/10): Clean dependency direction (never imports from admin/public), good separation of concerns.

### Good Development Practices

- pytest with fixtures, markers (`@pytest.mark.unit`, `@pytest.mark.network`), and coverage
- Black + isort + ruff for formatting and linting
- Application factory enables test isolation
- CSRF protection via Flask-WTF
- Graceful degradation when `fix_refs` is not installed

---

## Improvement Roadmap

### Immediate Fixes (Security Blockers -- Do Before Next Deploy)

| # | Fix | Effort | Impact |
|---|-----|--------|--------|
| 1 | **Add `@admin_required` to all unprotected admin routes** (8 files) | 1 hour | Closes critical access control gap |
| 2 | **Add `html.escape()` to `_make_summary()` and `_make_mdwiki_cat_url()`** | 30 min | Eliminates XSS vulnerability |
| 3 | **Remove hardcoded credentials from `load_env.php`** | 15 min | Prevents credential exposure |
| 4 | **Replace `echo "sql error:"` with logging in `mdwiki_sql.php`** | 15 min | Stops SQL detail leakage |
| 5 | **Remove `$_COOKIE['test']` debug checks in PHP** | 30 min | Prevents debug info exposure |
| 6 | **Fix rate limiting to use `request.remote_addr`** | 30 min | Closes rate limit bypass |

### Short-term Improvements (1-2 Weeks)

| # | Improvement | Effort | Impact |
|---|-------------|--------|--------|
| 7 | Fix `page_service.py` string key bug (`"word"` -> `PageRecord.word`) | 5 min | Prevents potential SQLAlchemy error |
| 8 | Add try/except with rollback to `report_service.py` | 30 min | Prevents session corruption |
| 9 | Fix `UnboundLocalError` in `tt.py` | 15 min | Prevents admin crash |
| 10 | Fix duplicate flash messages in logout handler | 15 min | Correct user feedback |
| 11 | Fix copy-paste log messages in `full_translators.py` and `users_no_inprocess.py` | 10 min | Correct error reporting |
| 12 | Change `app_context_processor` to `bp_admin.context_processor` | 5 min | Eliminates unnecessary work on non-admin requests |
| 13 | Change 404 handler log level from `ERROR` to `WARNING` | 5 min | Correct log severity |
| 14 | Add 405 Method Not Allowed handler | 15 min | Consistent error responses |
| 15 | Delete stale `routes/admin.py` duplicate | 5 min | Eliminate confusion |
| 16 | Remove dead code: `_main_service.py`, unused imports, commented blocks | 30 min | Reduce noise |
| 17 | Implement separate TTL for OAuth state tokens (5-10 min) | 30 min | Prevents replay attacks |
| 18 | Mask password in `DbConfig.to_dict()` | 5 min | Prevents accidental credential logging |

### Medium-term Improvements (1-2 Months)

| # | Improvement | Effort | Impact |
|---|-------------|--------|--------|
| 19 | **Implement generic `CrudService[ModelT]`** to eliminate 4+ duplicate service pairs | 2-3 days | Eliminates ~2000 lines of duplication |
| 20 | **Refactor `translated.py` / `translated_users.py`** into parameterized class (like `QidsModel`) | 1 day | Eliminates admin route duplication |
| 21 | **Extract shared `_set_record_active_status` pattern** for coordinator/full_translator/users_no_inprocess | 1 day | Eliminates user-role service duplication |
| 22 | **Merge `results_2026.py` and `results_api.py` shared logic** | 1 day | Eliminates results duplication |
| 23 | Split `results_2026.py` (622 lines) into focused modules | 1 day | Improves readability |
| 24 | Standardize exception types across all services (`ValueError` for domain, `LookupError` for not-found) | 1 day | Consistent error handling |
| 25 | Uncomment thread-safety lock in `crypto.py` | 15 min | Thread-safe Fernet initialization |
| 26 | Add pagination to `users_emails.py` dashboard | 2 hours | Prevents memory issues at scale |
| 27 | Add `pyproject.toml` to eliminate `sys.path` manipulation | 2 hours | Proper Python packaging |
| 28 | Add health check endpoint (`/health`) | 30 min | Enables monitoring |
| 29 | Cache `active_coordinators()` per-request using Flask `g` | 30 min | Eliminates per-request DB query |

### Long-term Strategic Refactoring (3-6 Months)

| # | Initiative | Effort | Impact |
|---|-----------|--------|--------|
| 30 | **Complete Python port of PHP results functionality** and deprecate PHP code | 2-3 weeks | Eliminates dual codebase maintenance |
| 31 | **Add database migration scripts (Alembic)** for schema versioning | 1 week | Enables safe schema evolution |
| 32 | **Add comprehensive test coverage** for admin routes and publish workflow | 2 weeks | Prevents regressions |
| 33 | Implement server-side caching for results (Redis or in-memory with TTL) | 1 week | Improves results page performance |
| 34 | Add OpenAPI/Swagger documentation for all `/api/` endpoints | 1 week | Enables frontend integration |
| 35 | Add audit logging for admin mutations | 1 week | Accountability and debugging |
| 36 | Consider SQLAlchemy 2.0 style (`select()` instead of `query()`) | 2 weeks | Future-proofs ORM usage |
| 37 | Add circuit breakers for external API calls (mdwiki.org, wikidata.org) | 1 week | Improves resilience |

### Security Hardening Priorities

| Priority | Action | Current State |
|----------|--------|---------------|
| **P0** | Add `@admin_required` to all admin routes | 8+ files unprotected |
| **P0** | Add `html.escape()` to HTML builders | 4+ functions with XSS |
| **P0** | Remove PHP hardcoded credentials | Plaintext in repository |
| **P1** | Fix rate limit bypass | `X-Forwarded-For` trusted |
| **P1** | Shorten OAuth state token TTL | Uses cookie max_age |
| **P1** | Mask password in `DbConfig.to_dict()` | Exposed in dict |
| **P2** | Remove SQL error echo in PHP | Leaks to browser |
| **P2** | Remove cookie-gated debug output | Anyone can enable |
| **P2** | Document CSRF exemption rationale | Undocumented |
| **P3** | Add CSRF exemption to specific routes only | Entire blueprint exempt |

### DevOps and Testing Recommendations

1. **Add pre-commit hooks**: Run `black`, `isort`, `ruff` before every commit
2. **Add CI pipeline**: pytest + linting on every PR
3. **Add security scanning**: `bandit` for Python, `psalm` for PHP
4. **Add dependency auditing**: `pip-audit` and `composer audit`
5. **Add integration tests**: Verify OAuth flow, publish workflow, admin CRUD end-to-end
6. **Add monitoring**: Health check endpoint, database connection pool metrics, external API latency tracking
7. **Add structured logging**: JSON format for production log aggregation
8. **Add database backups**: Automated daily backups of the toolsdb instance
9. **Document deployment**: Runbook for Toolforge deployment, rollback procedures

---

## Final Evaluation

| Metric | Score | Notes |
|--------|-------|-------|
| **Overall Project Score** | **6/10** | Functional architecture with critical security gaps and heavy duplication |
| **Risk Level** | **High** | Unprotected admin routes allow unauthorized data modification |
| **Technical Debt Level** | **High** | 8+ duplicate file pairs, broken dead code, inconsistent patterns |
| **Production Readiness** | **Conditional** | Core publishing works; admin dashboard needs security hardening before production use |
| **Estimated Effort to Production-Ready** | **2-3 weeks** | P0 security fixes (1 day) + short-term improvements (1 week) + testing (1-2 weeks) |

### Recommended Next Steps

1. **Today**: Apply all 6 immediate security fixes (P0 items)
2. **This week**: Complete short-term improvements (items 7-18)
3. **Next 2 weeks**: Add test coverage for admin routes and publish workflow
4. **Next month**: Begin medium-term refactoring (generic service class, route deduplication)
5. **Next quarter**: Complete PHP-to-Python migration and add Alembic migrations

The codebase has a solid architectural foundation (factory pattern, service layer, frozen config) that would support significant growth. The primary barriers to production readiness are security oversights in the admin layer and accumulated duplication from the PHP porting process. Addressing the P0 security items alone would substantially improve the project's risk profile.
