# PHP Behavior Analysis

## Entry Point (`index.php`)

| Parameter | Default     | Source                                                           |
| --------- | ----------- | ---------------------------------------------------------------- |
| `camp`    | `"Hearing"` | `$_GET['camp']` → falls back to `""` → falls back to `"Hearing"` |
| `depth`   | `"1"`       | `$_GET['depth']`                                                 |
| `code`    | `"ar"`      | `$_GET['code']`                                                  |

Response structure:

```json
{
  "execution_time": 0.123,
  "results": { "inprocess": {...}, "exists": {...}, "missing": [...], "ix": "..." }
}
```

## Full Request Flow (`get_results.php:get_results_new`)

```
get_results_new($cat="", $camp, $depth, $code, $filter_sparql=true, $cat2="")
├─ get_lang_pages_by_cat($code, $cat)
│   └─ SQL: SELECT * FROM pages p WHERE p.lang = ? AND p.cat = ? [lang, cat]
│   └─ static cache by "$lang.$cat"
│   └─ re-index by title: array_column(..., null, "title")
│
├─ get_cat_exists_and_missing_new($exists_via_td, $cat, $depth, $code)
│   ├─ if $exists_via_td empty: re-fetch via get_lang_pages_by_cat
│   ├─ get_mdwiki_cat_members($cat, $depth, true)
│   │   └─ (MDWiki API: categorymembers via curl)
│   ├─ $exists = filter $exists_via_td where title IN members
│   ├─ map $exists → {qid, title, target, via:"td", pupdate, user}
│   └─ $missing = array_diff(members, array_keys(exists))
│
├─ exists_by_qids_query($code)
│   └─ SQL: SELECT a.qid, a.title, a.category, t.code, t.target
│   │     FROM all_qids_titles a JOIN all_qids_exists t ON t.qid=a.qid
│   │     WHERE t.code=? AND t.target!='' AND t.target IS NOT NULL
│   └─ static cache by $lang
│   └─ re-index by title
│
├─ exists_expends($items_missing, $exists_targets_before)
│   └─ For each missing title that has a target in the qids data:
│       create {qid, title, target, via:"before"}
│   └─ Returns items_exists dict (keyed by title)
│
├─ Merge: items_missing -= keys(exists_1), items_exists += exists_1
│
├─ filter_items_missing_cat2() [only if $cat2 is set and != $cat]
│   └─ Intersect missing with members of cat2 category
│
├─ getinprocess_n($missing, $code)
│   └─ get_lang_in_process($code)
│   │   └─ SQL: SELECT * FROM in_process WHERE lang = ?
│   │   └─ static cache by $code
│   └─ Filter: only records where title IN missing
│   └─ Returns dict keyed by title
│
├─ Remove in-process from missing: missing = array_diff(...)
│
├─ create_summary($code, $cat, len_inprocess, len_missing, len_exists)
│   └─ HTML string with links to mdwiki.org and wikipedia.org
│
└─ ksort($items_exists) — sort by title (keys)
└─ Return: {inprocess, exists, missing, ix}
```

## Database Schema (Actual Tables & Views)

### `all_qids` table
Referenced by FK from `all_qids_exists`. Contains `qid` as primary key.

### `all_qids_exists` table (DB_NAME_NEW)
```sql
CREATE TABLE all_qids_exists (
    id int NOT NULL AUTO_INCREMENT,
    qid varchar(255) NOT NULL,
    code varchar(25) NOT NULL,
    target varchar(255) NOT NULL,
    PRIMARY KEY (id),
    UNIQUE KEY qid_code (qid, code),
    CONSTRAINT all_qids_exists_ibfk_1 FOREIGN KEY (qid) REFERENCES all_qids (qid)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_unicode_ci;
```

### `all_qids_titles` VIEW (DB_NAME_NEW)
```sql
CREATE VIEW all_qids_titles AS
SELECT
    qq.qid AS qid,
    q.title AS title,
    aa.category AS category
FROM
    all_qids qq
    LEFT JOIN qids q ON qq.qid = q.qid
    LEFT JOIN all_articles aa ON aa.article_id = q.title;
```

### `all_articles` table (DB_NAME_NEW)
```sql
CREATE TABLE all_articles (
    id int NOT NULL AUTO_INCREMENT,
    article_id varchar(255) NOT NULL,
    category varchar(255) DEFAULT NULL,
    PRIMARY KEY (id),
    UNIQUE KEY article_id (article_id)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_unicode_ci;
```

### `qids` table (already mapped by `QidRecord`)
- `id`, `qid` (varchar 20), `title` (varchar 255), `add_date`

### Database Tables Referenced in PHP

| Table / View            | DB Name     | Type    | Columns Used                | Has Python Model?   |
| ----------------------- | ----------- | ------- | --------------------------- | ------------------- |
| `pages`                 | DB_NAME     | TABLE   | `*` (filtered by lang, cat) | `PageRecord` ✓      |
| `in_process`            | DB_NAME_NEW | TABLE   | `*` (filtered by lang)      | `InProcessRecord` ✓ |
| `all_qids_titles`       | DB_NAME_NEW | **VIEW**  | `qid, title, category`      | **MISSING** ✗       |
| `all_qids_exists`       | DB_NAME_NEW | TABLE   | `qid, code, target`         | **MISSING** ✗       |
| `all_qids`              | DB_NAME_NEW | TABLE   | `qid` (FK target)           | **MISSING** ✗       |
| `all_articles`          | DB_NAME_NEW | TABLE   | `article_id, category`      | **MISSING** ✗       |
| `qids`                  | DB_NAME     | TABLE   | `qid, title`                | `QidRecord` ✓       |

