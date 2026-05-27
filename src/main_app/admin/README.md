# `admin/` -- Admin Dashboard Blueprint

## Project Overview

The `admin` package provides the coordinator-only administrative dashboard for the MDWiki Translation Dashboard. It includes CRUD operations for translations, campaigns, coordinators, QIDs, settings, and various management tools. The admin interface is protected by the `@admin_required` decorator which verifies the user is an active coordinator.

### Main Modules

| File | Purpose |
|------|---------|
| `__init__.py` | Package marker (empty) |
| `decorators.py` | `admin_required` decorator -- authentication + coordinator check |
| `sidebar.py` | HTML sidebar navigation generator for the admin dashboard |
| `routes/__init__.py` | Central blueprint hub -- `bp_admin` definition, sub-blueprint registration, direct routes |
| `routes/admin.py` | Duplicate of `__init__.py` (backup file) |
| `routes/add_translate.py` | Batch-add translation entries |
| `routes/campaigns.py` | Campaign/category CRUD with bulk operations |
| `routes/categories.py` | Categories dashboard (renders template) |
| `routes/coordinators.py` | Coordinator user management |
| `routes/full_translators.py` | Full translator privilege management |
| `routes/language_settings.py` | Per-language text processing settings |
| `routes/last.py` | Recent translations dashboard |
| `routes/pages_users_to_main.py` | Promote user-space pages to main namespace |
| `routes/projects.py` | Project CRUD |
| `routes/settings.py` | Application-wide key-value settings |
| `routes/stat.py` | Simple statistics dashboard |
| `routes/translated.py` | Edit/delete translated pages |
| `routes/translated_users.py` | Edit/delete user-space translations |
| `routes/tt.py` | Translate type (lead/full) management |
| `routes/users_emails.py` | User records with email and group management |
| `routes/users_no_inprocess.py` | Users excluded from in-process workflow |
| `routes/qids/qids.py` | QID table instance |
| `routes/qids/qids_model.py` | Generic reusable QID CRUD blueprint class |
| `routes/qids/qids_others.py` | QID Others table instance |

### Technologies & Dependencies

- **Flask Blueprints** with nested sub-blueprint registration
- **Marshmallow** for request validation (in shared schemas)
- **Flask-WTF** CSRF protection
- **SQLAlchemy** ORM via service layer

## Architecture & Code Quality Review

### Blueprint Hierarchy

```
bp_admin (/admin)
├── add_bp          (/add)
├── campaigns_bp    (/campaigns)
├── coordinators_bp (/coordinators)
├── full_translators_bp (/full_translators)
├── language_settings_bp (/language_settings)
├── pages_users_to_main_bp (/pages_users_to_main)
├── projects_bp     (/projects)
├── settings_bp     (/settings)
├── stat_bp         (/stat)
├── translated_bp   (/translated)
├── translated_users_bp (/translated_users)
├── tt_bp           (/tt)
├── users_emails_bp (/users_emails)
├── users_no_inprocess_bp (/users_no_inprocess)
├── qids_module.bp  (/qids)
└── qids_others_module.bp (/qids_others)
```

### Design Patterns

1. **Module-as-class pattern**: Most route modules (coordinators, full_translators, users_emails, projects, campaigns, settings, language_settings) wrap a Blueprint in a class with `_setup_routes()` called in `__init__`. The class is instantiated at module level and its `.bp` attribute is registered.

2. **Delegation pattern**: Routes delegate to private helper functions (e.g., `_coordinators_dashboard()`, `_add_coordinator()`) separating Flask routing from business logic.

3. **Parameterized blueprint (`QidsModel`)**: A reusable blueprint class parameterized by service, creating identical CRUD behavior for both `qids` and `qids_others` tables.

4. **Consistent error handling**: Mutation routes follow: validate input -> try service call -> catch `ValueError`/`Exception` -> flash message -> redirect.

### Access Control

The `admin_required` decorator in `decorators.py`:
```python
def admin_required(view):
    @functools.wraps(view)
    def wrapped(**kwargs):
        user = current_user()
        if user is None:
            return redirect(url_for("auth.login"))
        if user.username not in _get_cached_active_coordinators():
            abort(403)
        return view(**kwargs)
    return wrapped
```

Coordinators are cached on Flask's `g` object per-request via `_get_cached_active_coordinators()`.

## Strengths

1. **Parameterized CRUD (`QidsModel`)**: Excellent reuse pattern -- a single class serves both `qids` and `qids_others` with different configurations
2. **Consistent error handling**: Most mutation routes properly catch domain errors and flash user-friendly messages
3. **Bulk operations**: Campaigns and translated pages support bulk edit/delete in single form submissions
4. **Sidebar injection**: Automatic sidebar HTML injection via context processor
5. **Access control decorator**: Clean `admin_required` decorator with per-request caching

## Weaknesses

### Missing Access Control (CRITICAL)

Multiple admin routes lack the `@admin_required` decorator, making them accessible to unauthenticated users:

