# Prompt: Implement Admin Blueprint Routes

## Context & Goal

We are building a Flask admin blueprint (`admin_bp`) that mirrors a set of PHP admin pages.
Use the existing `add_translate` route (`src/main_app/admin/routes/add_translate.py`) as the
canonical pattern for **all** new routes — Blueprint setup, GET/POST split, service calls,
`flash()` + `redirect()`, and form field parsing.

---

## Reference Pattern (add_translate)

```python
add_bp = Blueprint("add", __name__, url_prefix="/add")

@add_bp.route("/", methods=["GET"])
def add_translate() -> str:
    categories = list_categories()
    return render_template("admins/add_translate.html", categories=categories)

@add_bp.route("/", methods=["POST"])
def add_translate_post() -> ResponseReturnValue:
    titles = request.form.getlist("mdtitle")
    # ... parse flat lists, not PHP rows[N][field] dicts ...
    for i in range(len(titles)):
        result = add_translate_row_to_db(...)
        if result:
            flash("...", "success")
        else:
            flash("...", "danger")
    return redirect(url_for("admin.add.add_translate"))
```

**Form field convention:** PHP sends `rows[2][mdtitle]`, `rows[2][cat]`, etc.
Flask forms use flat names: `mdtitle`, `cat`, `type`, … parsed with `request.form.getlist(...)`.

---

## Route Overview Table

| Route                       | PHP source dir                                | Blueprint name           | Service(s)                    | DB table(s) touched                                                 | Has POST?                 |
| --------------------------- | --------------------------------------------- | ------------------------ | ----------------------------- | ------------------------------------------------------------------- | ------------------------- |
| `admin/tt`                  | `coordinator/admin/tt/*.php`                  | `tt_bp`                  | `translate_type_service`      | `translate_type`, `qids` (read-only for new-title detection)        | **Yes** (insert/update)   |
| `admin/translated`          | `coordinator/admin/translated/*.php`          | `translated_bp`          | `page_service`                | `pages`                                                             | **Yes** (update + delete) |
| `admin/translated_users`    | `coordinator/admin/translated/*.php`          | `translated_users_bp`    | `user_page_service`           | `pages_users`                                                       | **Yes** (update + delete) |
| `admin/qids`                | `coordinator/admin/qids/*.php`                | `qids_bp`                | `qid_service`                 | `qids`                                                              | **Yes** (insert/update)   |
| `admin/qids_others`         | same `coordinator/admin/qids/*.php`           | `qids_others_bp`         | `qid_others_service`          | `qids_others`                                                       | **Yes** (insert/update)   |
| `admin/pages_users_to_main` | `coordinator/admin/pages_users_to_main/*.php` | `pages_users_to_main_bp` | `pages_users_to_main_service` | `pages_users`, `pages_users_to_main`, `pages` (write via add logic) | **Yes** (fix-it action)   |
| `admin/stat`                | `coordinator/admin/stat/*.php`                | `stat_bp`                | _(none — direct DB reads)_    | `pages`, `pages_users` (read-only aggregates)                       | **No**                    |

---

## Per-Route Specifications

---

### 1. `admin/tt` — Translate Type

**File:** `src/main_app/admin/routes/tt.py`
**Blueprint:** `tt_bp = Blueprint("tt", __name__, url_prefix="/tt")`
**Service:** `translate_type_service`

#### GET `/`

-   Query params: `cat` (string, default `"All"`)
-   Call `translate_type_service.list_translate_types(cat=cat)` → list of dicts
    with keys `tt_id`, `tt_title`, `tt_lead`, `tt_full`.
-   Also call `translate_type_service.list_new_titles()` → titles in `qids` not yet
    in `translate_type` (used to show "new titles" that need adding).
-   Call `list_categories()` for the category filter dropdown.
-   Render `admins/tt.html` with `translate_types`, `new_titles`, `categories`, `cat`.

#### GET `/edit`

-   Query params: `id` (optional), `title`, `lead`, `full`
-   If `id` is present → edit mode; if absent → add mode.
-   Render `admins/tt_edit.html` with the params pre-filled.
    (This is the popup equivalent of `edit_translate_type.php`.)

#### POST `/` (equivalent of `tt/post.php`)

-   Form fields (flat list style, one entry per submission from the edit popup):
    -   `id` (optional — present means update, absent means insert)
    -   `title` (required)
    -   `lead` (checkbox, value `"1"` or absent)
    -   `full` (checkbox, value `"1"` or absent)
-   Logic:
    ```
    if not title → flash error, redirect back
    result = translate_type_service.upsert(id, title, lead, full)
    flash success or danger
    redirect to url_for("admin.tt.tt_index")
    ```