**Critical**: `all_qids_titles` is a **VIEW**, not a table. It joins `all_qids` → `qids` → `all_articles`. The PHP code queries the VIEW directly; Python must either:
- A) Register the VIEW definition and query it (requires VIEW to exist in DB)
- B) Replicate the VIEW's JOIN logic as a raw SQL or SQLAlchemy query

### Dead / Unused Parameters in PHP

- `$camp` — passed to `get_results_new` but **never referenced** inside the function
- `$filter_sparql` — passed as `true` but **never referenced**
- `$no_refind` — defined in `super_function` signature but **never referenced**
- The first argument `""` (the `$cat`) passed from `index.php` means the PHP code **only queries pages where `cat = ''`** — this appears to be a refactoring artifact or incomplete campaign-to-category resolution. **The Python implementation MUST resolve `camp` → `category` from the `categories` table.**

### PHP Static Caching (per-request)

- `get_lang_pages_by_cat`: `static $data[$lang.$cat]` — caches by composite key
- `exists_by_qids_query`: `static $data2[$lang]` — caches by language
- `get_lang_in_process`: `static $cache[$code]` — caches by language code
- `CategoryFetcher.fetchCatsMembers`: APCu (operates at process level, not per-request)

### PHP Helper Modules

| Module                | Functions                                                                  | Purpose                                                                  |
| --------------------- | -------------------------------------------------------------------------- | ------------------------------------------------------------------------ |
| `results/helps.php`   | `filter_items_missing_cat2()`, `create_summary()`, `make_mdwiki_cat_url()` | Secondary cat filter + HTML summary generation                           |
| `results/getcats.php` | `CategoryFetcher` class + `get_mdwiki_cat_members()`, `make_options()`     | MDWiki API calls with curl, file cache, depth recursion, title filtering |
| `mdwiki_sql.php`      | `Database` class + `fetch_query()`, `get_dbname()`                         | PDO MySQL wrapper, DB routing by table name                              |

### CategoryFetcher Details

- **Endpoint**: `https://mdwiki.org/w/api.php`
- **Method**: POST with `categorymembers` API
- **Params**: `action=query`, `list=categorymembers`, `cmtitle=Category:<name>`, `cmlimit=max`, `cmtype=page|subcat`
- **Depth**: Recursive — processes subcategories up to `$depth` levels
- **Namespaces kept**: 0 (articles), 14 (Category), 3000 (custom)
- **Filtering**: Removes `File:`, `Template:`, `User:` prefixed titles, removes `(disambiguation)` suffixes
- **User-Agent**: `WikiProjectMed Translation Dashboard/1.0`
- **Timeout**: connect=10s, total=15s
- **Caching**: File cache (`JSON_TABLES_PATH/cats_cash/<cat>.json`) with `{list: [...]}` format OR MW API with APCu
- **Debug mode**: Enabled via `?test` or `test` cookie

## Ambiguities

1. **The `$cat = ""` bug**: Passing empty string as the category means the `pages` query matches `cat = ''` (no pages), and the MW API call returns nothing for an empty category name. The `$camp` value is dead code. **Safe interpretation**: The Python implementation should resolve `$camp` to a real `category` via the `categories` table (which has a `campaign→category` mapping). This is likely the original intent.
2. **`$cat2` filter**: The PHP code has logic for a secondary category filter but index.php passes `""` — this may be used by other callers.
3. **Vague `$no_refind`**: The `super_function` wrapper has this parameter but never uses it.

---

# Python Current State

## `routes.py` (`bp_main.get("/results_api")`)

```python
@bp_main.get("/results_api")
def results_api():
    code = request.args.get("code")      # No default
    camp = request.args.get("camp")      # No default
    depth = request.args.get("depth")    # No default
    result = results_api_result(code, camp, depth)
    return jsonify(result)
```

- CSRF exemption **not set** (CSRF is enabled globally; GET routes are unaffected by default since only POST/PUT/PATCH/DELETE are checked)
- `results_api_result()` currently returns `{}` — **empty stub**

## `results_api.py` (stub)

- Single function `results_api_result(code, camp, depth)` that returns `{}`
- No imports, no logic, no database access
- **All parameters are `None` when omitted** (Flask `.get()` returns `None` by default)

## Currently Available Infrastructure

| Component               | Status                                                                                                                                        |
| ----------------------- | --------------------------------------------------------------------------------------------------------------------------------------------- |
| `PageRecord` model      | ✓ — Includes `title`, `cat`, `lang`, `target`, `pupdate`, `user`, but no `qid` on PageRecord itself (qid is in separate `QidRecord` / `qids` table) |
| `InProcessRecord` model | ✓                                                                                                                                             |
| `CategoryRecord` model  | ✓ — Has `campaign`, `category`, `category2`, `depth` fields                                                                                   |
| `category_service`      | ✓ — Has `get_camp_to_cats()` returning `{campaign: category}` dict                                                                            |
| `in_process_service`    | ✓ — Has `list_in_process_by_lang()`                                                                                                           |
| `page_service`          | ✓ — Has `list_pages()` but no query-by-lang-and-cat                                                                                           |
| `QidRecord` model       | ✓ — Maps to `qids` table (used by the VIEW as `q.title` join)                                                                                |
| `all_qids_titles` VIEW  | ✗ **No model**                                                                                                                                |
| `all_qids_exists` table | ✗ **No model**                                                                                                                                |
| `all_qids` table        | ✗ **No model**                                                                                                                                |
| `all_articles` table    | ✗ **No model**                                                                                                                                |
| MW API client           | ✗ **No equivalent** of `CategoryFetcher`                                                                                                      |
| JSON file cache reader  | ✗ **No equivalent** of `openTablesFile()`                                                                                                     |

