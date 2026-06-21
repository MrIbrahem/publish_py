# `db/` -- Database Layer

## Project Overview

The `db` package provides the complete database layer for the MDWiki Translation Dashboard. It includes SQLAlchemy ORM models, a service layer with ~60 functions for CRUD operations, database initialization with automatic view creation, and support for both MySQL (production) and SQLite (testing).

### Main Modules

| Directory/File | Purpose |
|----------------|---------|
| `__init__.py` | `init_db()` function -- creates tables and views |
| `models/` | 12 SQLAlchemy model files defining 25+ ORM classes |
| `services/` | 25 service files across 7 subdirectories with ~60 CRUD functions |
| `services/_main_service.py` | Generic DbService (broken/unused) |
| `services/__init__.py` | Facade re-exporting all service functions |

### Technologies & Dependencies

- **Flask-SQLAlchemy** with custom `Base` class providing `to_dict()`
- **SQLAlchemy** ORM with `TypeDecorator` for cross-dialect compatibility
- **Alembic** migration support via naming conventions in metadata
- **PyMySQL** as the MySQL driver (production)
- **SQLite in-memory** for testing

## Architecture & Code Quality Review

### Model Layer

25+ ORM models organized by domain:

| Domain | Models | Tables |
|--------|--------|--------|
| **Pages** | `PageRecord`, `UserPageRecord`, `PagesUsersToMainRecord`, `InProcessRecord` | `pages`, `pages_users`, `pages_users_to_main`, `in_process` |
| **Content** | `CategoryRecord`, `ProjectRecord`, `LangRecord`, `TranslateTypeRecord` | `categories`, `projects`, `langs`, `translate_type` |
| **Analytics** | `AssessmentRecord`, `RefsCountRecord`, `WordRecord`, `EnwikiPageviewRecord`, `ViewsNewRecord`, `ViewsNewAllRecord` | `assessments`, `refs_counts`, `words`, `enwiki_pageviews`, `views_new`, `views_new_all` (VIEW) |
| **Wikidata** | `QidRecord`, `QidOthersRecord`, `AllQidsExistRecord`, `AllArticlesRecord`, `CategoryMemberRecord` | `qids`, `qids_others`, `all_qids_exists`, `all_articles`, `category_members` |
| **Users** | `UserTokenRecord`, `UserRecord`, `UsersNoInprocessRecord`, `CoordinatorRecord`, `FullTranslatorRecord` | `user_tokens`, `users`, `users_no_inprocess`, `coordinators`, `full_translators` |
| **Config** | `SettingRecord`, `LanguageSettingRecord` | `new_settings`, `language_settings` |
| **Reports** | `ReportRecord`, `MdwikiRevidRecord` | `publish_reports`, `mdwiki_revids` |

### Service Layer Pattern

Each service module follows a consistent pattern:

```python
def list_records() -> list[ModelRecord]: ...
def get_record(record_id: int) -> ModelRecord | None: ...
def add_record(field1, field2, ...) -> ModelRecord: ...  # Raises ValueError on duplicate
def add_or_update_record(...) -> ModelRecord: ...         # Upsert
def update_record(record_id: int, **kwargs) -> ModelRecord: ...  # Raises LookupError
def delete_record(record_id: int) -> None: ...            # Raises LookupError
```

Error handling pattern:
- **Insert**: `IntegrityError` -> `ValueError` with rollback
- **Update/Delete**: Re-fetch after operation to verify, raise `LookupError` if not found
- **Post-delete verification**: Nearly all `delete_*` functions re-fetch to confirm deletion

### Database Views

`ViewsNewAllRecord` is backed by a SQL VIEW, created automatically by `init_db()`:

```python
class ViewsNewAllRecord(db.Model):
    __tablename__ = "views_new_all"
    __table_args__ = {
        "info": {
            "is_view": True,
            "create_query": "CREATE VIEW views_new_all AS SELECT ..."
        }
    }
```

The `after_create` event listener in `data_base.py` detects `is_view` and executes the raw SQL.

### Cross-Dialect Support

`LONGTEXT` TypeDecorator:
```python
class LONGTEXT(TypeDecorator):
    impl = Text
    def load_dialect_impl(self, dialect):
        if dialect.name == "mysql":
            return dialect.type_descriptor(MEDIUMBLOB())
        return dialect.type_descriptor(Text())
```

This allows the same models to work with MySQL (production) and SQLite (testing).

### Design Patterns

- **Service-module pattern**: Free functions per table (not classes), taking primitives and returning ORM objects
- **Upsert pattern**: `add_*` (insert-only) vs `add_or_update_*` (find-or-create)
- **Post-delete verification**: Re-fetch after delete to confirm
- **IntegrityError -> ValueError**: Consistent error translation
- **View-backed ORM**: `table.info["is_view"]` + `create_query` for automatic view creation
- **LONGTEXT TypeDecorator**: Cross-dialect MySQL/SQLite compatibility
- **Raw SQL for complex queries**: `missing_stats_service.py`, `results_2026_service.py`, `allqid_service.py` use `sqlalchemy.text()` with parameterized queries

## Strengths

1. **Clean model organization**: Models grouped by domain in separate files
2. **Consistent service pattern**: All services follow the same CRUD template with predictable function signatures
3. **Cross-dialect testing**: `LONGTEXT` TypeDecorator + SQLite in-memory enables fast tests without MySQL
4. **View-backed ORM**: Automatic view creation from model metadata is elegant
5. **Parameterized raw SQL**: Complex queries use `:param` placeholders, no SQL injection risk
6. **`@lru_cache` for coordinator lookup**: `active_coordinators()` is cached with automatic invalidation on mutations