-   PHP source: `tt/post.php` → calls `insert_to_translate_type($title, $lead, $full, $tt_id)`
    which does INSERT … WHERE NOT EXISTS if no id, UPDATE WHERE id if id present.

**Service methods needed in `translate_type_service`:**

-   `list_translate_types(cat="All") → list[dict]`
    -   SQL: `SELECT tt_id, tt_title, tt_lead, tt_full FROM translate_type`
    -   Filtered by category membership when `cat != "All"`.
-   `list_new_titles() → list[str]`
    -   SQL: `SELECT DISTINCT title FROM qids WHERE title NOT IN (SELECT tt_title FROM translate_type)`
-   `upsert(id, title, lead, full) → bool`
    -   INSERT … WHERE NOT EXISTS when `id` is empty.
    -   UPDATE … WHERE id when `id` is set.

---

### 2a. `admin/translated` — Translated Main Pages (`pages`)

**File:** `src/main_app/admin/routes/translated.py`
**Blueprint:** `translated_bp = Blueprint("translated", __name__, url_prefix="/translated")`
**Service:** `page_service`
**DB table:** `pages`

#### GET `/`

-   Query params: `lang` (default `"All"`), `page` (int, default 1), `limit` (int, default 500)
-   Call `page_service.list_translated(lang, limit, offset) → list[dict]`
-   Call `page_service.count_translated(lang) → int` for pagination.
-   Render `admins/translated.html` with `rows`, `total_count`, `lang`, `page`, `limit`.

#### GET `/edit`

-   Query params: `id` (required)
-   Call `page_service.get_by_id(id) → dict`
-   Render `admins/translated_edit.html` with `row`.
    Fields: `title`, `target`, `lang`, `user`, `pupdate`, and a `delete` toggle checkbox.

#### POST `/edit` (equivalent of `translated/edit_page.php` POST against `pages`)

-   Form fields:
    -   `id` (required)
    -   `delete` (optional checkbox, value = `id` — signals delete instead of update)
    -   `title`, `target`, `lang`, `user`, `pupdate` (required for update)
-   Logic:
    ```
    if "delete" in request.form:
        page_service.delete(id)
        flash("Page deleted.", "success")
    else:
        page_service.update(id, title, target, lang, user, pupdate)
        flash("Page updated.", "success")
    redirect to url_for("admin.translated.translated_index")
    ```
-   PHP SQL (update): `UPDATE pages SET title=?, target=?, lang=?, user=?, pupdate=? WHERE id=?`
-   PHP SQL (delete): `DELETE FROM pages WHERE id=?`

**Service methods needed in `page_service`:**

-   `list_translated(lang, limit, offset) → list[dict]`
-   `count_translated(lang) → int`
-   `get_by_id(id) → dict`
-   `update(id, title, target, lang, user, pupdate) → None`
-   `delete(id) → None`

---

### 2b. `admin/translated_users` — Translated User Pages (`pages_users`)

**File:** `src/main_app/admin/routes/translated_users.py`
**Blueprint:** `translated_users_bp = Blueprint("translated_users", __name__, url_prefix="/translated_users")`
**Service:** `user_page_service`
**DB table:** `pages_users`

**Identical structure to `admin/translated`** — same three endpoints, same logic, same form fields —
but all queries target `pages_users` instead of `pages`.

Routes:

-   `GET /` → `translated_users_index`
-   `GET /edit` → `translated_users_edit`
-   `POST /edit` → `translated_users_edit_post`

Render templates: `admins/translated_users.html`, `admins/translated_users_edit.html`
(can reuse the `translated` templates with a passed context variable if preferred).

Redirect after POST → `url_for("admin.translated_users.translated_users_index")`.

**Service methods needed in `user_page_service`:** identical interface to `page_service` above,
querying `pages_users`:

-   `list_translated(lang, limit, offset) → list[dict]`
-   `count_translated(lang) → int`
-   `get_by_id(id) → dict`
-   `update(id, title, target, lang, user, pupdate) → None`
-   `delete(id) → None`

---

### 3. `admin/qids` — TD Qids

**File:** `src/main_app/admin/routes/qids.py`
**Blueprint:** `qids_bp = Blueprint("qids", __name__, url_prefix="/qids")`
**Service:** `qid_service`
**DB table:** `qids`

#### GET `/`

-   Query params: `dis` (default `"all"`; values: `"all"`, `"empty"`, `"duplicate"`)
-   Call `qid_service.list_qids(dis=dis) → list[dict]` with keys `id`, `title`, `qid`.
-   Render `admins/qids.html` with `rows`, `dis`, `qid_table="qids"`.