## Existing `qid_service.py`

- Has `add_qid`, `update_qid`, `delete_qid`, `get_page_qid`, `list_qids`, `get_title_to_qid`
- Works with `qids` table via `QidRecord`
- **No query for `all_qids_titles` VIEW or `all_qids_exists` table**

---

# Missing Features

1. **Campaign-to-category resolution** — Map `camp` request param to a real `category` string using `categories` table
2. **`get_lang_pages_by_cat`** — Query `pages` table by `lang` and `cat` (missing in `page_service`)
3. **MW API CategoryFetcher** — Fetch category members from `https://mdwiki.org/w/api.php` with depth recursion, file/APCu caching
4. **`all_qids_exists` model** — ORM model for the `all_qids_exists` table
5. **`all_qids` model** — ORM model for the `all_qids` table
6. **`all_articles` model** — ORM model for the `all_articles` table
7. **`all_qids_titles` VIEW model or equivalent query** — Must replicate the VIEW to avoid needing it in all environments
8. **`exists_by_qids_query`** — JOIN query replicating the VIEW + `all_qids_exists`
9. **`exists_expends`** — Logic to retroactively find targets for "missing" pages that have entries in the qids tables
10. **`getinprocess_n`** — Match missing titles against in-process records
11. **`create_summary`** — HTML summary string generation
12. **`filter_items_missing_cat2`** — Secondary category filter (optional, for `cat2` support)
13. **`make_mdwiki_cat_url`** — HTML link generation helper
14. **Static/lru caching** — Per-request in-memory caching (like PHP `static $data`)
15. **Default parameter handling** — PHP's non-null coalescing defaults for `camp`, `depth`, `code`
16. **Response `execution_time` field** — Timing wrapper
17. **CSRF exemption** — For the GET route (probably not needed, but verify)

---

# Behavior Mapping (PHP → Python)

| PHP Function                              | Python Equivalent                                | Notes                                               |
| ----------------------------------------- | ------------------------------------------------ | --------------------------------------------------- |
| `index.php` params/camp default           | `results_api()` in `routes.py`                   | Add defaults, add `camp→cat` resolution, add timing |
| `get_results_new()`                       | `results_api_result()`                           | Main orchestrator                                   |
| `get_lang_pages_by_cat()`                 | `page_service.list_pages_by_lang_cat()`          | New service method                                  |
| `get_cat_exists_and_missing_new()`        | `_get_cat_exists_and_missing()`                  | Private helper                                      |
| `get_mdwiki_cat_members()`                | `category_fetcher.get_mdwiki_cat_members()`      | New service/module using `requests`                 |
| `CategoryFetcher` class                   | `CategoryFetcher` class                          | New class using `requests` + file caching           |
| `make_options()`                          | Inline in constructor                            | Generate options from request/config                |
| `getCatsFromCache()` + `openTablesFile()` | `_get_cats_from_cache()` + `_open_tables_file()` | File-based JSON cache                               |
| `fetchCatsMembersApi()`                   | `_fetch_cats_members_api()`                      | MW API calls via `requests`                         |
| `titlesFilters()`                         | `_titles_filter()`                               | Namespace/disambiguation filter                     |
| `postUrlsMdwiki()`                        | `_post_urls_mdwiki()`                            | `requests.post()` wrapper                           |
| `exists_by_qids_query()`                  | `qid_service.list_targets_by_lang()`             | New service method (replicates VIEW query)          |
| `all_qids_titles` VIEW                    | Raw SQL or replicated JOIN query                 | VIEW does not exist in all environments             |
| `exists_expends()`                        | `_exists_expends()`                              | Private helper                                      |
| `getinprocess_n()`                        | `_get_inprocess_for_titles()`                    | Private helper                                      |
| `get_lang_in_process()`                   | `in_process_service.list_in_process_by_lang()`   | Already exists!                                     |
| `filter_items_missing_cat2()`             | `_filter_items_missing_cat2()`                   | Private helper                                      |
| `create_summary()`                        | `_create_summary()`                              | HTML string builder                                 |
| `make_mdwiki_cat_url()`                   | `_make_mdwiki_cat_url()`                         | URL + HTML link builder                             |
| `get_dbname()`                            | Built into SQLAlchemy engine config              | Route to appropriate DB via engine config           |
| `Database` class                          | `get_session()`                                  | Already uses SQLAlchemy `Session`                   |

---

# Recommended Python Architecture

## Directory Layout

```
src/sqlalchemy_app/
├── public/
│   └── routes/
│       └── main/
│           ├── routes.py            # Route registration (barely changed)
│           └── results_api.py       # Main orchestrator + helpers
├── shared/
│   └── services/
│       ├── page_service.py          # Add list_pages_by_lang_cat()
│       ├── in_process_service.py    # Already has list_in_process_by_lang()
│       ├── category_service.py      # Already has get_camp_to_cats()
│       └── mediawiki_api.py         # NEW: CategoryFetcher replacement
├── sqlalchemy_models/
│   ├── __init__.py                  # Add new models
│   ├── qid.py                      # Add AllQidsExistRecord, AllQidsRecord
│   └── all_articles.py             # NEW: AllArticlesRecord
```

## Models to Add

### `AllQidsExistRecord` (in `sqlalchemy_models/qid.py`)
```python
class AllQidsExistRecord(BaseDb):
    """Maps to all_qids_exists table in DB_NAME_NEW."""
    __tablename__ = "all_qids_exists"
    __table_args__ = {"info": {"db_name": "DB_NAME_NEW"}}

    id = Column(Integer, primary_key=True, autoincrement=True)
    qid = Column(String(255), nullable=False)
    code = Column(String(25), nullable=False)
    target = Column(String(255), nullable=False)
```