## Weaknesses

### Massive Code Duplication

| Duplication | Similarity | Impact |
|-------------|-----------|--------|
| `page_service.py` ~ `user_page_service.py` | ~90% | Same CRUD functions differing only in model class |
| `qid_service.py` ~ `qid_others_service.py` | ~95% | Every function has a direct counterpart |
| Analytics services (4 files) | ~80% | Same CRUD template with different model/fields |
| User-role services (3 files) | ~85% | Same list/add/delete/activate pattern |

The broken `_main_service.py` was apparently an attempt at a generic service but was never completed.

### Inconsistent Error Handling

- Some services wrap `commit()` in try/except with rollback (e.g., `in_process_service.py`)
- Others do not (e.g., `report_service.py`, `full_translator_service.py` delete)
- Exception types vary: `ValueError` vs `LookupError` vs `UniqueError`

## Critical Issues

### Bugs

> **`_main_service.py` -- Completely broken**: Line 24 has `db.sessionquery(DbRecord)` (missing dot), line 29 has `db.sessionget(DbRecord, _id)` (missing dot), and line 10 imports `BaseDb` which doesn't exist (only `Base` is exported). This file will crash at import time. It appears unused.

> **`page_service.py` line 297 -- String key in update dict**:
> ```python
> .update({PageRecord.target: target, PageRecord.pupdate: pupdate, "word": word})
> ```
> `"word"` is a raw string instead of `PageRecord.word`. SQLAlchemy's `.update()` expects column objects as keys.

> **`report_service.py` -- No rollback on failure**: `add_report()` and `delete_report()` do `db.session.commit()` with no try/except. If commit fails, the session is left in a dirty state.

> **`report_service.py` -- Dead `select_fields` parameter**: `query_reports_with_filters()` accepts `select_fields` but never uses it.

> **`report_service.py` -- `>0` filter is a no-op**: The `>0` filter case does `pass` with commented-out logic.

### Performance

> **`coordinator_service.py` -- `@lru_cache` on DB function**: `active_coordinators()` uses `@functools.lru_cache(maxsize=1)` which caches permanently in the process. While cleared on mutations within the same process, external changes (direct SQL, other processes) leave the cache stale. Also, `lru_cache` on a function querying a scoped session can produce unexpected results in multi-request contexts.

### Code Quality

> **`category_members.py` -- FK commented out**: `ForeignKey("categories.category")` is commented out, meaning referential integrity is not enforced at the DB level.

> **`pages_users_to_main_service.py` naming collision**: Two different files share this name in `pages/` and `reports/` subdirectories. While in different packages, the identical name causes import confusion.

## Areas That Need Attention

| Area | Priority | Details |
|------|----------|---------|
| `_main_service.py` broken code | **High** | Fix or delete -- currently dead code with syntax errors |
| `page_service.py` string key bug | **High** | Replace `"word"` with `PageRecord.word` |
| `report_service.py` missing rollback | **High** | Add try/except with rollback to `add_report` and `delete_report` |
| Code duplication | **Medium** | Implement generic service class to eliminate 4+ duplicate pairs |
| Inconsistent error types | **Medium** | Standardize on `ValueError` for domain errors, `LookupError` for not-found |
| Naming collision | **Low** | Rename one of the `pages_users_to_main_service.py` files |
| `category_members.py` FK | **Low** | Uncomment ForeignKey or document why it's disabled |
| f-string logging | **Low** | Replace with `%s` lazy formatting |

## Improvement Plan

### Quick Wins
- [ ] Fix `page_service.py` line 297: `"word"` -> `PageRecord.word`
- [ ] Add try/except with rollback to `report_service.py` `add_report()` and `delete_report()`
- [ ] Delete or fix `_main_service.py`
- [ ] Remove dead `select_fields` parameter from `query_reports_with_filters()`
- [ ] Fix `>0` filter no-op in `report_service.py`

### Medium-term Improvements
- [ ] Implement a generic `CrudService[ModelT]` class to replace duplicated service modules
- [ ] Standardize exception types across all services
- [ ] Rename `db/services/pages/pages_users_to_main_service.py` to avoid naming collision
- [ ] Replace f-string logging with lazy `%s` formatting

### Long-term Recommendations
- [ ] Add database migration scripts (Alembic) for schema versioning
- [ ] Add connection pooling monitoring and alerting
- [ ] Implement soft deletes for audit-critical tables
- [ ] Add database-level constraints for business rules (e.g., check constraints)
- [ ] Consider SQLAlchemy 2.0 style (`select()` instead of `query()`)

## Comprehensive Review

| Metric | Score | Notes |
|--------|-------|-------|
| **Overall Rating** | **6.5/10** | Good patterns but heavy duplication and some bugs |
| **Production Readiness** | Ready with caveats | Core CRUD works; bugs in report_service and page_service need fixing |
| **Technical Debt** | **High** | Massive duplication, broken _main_service, inconsistent patterns |
| **Risk Assessment** | **Medium** | Missing rollback in report_service could corrupt session state |
| **Maintainability** | **Medium** | Consistent patterns make individual files easy to read, but duplication increases change risk |