| Route File | Affected Endpoints | Severity |
|------------|-------------------|----------|
| `add_translate.py` | GET + POST `/add/` | **Critical** -- anyone can add translations |
| `pages_users_to_main.py` | All 3 routes | **Critical** -- anyone can promote pages |
| `translated.py` | All 3 routes | **High** -- anyone can edit/delete translations |
| `translated_users.py` | All 3 routes | **High** -- anyone can edit/delete user translations |
| `tt.py` | All 5 routes | **High** -- anyone can modify translate types |
| `qids/qids_model.py` | All 5 routes (both qids) | **High** -- anyone can modify QID mappings |
| `routes/__init__.py` | `/reports`, `/process`, `/process_total` | **Medium** -- data exposure |

### Code Duplication

1. **`translated.py` ~ `translated_users.py`**: ~95% identical structure. Only the service, blueprint name, URL prefix, and template names differ. Both define their own `_safe_int`. This is the most egregious duplication.

2. **`coordinators.py` ~ `full_translators.py` ~ `users_no_inprocess.py`**: All share identical `_set_record_active_status`, `_activate_record`, `_deactivate_record` helper patterns.

3. **`routes/admin.py`**: Identical content to `routes/__init__.py` -- appears to be a stale backup file.

### Context Processor Scope

`inject_sidebar()` is registered as `@bp_admin.app_context_processor` instead of `@bp_admin.context_processor`, causing it to execute on **every request** across the entire application, not just admin routes.

## Critical Issues

### Security

> **Missing `@admin_required` on 8+ route files**: The `add_translate`, `pages_users_to_main`, `translated`, `translated_users`, `tt`, `qids_model`, and several routes in `__init__.py` lack access control. Any visitor can add translations, edit/delete records, and modify QID mappings.

### Bugs

> **`tt.py` line 63 -- `UnboundLocalError`**: If `int(tt_id_raw)` raises at line 56, the except block sets `translate_types = None` but the flash message at line 63 references `tt_id` which was never assigned. This will crash with `UnboundLocalError`.

> **Copy-paste log messages**: `full_translators.py` line 73 and `users_no_inprocess.py` line 73 both log "Unable to {action} coordinator." instead of the correct entity name.

### Dead Code

- `routes/admin.py` is a duplicate of `routes/__init__.py`
- `SidebarItem.admin` field is defined but never consumed
- `SidebarItem.disabled` field is checked but never set to `True`

## Areas That Need Attention

| Area | Priority | Details |
|------|----------|---------|
| Missing `@admin_required` | **Critical** | Apply to all unprotected routes immediately |
| `UnboundLocalError` in `tt.py` | **High** | Fix variable scoping in error handling |
| Code duplication | **Medium** | Refactor translated/translated_users into parameterized class |
| Context processor scope | **Medium** | Change `app_context_processor` to `context_processor` |
| Dead imports | **Low** | `campaigns.py`: unused `get_camp_to_cats`, `get_campaign_category`; `users_emails.py`: unused `get_user_by_username`, `user_exists` |
| Stale backup file | **Low** | Delete `routes/admin.py` |

## Improvement Plan

### Quick Wins (Immediate)
- [ ] **Add `@admin_required` to all unprotected routes** -- this is the highest priority fix
- [ ] Fix `tt.py` `UnboundLocalError` by initializing `tt_id` before the try block
- [ ] Fix copy-paste log messages in `full_translators.py` and `users_no_inprocess.py`
- [ ] Change `app_context_processor` to `bp_admin.context_processor` in `routes/__init__.py`
- [ ] Delete stale `routes/admin.py` duplicate

### Medium-term Improvements
- [ ] Refactor `translated.py` and `translated_users.py` into a parameterized class (like `QidsModel`)
- [ ] Extract shared `_set_record_active_status` pattern into a mixin or base class for coordinator/full_translator/users_no_inprocess
- [ ] Remove dead imports from `campaigns.py` and `users_emails.py`
- [ ] Add error handling to `last.py` service calls

### Long-term Recommendations
- [ ] Create a generic CRUD blueprint factory (extending the `QidsModel` pattern) for all admin entities
- [ ] Add pagination to `users_emails.py` dashboard (currently loads ALL users into memory)
- [ ] Add audit logging for admin mutations (who changed what, when)
- [ ] Add input validation via Marshmallow schemas for all POST endpoints

## Comprehensive Review

| Metric | Score | Notes |
|--------|-------|-------|
| **Overall Rating** | **5/10** | Functional but has critical security gaps and significant duplication |
| **Production Readiness** | **Not ready** | Missing access control on multiple routes is a blocker |
| **Technical Debt** | **High** | Massive code duplication, stale files, copy-paste bugs |
| **Risk Assessment** | **High** | Unprotected admin routes allow unauthorized data modification |
| **Maintainability** | **Medium** | Good patterns exist (QidsModel) but most code is duplicated |