### `AllQidsRecord` (in `sqlalchemy_models/qid.py`)
```python
class AllQidsRecord(BaseDb):
    """Maps to all_qids table in DB_NAME_NEW."""
    __tablename__ = "all_qids"
    __table_args__ = {"info": {"db_name": "DB_NAME_NEW"}}

    qid = Column(String(255), primary_key=True)
```

### `AllArticlesRecord` (in `sqlalchemy_models/all_articles.py`)
```python
class AllArticlesRecord(BaseDb):
    """Maps to all_articles table in DB_NAME_NEW."""
    __tablename__ = "all_articles"
    __table_args__ = {"info": {"db_name": "DB_NAME_NEW"}}

    id = Column(Integer, primary_key=True, autoincrement=True)
    article_id = Column(String(255), nullable=False, unique=True)
    category = Column(String(255), nullable=True)
```

### `all_qids_titles` — NOT a table model

Do NOT create `AllQidsTitleRecord` as a table model. Instead, replicate the VIEW logic in a query or use raw SQL:

**Option A — Raw SQL (simplest, matches PHP exactly):**
```python
def list_targets_by_lang(lang: str) -> List[dict]:
    """Replicates: SELECT a.qid, a.title, a.category, t.code, t.target
       FROM all_qids_titles a JOIN all_qids_exists t ON t.qid = a.qid
       WHERE t.code = ? AND t.target != '' AND t.target IS NOT NULL"""
    sql = """
        SELECT qq.qid AS qid, q.title AS title, aa.category AS category,
               t.code AS code, t.target AS target
        FROM all_qids qq
        LEFT JOIN qids q ON qq.qid = q.qid
        LEFT JOIN all_articles aa ON aa.article_id = q.title
        JOIN all_qids_exists t ON t.qid = qq.qid
        WHERE t.code = :lang
          AND t.target != '' AND t.target IS NOT NULL
    """
    with get_session() as session:
        result = session.execute(text(sql), {"lang": lang})
        rows = result.fetchall()
        return [dict(row._mapping) for row in rows]
```

**Option B — VIEW model with `is_view=True` (preferred if VIEW exists in target DB):**
```python
class AllQidsTitleRecord(BaseDb):
    __tablename__ = "all_qids_titles"
    __table_args__ = {
        "info": {
            "is_view": True,
            "create_query": """
                CREATE VIEW all_qids_titles AS
                SELECT qq.qid, q.title, aa.category
                FROM all_qids qq
                LEFT JOIN qids q ON qq.qid = q.qid
                LEFT JOIN all_articles aa ON aa.article_id = q.title
            """
        }
    }
    qid = Column(String(255), primary_key=True)
    title = Column(String(255))
    category = Column(String(255))
```
Then query:
```python
session.query(AllQidsTitleRecord.qid, AllQidsTitleRecord.title, ...)
    .join(AllQidsExistRecord, AllQidsExistRecord.qid == AllQidsTitleRecord.qid)
    .filter(...)
```

**Recommendation**: Use Option A (raw SQL) — it does not depend on the VIEW existing in all environments and exactly replicates the PHP behavior.

### Multi-Database Handling

The `all_qids_*` tables and `all_articles` are in `DB_NAME_NEW`. The existing engine connects to a single database. You have two options:

**Option 1**: Add all `DB_NAME_NEW` tables to a **second engine** in `engine.py`:
```python
def build_db_url_new(db_data):
    return f"mysql+pymysql://{db_data.db_user}:{db_data.db_password}@{db_data.db_host}/{os.getenv('TOOL_TOOLSDB_DBNAME_NEW', db_data.db_name + '_new')}"
```

**Option 2**: If both databases are on the same host and the tables are accessible from the main DB connection, just add them to the same metadata. **Check this first** — the `get_dbname()` PHP function routes `all_qids_titles` and `all_qids_exists` to `DB_NAME_NEW` which suggests a separate database.

## New/Modified Service Functions

### `page_service.py` — Add:
```python
def list_pages_by_lang_cat(lang: str, cat: str) -> List[PageRecord]:
    with get_session() as session:
        return (
            session.query(PageRecord)
            .filter(PageRecord.lang == lang, PageRecord.cat == cat)
            .all()
        )
```

### `qid_service.py` — Add:
```python
def list_targets_by_lang(lang: str) -> List[dict]:
    """Replicate all_qids_titles VIEW + JOIN with all_qids_exists.

    Equivalent PHP SQL:
    SELECT a.qid, a.title, a.category, t.code, t.target
    FROM all_qids_titles a JOIN all_qids_exists t ON t.qid = a.qid
    WHERE t.code = ? AND t.target != '' AND t.target IS NOT NULL
    """
    sql = text("""
        SELECT qq.qid AS qid, q.title AS title, aa.category AS category,
               t.code AS code, t.target AS target
        FROM all_qids qq
        LEFT JOIN qids q ON qq.qid = q.qid
        LEFT JOIN all_articles aa ON aa.article_id = q.title
        JOIN all_qids_exists t ON t.qid = qq.qid
        WHERE t.code = :lang
          AND t.target != '' AND t.target IS NOT NULL
    """)
    with get_session() as session:
        rows = session.execute(sql, {"lang": lang}).fetchall()
        return [dict(row._mapping) for row in rows]
```