#### GET `/edit`

-   Query params: `id` (optional), `title`, `qid`
-   Render `admins/qids_edit.html` (add or edit mode based on `id`).

#### POST `/` (equivalent of `qids/post.php` with `qid_table=qids`)

-   Form fields:
    -   `id` (optional — present = update, absent = insert)
    -   `title` (required)
    -   `qid` (required)
-   Validation (mirrors PHP logic):
    1. Both `title` and `qid` must be non-empty.
    2. Check if `qid` already exists in `qids` for a **different** id → flash error.
    3. Check if `title` already exists in `qids` for a **different** id → flash error.
-   On pass:
    -   If no `id`: `qid_service.insert(title, qid)` (INSERT … WHERE NOT EXISTS, then fill empty qid).
    -   If `id` present: `qid_service.update(id, title, qid)`.
-   Flash success or danger; redirect to `url_for("admin.qids.qids_index")`.

**Service methods needed in `qid_service`:**

-   `list_qids(dis="all") → list[dict]`
    -   `"all"` → all rows from `qids`
    -   `"empty"` → rows where `qid IS NULL OR qid = ''`
    -   `"duplicate"` → self-join to find duplicate qid or title entries
-   `get_by_qid(qid) → dict | None`
-   `get_by_title(title) → dict | None`
-   `insert(title, qid) → bool`
-   `update(id, title, qid) → bool`

---

### 4. `admin/qids_others` — Qids Others

**File:** `src/main_app/admin/routes/qids_others.py`
**Blueprint:** `qids_others_bp = Blueprint("qids_others", __name__, url_prefix="/qids_others")`
**Service:** `qid_others_service`
**DB table:** `qids_others`

**Identical structure to `admin/qids`** — same endpoints, same logic, same service interface —
but all queries target `qids_others` instead of `qids`.

Routes:

-   `GET /` → `qids_others_index`
-   `GET /edit` → `qids_others_edit`
-   `POST /` → `qids_others_post`

Render templates: `admins/qids_others.html`, `admins/qids_others_edit.html`
(can reuse the qids templates with a passed `qid_table` variable if preferred).

**Service methods in `qid_others_service`:** same as `qid_service` but querying `qids_others`.

---

### 5. `admin/pages_users_to_main` — Move User Pages to Main

**File:** `src/main_app/admin/routes/pages_users_to_main.py`
**Blueprint:** `pages_users_to_main_bp = Blueprint("pages_users_to_main", __name__, url_prefix="/pages_users_to_main")`
**Service:** `pages_users_to_main_service`

#### GET `/`

-   Query params: `lang` (default `"All"`)
-   Call `pages_users_to_main_service.list_pending(lang) → list[dict]`
    -   Fetches rows that need to be moved to main (from `pages_users` joined with `pages_users_to_main`).
    -   Each row has: `id`, `user`, `lang`, `title`, `target`, `pupdate`, `new_user`, `new_target`, `new_qid`, `qid`.
-   Render `admins/pages_users_to_main.html` with `rows`, `lang`, language filter list.

#### GET `/fix_it`

-   Query params: `id` (required), `new_user`, `new_target`
-   Call `pages_users_to_main_service.get_user_page(id)` → fetch from `pages_users WHERE id=?`
    -   Returns: `title`, `lang`, `target` (old target), `user` (old user), `pupdate`
-   Call `pages_users_to_main_service.check_main_page_exists(title, lang)` →
    query `pages WHERE title=? AND lang=? AND (target != '' AND target IS NOT NULL)`
    -   If result is not empty, pass `duplicate_page` to template to show a warning card.
-   Render `admins/pages_users_to_main_fix_it.html` with:
    -   `id`, `title`, `lang`, `old_target` (from `pages_users`), `new_user`, `new_target`, `pupdate`
    -   `duplicate_page` (dict or None)
    -   Fields the user can edit: `title`, `lang`, `new_target`, `new_user`, `pupdate`

#### POST `/fix_it` (equivalent of `fix_it_post.php`)

-   Form fields:
    -   `id` (required, int)
    -   `title` (required)
    -   `lang` (required)
    -   `new_target` (required)
    -   `new_user` (required)
    -   `pupdate` (required, YYYY-MM-DD)