### New Module: `mediawiki_api.py`
```python
class CategoryFetcher:
    def __init__(self, options: dict, endpoint: str = "https://mdwiki.org/w/api.php"): ...
    def get_mdwiki_cat_members(self, root_cat: str, depth: int = 0, use_cache: bool = True) -> list[str]: ...

    # Private:
    def _get_cats_members(self, cat: str, use_cache: bool) -> list[str]: ...
    def _fetch_cats_members_api(self, cat: str) -> list[str]: ...
    def _get_cats_from_cache(self, cat: str) -> list: ...
    def _open_tables_file(self, cat: str) -> dict: ...
    def _titles_filter(self, titles: list[str]) -> list[str]: ...
    def _post_urls_mdwiki(self, params: dict) -> dict: ...
```

---

# Step-by-Step Migration Plan

## Phase 1: Data Layer — Models & Queries

1. **Add `AllQidsExistRecord` model** in `sqlalchemy_models/qid.py`
2. **Add `AllQidsRecord` model** in `sqlalchemy_models/qid.py`
3. **Add `AllArticlesRecord` model** in `sqlalchemy_models/all_articles.py`
4. **Add `list_pages_by_lang_cat(lang, cat)`** to `page_service.py`
5. **Add `list_targets_by_lang(lang)`** to `qid_service.py` — raw SQL replicating the VIEW + JOIN
6. **Update `__init__.py`** of `sqlalchemy_models` and `shared/services/` to export new classes

## Phase 2: MW API Client

7. **Create `mediawiki_api.py`** in `shared/services/`
8. Implement `CategoryFetcher` class with:
   - `__init__(options, endpoint)`
   - `get_mdwiki_cat_members(root_cat, depth, use_cache)` — BFS depth recursion
   - `_fetch_cats_members_api(cat)` — `requests.post()` with pagination (`cmcontinue`)
   - `_titles_filter(titles)` — strip `File:`, `Template:`, `User:`, `(disambiguation)`
   - File cache reader (`_open_tables_file`) — reads from `JSON_TABLES_PATH` env var
   - User-Agent from `settings.user_agent`
9. Write `get_mdwiki_cat_members(cat, depth, use_cache)` standalone function

## Phase 3: Orchestrator Logic

10. **Rewrite `results_api.py`** with the full orchestrator:
    - `results_api_result(code, camp, depth)` → entry point
    - `_resolve_campaign_to_category(camp)` — looks up `categories` table
    - `_get_lang_pages_by_cat(lang, cat)` — wraps `page_service`, adds per-request cache
    - `_get_cat_exists_and_missing(existing, cat, depth, code)` — core matching logic
    - `_get_exists_targets_by_lang(code)` — wraps new `qid_service` method, adds cache
    - `_exists_expends(missing, targets)` — retroactive target matching
    - `_get_inprocess_for_titles(missing, code)` — wraps existing `in_process_service`
    - `_create_summary(code, cat, inprocess_count, missing_count, exists_count)` — HTML builder
    - `_make_mdwiki_cat_url(category)` — HTML link builder

## Phase 4: Route & Defaults

11. **Update `routes.py`** — add default values, timing, `jsonify` with proper structure

## Phase 5: Multi-Database Engine

12. **If `all_qids_*` tables are on a different host/db**: Add second engine in `engine.py`, create `get_session_new()` context manager, or use SQLAlchemy `binds` on the engine.

## Phase 6: Testing

13. Write unit tests with mock/fake DB and mock MW API
14. Write integration tests against captured PHP response snapshots

---

# Edge Cases

| Edge Case                                 | PHP Behavior                                                                                                                            | Python Handling                                                                  |
| ----------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------- |
| `camp` not provided                       | Defaults to `"Hearing"`                                                                                                                 | Same — fallback to `"Hearing"`                                                   |
| `camp` unknown (no category)              | Queries `cat = "Hearing"` literally, likely returns empty                                                                               | Log warning, fall back to using campaign string as category name (or raise)      |
| `depth = 0`                               | Only root category members (no subcats)                                                                                                 | Same — `while depth > depth_done`                                                |
| `depth = negative` or non-numeric         | PHP coerce via `(int) $depth`, negative clamped to 0                                                                                    | `max(0, int(depth))`                                                             |
| `code` not provided                       | Defaults to `"ar"`                                                                                                                      | Same                                                                             |
| `code` invalid (no `pages` records)       | Empty `$exists_via_td`, then `get_cat_exists_and_missing` refetches (still empty), `get_mdwiki_cat_members` still runs for the category | Empty pages query, still fetch category members, result = all members as missing |
| `exists_via_td` has duplicate titles      | `array_column(..., null, "title")` dedup by last wins                                                                                   | Explicit dict construction: `{r.title: r for r in results}`                      |
| Missing list has duplicates               | `array_unique` then `array_values`                                                                                                      | `list(dict.fromkeys(...))`                                                       |
| `exists_targets_before` has no matches    | Returns `[]`, skipped merge                                                                                                             | Empty dict, skip                                                                 |
| Category has subcategories at depth > 1   | Recursively fetches subcat members, filters namespaced titles                                                                           | Same BFS approach                                                                |
| MW API returns HTTP error                 | Returns empty array, logs                                                                                                               | Returns empty list, logs                                                         |
| File cache missing or corrupt             | Returns empty array, logs                                                                                                               | Same                                                                             |
| `in_process` has no records for this lang | Returns empty array                                                                                                                     | Returns empty dict                                                               |
| in_process record title not in missing    | Filtered out by `in_array` check                                                                                                        | Dict comprehension filtering                                                     |
| Edge: `$cat2` filtering                   | PHP `filter_items_missing_cat2` — intersect with another cat's members                                                                  | Implement for parity, gate on non-empty `cat2` param                             |
| `all_qids_titles` VIEW not accessible     | N/A (VIEW exists in PHP env)                                                                                                            | Must replicate VIEW logic via raw SQL in service layer                           |

---

# Testing Strategy

## 1. Snapshot Testing (PHP → Python Parity)

Capture real PHP responses:

```python
# tests/test_services/test_results_api.py

PHP_RESPONSE_EXISTS = {
    "exists": {
        "Abdominal thrusts": {"qid": "Q133005500", "title": "Abdominal thrusts", ...},
    },
    "missing": ["ACL tear", "Acute pancreatitis"],
    "inprocess": {"Some title": { "id": 1, "title": "Some title", ... }},
    "ix": "Found 100 pages in <a ...>Category</a>, ..."
}
```

Test with:
- Known `camp` → resolved category
- Known `code` (e.g., `"ar"`)
- Specific `depth`

## 2. Test Isolation

| Dependency               | Isolation Strategy                                   |
| ------------------------ | ---------------------------------------------------- |
| `pages` table            | In-memory SQLite with `PageRecord` fixture data      |
| `in_process` table       | In-memory SQLite with `InProcessRecord` fixture data |
| `qids` table             | In-memory SQLite with `QidRecord` fixture data       |
| `all_qids_exists` table  | In-memory SQLite with fixture data                   |
| `all_qids` table         | In-memory SQLite with fixture data                   |
| `all_articles` table     | In-memory SQLite with fixture data                   |
| `categories` table       | In-memory SQLite with `CategoryRecord` fixture data  |
| MW API (CategoryFetcher) | Monkeypatch `requests.post` to return fixture JSON   |
| File cache               | Monkeypatch or test both paths (cache hit/miss)      |
| `execution_time`         | Approximate match (assert > 0)                       |

**Important for VIEW query testing**: The `list_targets_by_lang` service uses raw SQL that replicates the VIEW. Test this with fixture data in the three underlying tables (`all_qids`, `qids`, `all_articles`) — no VIEW needed.

## 3. Test Matrix

| Test               | Code   | Camp            | Depth | Expected                                 |
| ------------------ | ------ | --------------- | ----- | ---------------------------------------- |
| All defaults       | None   | None            | None  | `code="ar"`, `camp="Hearing"`, `depth=1` |
| Explicit params    | `"es"` | `"RTT"`         | `"2"` | Exact match                              |
| Empty pages table  | `"xx"` | `"Hearing"`     | `"1"` | All members as missing                   |
| Cat2 filter active | `"ar"` | `"Hearing"`     | `"1"` | Filtered by secondary cat                |
| Depth 0            | `"ar"` | `"RTT"`         | `"0"` | No subcategory recursion                 |
| No MW API members  | `"ar"` | `"NonExistent"` | `"1"` | All pages as exists, none missing        |

## 4. Key Assertions

```python
def test_response_structure(result):
    assert "inprocess" in result["results"]
    assert "exists" in result["results"]
    assert "missing" in result["results"]
    assert "ix" in result["results"]
    assert "execution_time" in result
    assert isinstance(result["results"]["missing"], list)
    assert isinstance(result["results"]["inprocess"], dict)
    assert isinstance(result["results"]["exists"], dict)
    # ix contains HTML link to mdwiki.org
    assert "mdwiki.org" in result["results"]["ix"]
    # exists items sorted alphabetically by key
    keys = list(result["results"]["exists"].keys())
    assert keys == sorted(keys)
```

---

# Suggested Final Function Layout

## `results_api.py`