-   Logic:
    1. Validate `id > 0`; fetch `pages_users WHERE id=?` to get `translate_type`, `cat`, `word`.
    2. Call `add_translate_row_to_db(title, translate_type, cat, lang, new_user, new_target, pupdate, word)`
       (reuse the same service function as the `add` route).
    3. If step 2 succeeds → call `pages_users_to_main_service.delete_user_page(id)`:
        - `DELETE FROM pages_users_to_main WHERE id=?`
        - `DELETE FROM pages_users WHERE id=?`
        - Verify both deletes succeeded.
    4. Flash all successes/errors; redirect to `url_for("admin.pages_users_to_main.pages_users_to_main_index")`.

**Service methods needed in `pages_users_to_main_service`:**

-   `list_pending(lang="All") → list[dict]`
    -   PHP calls `get_pages_users_to_main($lang)` — fetches from `pages_users` joined or filtered
        by `pages_users_to_main` entries.
    -   Each row includes `id`, `user`, `lang`, `title`, `target`, `pupdate`, `new_user`, `new_target`, `new_qid`.
-   `get_user_page(id) → dict | None`
    -   `SELECT * FROM pages_users WHERE id = ?`
-   `check_main_page_exists(title, lang) → dict | None`
    -   `SELECT * FROM pages WHERE title=? AND lang=? AND (target != '' AND target IS NOT NULL) LIMIT 1`
-   `delete_user_page(id) → bool`
    -   `DELETE FROM pages_users_to_main WHERE id=?`
    -   `DELETE FROM pages_users WHERE id=?`
    -   Returns True only if both rows are gone.

---

### 6. `admin/stat` — Statistics

**File:** `src/main_app/admin/routes/stat.py`
**Blueprint:** `stat_bp = Blueprint("stat", __name__, url_prefix="/stat")`
**Service:** none (direct DB reads or reuse existing aggregation functions)

> No PHP files were provided for `stat`. Implement a stub only.

#### GET `/`

-   No query params required initially.
-   Render `admins/stat.html` with whatever aggregate data is available
    (e.g. counts from `pages`, `pages_users`).
-   No POST endpoint needed.

---

## Implementation Rules

1. **File locations:**

    - Routes: `src/main_app/admin/routes/<name>.py`
    - Templates: `src/main_app/templates/admins/<name>.html`
    - Services: wherever existing services live (e.g. `src/main_app/db/services/...`)

2. **Blueprint registration:** register each new `*_bp` in the parent admin blueprint
   (`src/main_app/admin/__init__.py` or wherever `add_bp` is registered today), using the
   same pattern already used for `add_bp`.

3. **Form parsing — flat list style (not PHP rows dict):**
   PHP `rows[2][field]` → Flask `request.form.getlist("field")`.
   Single-record edit forms (tt edit, qids edit, translated edit, fix_it) use
   `request.form.get("field")` since they post exactly one record.

4. **No CSRF token logic in Python** — handle at the template/middleware level,
   consistent with how `add_translate` handles it (none in the Python route file).

5. **Flash + redirect pattern** — always flash then redirect (PRG pattern), never render
   the template directly after a POST.

6. **Error handling** — wrap service calls in `try/except`, log with `logger.exception`,
   flash `"danger"` on exception, same as `add_translate_post`.

7. **`qids` vs `qids_others` split** — even though PHP used a single `?qid_table=` param,
   Flask has **two separate blueprints** at two separate URL prefixes. Do not merge them.

8. **`translated` split** — PHP used `?table=pages` / `?table=pages_users` on the same PHP file.
   Flask uses **two separate blueprints**: `translated_bp` (url_prefix `/translated`, queries `pages`)
   and `translated_users_bp` (url_prefix `/translated_users`, queries `pages_users`).
   Same pattern as the `qids` / `qids_others` split. Do **not** use a `table` query param to switch
   between them in Flask.

9. **Logging:** add `logger = logging.getLogger(__name__)` at the top of every route file.

---

## Summary Checklist

-   [ ] `tt.py` — GET `/`, GET `/edit`, POST `/`
-   [ ] `translated.py` — GET `/`, GET `/edit`, POST `/edit`
-   [ ] `translated_users.py` — GET `/`, GET `/edit`, POST `/edit`
-   [ ] `qids.py` — GET `/`, GET `/edit`, POST `/`
-   [ ] `qids_others.py` — GET `/`, GET `/edit`, POST `/`
-   [ ] `pages_users_to_main.py` — GET `/`, GET `/fix_it`, POST `/fix_it`
-   [ ] `stat.py` — GET `/` (stub)
-   [ ] Service stubs: `translate_type_service`, `qid_service`, `qid_others_service`, `pages_users_to_main_service` (+ new methods on existing `page_service` / `user_page_service`)
-   [ ] Templates for each route (index + edit/fix_it where applicable)
-   [ ] Blueprint registration in admin `__init__.py` for all 7 blueprints