```python
"""Results API — mirrors PHP Results\GetResults\get_results_new."""

from __future__ import annotations

import logging
import time
from typing import Any

from flask import g

from ...shared.services.category_service import get_camp_to_cats
from ...shared.services.in_process_service import list_in_process_by_lang
from ...shared.services.page_service import list_pages_by_lang_cat
from ...shared.services.qid_service import list_targets_by_lang
from .mediawiki_api import get_mdwiki_cat_members

logger = logging.getLogger(__name__)


def results_api_result(
    code: str | None,
    camp: str | None,
    depth: str | None,
    cat2: str | None = None,
) -> dict[str, Any]:
    code = code or "ar"
    camp = camp or "Hearing"
    depth_int = max(0, int(depth or 1))

    cat = _resolve_campaign_to_category(camp)

    pages = _get_lang_pages_by_cat(code, cat)
    pages_by_title = {p.title: p for p in pages}

    items_exists, items_missing = _get_cat_exists_and_missing(
        pages_by_title, cat, depth_int, code
    )

    targets = _get_exists_targets_by_lang(code)
    extra_exists = _exists_expends(items_missing, targets)

    if extra_exists:
        items_exists.update(extra_exists)
        items_missing = [t for t in items_missing if t not in extra_exists]

    missing = _unique_ordered(items_missing)

    inprocess = _get_inprocess_for_titles(missing, code)
    in_titles = set(inprocess)
    missing = [t for t in missing if t not in in_titles]

    summary = _make_summary(code, cat, len(inprocess), len(missing), len(items_exists))

    return {
        "inprocess": inprocess,
        "exists": dict(sorted(items_exists.items())),
        "missing": missing,
        "ix": summary,
    }


def _resolve_campaign_to_category(camp: str) -> str:
    cats = get_camp_to_cats()
    return cats.get(camp, camp)


def _get_lang_pages_by_cat(lang: str, cat: str) -> list:
    key = f"lang_pages_{lang}_{cat}"
    if key in g:
        return g[key]
    result = list_pages_by_lang_cat(lang, cat)
    g[key] = result
    return result


def _get_cat_exists_and_missing(
    pages_by_title: dict[str, Any],
    cat: str,
    depth: int,
    code: str,
) -> tuple[dict, list]:
    if not pages_by_title:
        pages_by_title = {p.title: p for p in _get_lang_pages_by_cat(code, cat)}

    members = get_mdwiki_cat_members(cat, depth, use_cache=True)
    member_set = set(members)

    exists = {}
    for title, page in pages_by_title.items():
        if title in member_set:
            exists[title] = {
                "qid": getattr(page, "qid", "") or "",
                "title": page.title or "",
                "target": page.target or "",
                "via": "td",
                "pupdate": page.pupdate or "",
                "user": page.user or "",
            }

    missing = list(member_set - set(exists.keys()))

    return exists, missing


def _get_exists_targets_by_lang(lang: str) -> dict[str, dict]:
    key = f"exists_targets_{lang}"
    if key in g:
        return g[key]
    rows = list_targets_by_lang(lang)
    result = {row["title"]: row for row in rows}
    g[key] = result
    return result


def _exists_expends(
    missing: list[str],
    targets: dict[str, dict],
) -> dict[str, dict]:
    result = {}
    for title in missing:
        entry = targets.get(title)
        if entry and entry.get("target"):
            result[title] = {
                "qid": entry.get("qid", ""),
                "title": entry.get("title", ""),
                "target": entry["target"],
                "via": "before",
            }
    return result


def _get_inprocess_for_titles(missing: list[str], code: str) -> dict[str, dict]:
    key = f"inprocess_{code}"
    if key in g:
        records = g[key]
    else:
        records = list_in_process_by_lang(code)
        g[key] = records

    missing_set = set(missing)
    return {
        r.title: {
            "id": r.id,
            "title": r.title,
            "user": r.user,
            "lang": r.lang,
            "cat": r.cat,
            "translate_type": r.translate_type,
            "word": r.word,
            "add_date": r.add_date.isoformat() if r.add_date else None,
        }
        for r in records
        if r.title in missing_set
    }


def _unique_ordered(items: list[str]) -> list[str]:
    seen = set()
    result = []
    for item in items:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return result


def _make_mdwiki_cat_url(category: str, name: str | None = None) -> str:
    if not category:
        return ""
    clean = category.replace("Category:", "")
    display = name or clean
    from urllib.parse import quote
    encoded = quote(clean.replace(" ", "_"), safe="")
    return (
        f"<a target='_blank' "
        f"href='https://mdwiki.org/wiki/Category:{encoded}'>{display}</a>"
    )


def _make_summary(
    code: str, cat: str, inprocess_count: int, missing_count: int, exists_count: int
) -> str:
    total = exists_count + missing_count + inprocess_count
    cat_url = _make_mdwiki_cat_url(cat, "Category")
    return (
        f"Found {total} pages in {cat_url}, "
        f"{exists_count} exists, and {missing_count} missing in "
        f"(<a href='https://{code}.wikipedia.org' "
        f"target='_blank'>{code}</a>), "
        f"{inprocess_count} In process."
    )
```

## `routes.py` (updated route)

```python
@bp_main.get("/results_api")
def results_api():
    code = request.args.get("code")
    camp = request.args.get("camp")
    depth = request.args.get("depth")

    start = time.time()
    result_dict = results_api_result(code, camp, depth)
    elapsed = time.time() - start

    return jsonify({
        "execution_time": round(elapsed, 6),
        "results": result_dict,
    })
```

## `mediawiki_api.py` (new file)

```python
"""MediaWiki API client for fetching category members (PHP CategoryFetcher port)."""

from __future__ import annotations

import json
import logging
import os
import re
from pathlib import Path
from typing import Any

import requests

from ..config import settings

logger = logging.getLogger(__name__)

USER_AGENT = settings.user_agent
DEFAULT_ENDPOINT = "https://mdwiki.org/w/api.php"
NS_MAIN = 0
NS_CATEGORY = 14
NS_CUSTOM = 3000


class CategoryFetcher:
    def __init__(
        self,
        options: dict[str, Any] | None = None,
        endpoint: str = "",
    ):
        self.options = options or {}
        self.endpoint = endpoint or DEFAULT_ENDPOINT
        self.debug = bool(self.options.get("debug", False))
        self.connect_timeout = self.options.get("connect_timeout", 10)
        self.timeout = self.options.get("timeout", 15)
        self.tables_dir = self.options.get("tablesDir", "")

    def get_mdwiki_cat_members(
        self, root_cat: str, depth: int = 0, use_cache: bool = True
    ) -> list[str]:
        depth = max(0, depth)
        titles: list[str] = []
        cats: list[str] = [root_cat]
        depth_done = -1

        while cats and depth > depth_done:
            next_cats: list[str] = []
            for cat in cats:
                all_titles = self._get_cats_members(cat, use_cache)
                for title in all_titles:
                    if title.startswith("Category:"):
                        next_cats.append(title)
                    else:
                        titles.append(title)
            depth_done += 1
            cats = next_cats

        titles = list(dict.fromkeys(titles))
        return self._titles_filter(titles)

    def _get_cats_members(self, cat: str, use_cache: bool) -> list[str]:
        all_items: list[str] = []
        if use_cache:
            all_items = self._get_cats_from_cache(cat)
        if not all_items:
            all_items = self._fetch_cats_members_api(cat)
        return all_items

    def _fetch_cats_members_api(self, cat: str) -> list[str]:
        if not cat.startswith("Category:"):
            cat = f"Category:{cat}"

        params: dict[str, str] = {
            "action": "query",
            "list": "categorymembers",
            "cmtitle": cat,
            "cmlimit": "max",
            "cmtype": "page|subcat",
            "format": "json",
        }

        items: list[str] = []
        cmcontinue: str | None = "x"
        iteration = 0
        max_iterations = 100

        while cmcontinue and iteration < max_iterations:
            iteration += 1
            if cmcontinue != "x":
                params["cmcontinue"] = cmcontinue

            data = self._post_urls_mdwiki(params)
            query = data.get("query", {})
            members = query.get("categorymembers", [])
            if not members:
                break

            cmcontinue = data.get("continue", {}).get("cmcontinue", "")

            for page in members:
                ns = page.get("ns", -1)
                if ns in (NS_MAIN, NS_CATEGORY, NS_CUSTOM):
                    items.append(page["title"])

        if iteration >= max_iterations:
            logger.warning("fetch_cats_members_api: Hit maximum iterations for '%s'", cat)

        return items

    def _get_cats_from_cache(self, cat: str) -> list[str]:
        if self.options.get("nocache"):
            return []
        data = self._open_tables_file(cat)
        if not data:
            return []
        lst = data.get("list")
        if not isinstance(lst, list):
            return []
        return lst

    def _open_tables_file(self, cat: str) -> dict | None:
        if not self.tables_dir:
            return None
        safe_cat = cat.replace("/", "").replace("\\", "").replace("..", "")
        file_path = Path(self.tables_dir) / "cats_cash" / f"{safe_cat}.json"
        if not file_path.is_file():
            return None
        try:
            with open(file_path, encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError) as e:
            logger.warning("Failed to read cache file %s: %s", file_path, e)
            return None

    def _titles_filter(self, titles: list[str]) -> list[str]:
        pattern = re.compile(r"^(File|Template|User):")
        disambig = re.compile(r"\(disambiguation\)$")
        result = []
        for t in titles:
            if not isinstance(t, str):
                continue
            if pattern.match(t):
                continue
            if disambig.search(t):
                continue
            result.append(t)
        return result

    def _post_urls_mdwiki(self, params: dict) -> dict:
        resp = requests.post(
            self.endpoint,
            data=params,
            headers={"User-Agent": USER_AGENT},
            timeout=(self.connect_timeout, self.timeout),
        )
        resp.raise_for_status()
        return resp.json()


def get_mdwiki_cat_members(cat: str, depth: int = 0, use_cache: bool = True) -> list[str]:
    options = {
        "tablesDir": os.getenv("JSON_TABLES_PATH", ""),
    }
    fetcher = CategoryFetcher(options)
    return fetcher.get_mdwiki_cat_members(cat, depth, use_cache)
```

## `page_service.py` — Add

```python
def list_pages_by_lang_cat(lang: str, cat: str) -> List[PageRecord]:
    with get_session() as session:
        return (
            session.query(PageRecord)
            .filter(PageRecord.lang == lang, PageRecord.cat == cat)
            .all()
        )
```

## `qid_service.py` — Add

```python
def list_targets_by_lang(lang: str) -> List[dict]:
    """Replicate all_qids_titles VIEW + JOIN with all_qids_exists.

    Equivalent PHP SQL:
    SELECT a.qid, a.title, a.category, t.code, t.target
    FROM all_qids_titles a JOIN all_qids_exists t ON t.qid = a.qid
    WHERE t.code = ? AND t.target != '' AND t.target IS NOT NULL
    """
    sql = text("""
        SELECT qq.qid AS qid, q.title AS title, aa.category AS category,
               t.code AS code, t.target AS target
        FROM all_qids qq
        LEFT JOIN qids q ON qq.qid = q.qid
        LEFT JOIN all_articles aa ON aa.article_id = q.title
        JOIN all_qids_exists t ON t.qid = qq.qid
        WHERE t.code = :lang
          AND t.target != '' AND t.target IS NOT NULL
    """)
    with get_session() as session:
        rows = session.execute(sql, {"lang": lang}).fetchall()
        return [dict(row._mapping) for row in rows]
```

---

# Key Migration Notes

| Concern | Detail |
|---------|--------|
| **Flask routing** | GET route, no CSRF check — keep as `@bp_main.get(...)`. No changes needed. |
| **SQLAlchemy integration** | Use existing `get_session()` pattern. `all_qids_*` tables may be in `DB_NAME_NEW` — if on a different host/database, add a second engine. |
| **VIEW handling** | `all_qids_titles` is a VIEW. Do NOT model it as a table. Use raw `text()` SQL replicating the VIEW's JOIN logic in the service layer. This avoids depending on the VIEW existing in dev/test. |
| **Serialization** | PHP `json_encode` converts assoc arrays → JSON objects, indexed arrays → JSON arrays. Python `jsonify` does the same for dicts vs lists. Ensure `exists` and `inprocess` are `dict` (not `list`), `missing` is `list`. |
| **Execution time** | PHP uses `microtime(true)`. Python uses `time.time()`. Wrap in `round(..., 6)`. |
| **HTML in JSON** | PHP stores raw HTML in `ix` field. Python should store the same HTML string. Flask `jsonify` passes strings raw — verify no double-escaping. |
| **Recursion/perf** | `CategoryFetcher` makes HTTP calls per category per depth level. Add `timeout`, limit max iterations (PHP uses 100). Consider caching MW API responses. |
| **File cache path** | From env `JSON_TABLES_PATH` (PHP: `JSON_TABLES_PATH`). Python config has `paths.words_json_path` but not `JSON_TABLES_PATH`. May need to add this env var to config. |
| **`qids` vs `all_qids`** | `qids` table (mapped by `QidRecord`) is in DB_NAME. `all_qids` table is in DB_NAME_NEW and has a different schema. They are separate tables. |
| **`PageRecord` has no `qid`** | The `qid` field referenced in PHP's `get_cat_exists_and_missing_new` comes from the `pages` table. Check if `pages` table has a `qid` column — the existing `PageRecord` model does not include `qid`. If the `pages` table has a `qid` column, add it to `PageRecord`. |
