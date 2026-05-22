# Plan — Port `results_2026` PHP module to the `bp_main.get("/")` index() route in publish_py

> **Corrigendum (post-implementation, after sql.sql review):**
> Earlier sections of this plan claim "the publish_py-side equivalent of `category_members` is `all_articles`" and recommend swapping the table name. **That is wrong.** Per `Translation-Dashboard/sql.sql`, `all_articles` and `category_members` are two distinct tables: `all_articles` has `UNIQUE(article_id)` (one row per article, with its primary category) while `category_members` has `UNIQUE(category, article_id)` (true many-to-many membership). The PHP queries explicitly need the many-to-many table.
>
> **Implementation uses `category_members` directly,** backed by a new `CategoryMemberRecord` SQLAlchemy model (`src/main_app/db/models/category_members.py`) so the table is auto-created at app launch alongside the other models. Treat `§3 Database queries` and `§9 row 1` of this plan as updated accordingly.

**Scope:** Replicate the behavior of `Translation-Dashboard/src/backend/results_2026/*.php` (the new "2026" results pipeline) inside the existing Flask `index()` route at `publish_py/src/main_app/public/routes/main/routes.py`. Both repos share the same MySQL/MariaDB database, so the table names referenced here must remain identical.

**Status:** Planning only — no code is written until this plan is reviewed and approved.

---

## 1. Files to be read, created, or modified

### 1.1 PHP files read (Translation-Dashboard, reference only — not modified)

| Path | Purpose |
|------|---------|
| `src/backend/results_2026/index.php` | Top-level `results_loader_2026($data)` orchestrator + `Results_tables_2026()` + `card_result()` wrapper + `load_translate_type()` filter helper |
| `src/backend/results_2026/get_results_2026.php` | `get_results_2026($cat, $code)` — combines `missing`, `exists`, `inprocess` and computes the summary |
| `src/backend/results_2026/include.php` | Bootstraps the four files above |
| `src/backend/results_2026/results_table.php` | Renders the missing-titles table |
| `src/backend/results_2026/results_table_exists.php` | Renders the already-translated (exists) table |
| `src/backend/results_2026/results_table_inprocess.php` | Renders the "in-process" table |
| `src/backend/api_or_sql/new_sql_tables.php` | Defines `missing_by_lang_and_category()`, `exists_by_lang_and_category()` SQL |
| `src/backend/api_or_sql/process_data.php` | Defines `get_lang_in_process()` SQL |
| `src/backend/api_or_sql/funcs.php` | Defines `get_lang_pages_by_cat()` SQL |
| `src/backend/api_or_sql/data_tab.php` | Defines `get_td_or_sql_full_translators()`, `get_td_or_sql_translate_type()`, `get_td_or_sql_settings()`, `get_endpoint()` |
| `src/frontend/html.php` | Defines `make_mdwiki_href`, `make_mdwiki_article_url_blank`, `make_mdwiki_cat_url`, `make_wikipedia_url_blank`, `make_wikidata_url_blank` |
| `src/backend/results/tr_link.php` | Defines `make_tr_link_medwiki`, `make_ContentTranslation_url` |
| `src/frontend/results_rows/results_table_html.php` | Defines `make_table_start()` |
| `src/results/helps.php` | Defines `make_translate_urls()` |
| `src/backend/loaders/load_request.php` | Defines GET parameter parsing |
| `src/index.php` | Defines how the loader is wired into the page (form + `results_loader_2026($data)`) |

### 1.2 publish_py files read (reference only — not modified)

| Path | Purpose |
|------|---------|
| `src/app.py`, `src/main_app/__init__.py` | App factory, blueprint registration |
| `src/main_app/public/routes/main/routes.py` | **Will be modified.** Hosts `bp_main` and the current `index()` route |
| `src/main_app/public/routes/main/results_api.py` | Existing JSON results endpoint — pattern reference only |
| `src/main_app/db/services/__init__.py` | Service barrel exports |
| `src/main_app/db/services/pages/{page_service,in_process_service,translate_type_service}.py` | Existing service helpers we will reuse |
| `src/main_app/db/services/users/{coordinator_service,full_translator_service}.py` | `active_coordinators()`, `is_full_translator()` |
| `src/main_app/db/services/content/{lang_service,category_service}.py` | `list_langs`, `list_categories`, `get_camp_to_cats` |
| `src/main_app/db/services/config/setting_service.py` | `get_setting_by_key()` for `use_mdwikicx` lookup |
| `src/main_app/db/services/wikidata/allqid_service.py` | Existing `list_targets_by_lang()` — pattern reference for raw-SQL queries |
| `src/main_app/db/models/*.py` | All model definitions referenced by the new queries |
| `src/main_app/shared/auth/identity.py` | `current_user()` |
| `src/templates/{base.html,index.html,_navbar.html}` | Template framework, existing form |

### 1.3 publish_py files to be CREATED

| Path | Purpose |
|------|---------|
| `src/main_app/db/services/pages/results_2026_service.py` | `missing_by_lang_and_category()`, `exists_by_lang_and_category()` raw-SQL helpers (mirroring `new_sql_tables.php`) |
| `src/main_app/shared/utils/wiki_links.py` | URL/HTML helpers: `mdwiki_url`, `mdwiki_article_link`, `mdwiki_cat_link`, `wikipedia_link`, `wikidata_link`, `tr_link_medwiki`, `content_translation_url` |
| `src/main_app/public/routes/main/results_2026.py` | Core porting module: `results_loader_2026(...)` Python function + small dataclass for the result bundle. This is the equivalent of PHP's `index.php` + `get_results_2026.php` orchestration logic. (HTML rendering itself happens in templates — see below.) |
| `src/templates/results_2026/_results_card.html` | Jinja partial: collapsible Bootstrap card wrapper (replaces PHP `card_result()`) |
| `src/templates/results_2026/_results_table.html` | Jinja partial: missing-titles table (replaces `results_table.php`) |
| `src/templates/results_2026/_inprocess_table.html` | Jinja partial: in-process table (replaces `results_table_inprocess.php`) |
| `src/templates/results_2026/_exists_table.html` | Jinja partial: exists table (replaces `results_table_exists.php`) |

### 1.4 publish_py files to be MODIFIED

| Path | Change |
|------|--------|
| `src/main_app/public/routes/main/routes.py` | Update `index()` to: parse the same set of GET params as PHP `load_request`, resolve campaign↔category, invoke the new `results_loader_2026(...)` when both `code` and `camp` are present, pass the resulting bundle into the template |
| `src/templates/index.html` | Append a "results" block below the existing form that renders the three cards from `results_2026/*.html` partials when results are present |

> No existing template, route, or service is removed. The current `/results_api` JSON endpoint is left untouched so existing API consumers keep working.

---

## 2. PHP → Python mapping

### 2.1 Functions / orchestrators

| PHP function | New Python equivalent |
|---|---|
| `Results\GetResults2026\results_loader_2026($data)` | `main_app.public.routes.main.results_2026.results_loader_2026(...)` |
| `Results\GetResults2026\Results_tables_2026(...)` | Inlined — Python returns a structured bundle and the Jinja templates render the three cards |
| `Results\GetResults2026\get_results_2026($cat, $code)` | `main_app.public.routes.main.results_2026.get_results_2026(cat, code)` |
| `Results\GetResults2026\getinprocess_n($missing, $code)` | Private helper `_filter_inprocess_to_missing(...)` inside `results_2026.py` |
| `Results\GetResults2026\_create_summary(...)` | `_create_summary(...)` inside `results_2026.py` (returns HTML string) |
| `Results\GetResults2026\load_translate_type('full' \| 'no')` | Reuses existing `list_translate_types()` once and partitions into two lists in `results_2026.py` |
| `Results\GetResults2026\card_result(...)` | Jinja partial `_results_card.html` |
| `Results\GetResults2026\make_results_table_2026(...)` | Jinja partial `_results_table.html` (driven by Python-prepared row dicts) |
| `Results\GetResults2026\make_results_table_inprocess(...)` | Jinja partial `_inprocess_table.html` (driven by Python-prepared row dicts) |
| `Results\GetResults2026\make_results_table_exists_2026(...)` | Jinja partial `_exists_table.html` (driven by Python-prepared row dicts) |
| `Loaders\LoadRequest\load_request(...)` | `_parse_request_args(...)` private helper inside `routes.py` (lightweight, since langs/categories already loaded for the form) |

### 2.2 SQL helpers

| PHP function | New Python equivalent |
|---|---|
| `SQLorAPI\Funcs\missing_by_lang_and_category($lang, $cat)` | `db.services.pages.results_2026_service.missing_by_lang_and_category(lang, cat)` |
| `SQLorAPI\Funcs\exists_by_lang_and_category($lang, $cat)` | `db.services.pages.results_2026_service.exists_by_lang_and_category(lang, cat)` |
| `SQLorAPI\Funcs\get_lang_pages_by_cat($lang, $cat)` | Already exists: `list_pages_by_lang_cat(lang, cat)` |
| `SQLorAPI\Process\get_lang_in_process($code)` | Already exists: `list_in_process_by_lang(code)` |
| `SQLorAPI\GetDataTab\get_td_or_sql_translate_type()` | Already exists: `list_translate_types()` |
| `SQLorAPI\GetDataTab\get_td_or_sql_full_translators()` | Already exists: `is_full_translator(username)` (preferred) or `list_full_translators()` |
| `SQLorAPI\GetDataTab\get_endpoint()` | New helper `_get_endpoint()` inside `wiki_links.py` (reads `use_mdwikicx` setting) |

### 2.3 URL builders

All HTML/URL helpers go into `src/main_app/shared/utils/wiki_links.py`. They produce **plain Python strings**, marked safe in the templates with the `|safe` filter (or used directly in `href` attributes which Jinja already escapes correctly).

| PHP helper | Python signature |
|---|---|
| `make_mdwiki_href($title)` | `mdwiki_url(title: str) -> str` |
| `make_mdwiki_article_url_blank($title, $name=null)` | `mdwiki_article_link(title: str, name: str \| None = None) -> str` |
| `make_mdwiki_cat_url($category, $name=null)` | `mdwiki_cat_link(category: str, name: str \| None = None) -> str` |
| `make_wikipedia_url_blank($target, $lang, $name='', $deleted=false)` | `wikipedia_link(target: str, lang: str, name: str = "", deleted: bool = False) -> str` |
| `make_wikidata_url_blank($qid, $name='', $default='')` | `wikidata_link(qid: str, name: str = "", default: str = "") -> str` |
| `make_tr_link_medwiki(...)` | `tr_link_medwiki(title, lang, cat, camp, tra_type, word) -> str` |
| `make_ContentTranslation_url(...)` | `content_translation_url(title, lang, cat, camp, tra_type, endpoint) -> str` |
| `get_endpoint()` | `_get_endpoint() -> str` (private to `wiki_links.py`) |

All builders use `urllib.parse.quote` (with `safe=""`) which is the closest Python equivalent of PHP `rawurlencode`, and replace spaces with `_` before encoding (matches PHP behavior exactly).

---

## 3. Database queries (verbatim from PHP, with Python-side substitution rules)

> Both repos share the same MariaDB instance. The PHP query references `category_members`; in publish_py the same table is exposed by the model `AllArticlesRecord` (table name `all_articles`) — confirmed by the existing `list_targets_by_lang()` SQL which already joins on `all_articles aa ON aa.article_id = q.title`. **All queries below will use `all_articles` (matching the publish_py convention) instead of `category_members`.** This is the single, critical naming difference; all other table/column names match exactly.

### 3.1 `missing_by_lang_and_category(lang, cat)`

```sql
SELECT
    c.article_id   AS title,
    c.category     AS category,
    ase.importance AS importance,
    rc.r_lead_refs AS r_lead_refs,
    rc.r_all_refs  AS r_all_refs,
    ep.en_views    AS en_views,
    q.qid          AS qid,
    w.w_lead_words AS w_lead_words,
    w.w_all_words  AS w_all_words
FROM all_articles c
JOIN qids q                  ON q.title    = c.article_id
LEFT JOIN all_qids_exists aq ON aq.qid     = q.qid AND aq.code = :lang
LEFT JOIN assessments ase    ON ase.title  = c.article_id
LEFT JOIN enwiki_pageviews ep ON ep.title  = c.article_id
LEFT JOIN refs_counts rc     ON rc.r_title = c.article_id
LEFT JOIN words w            ON w.w_title  = c.article_id
WHERE c.category = :cat
  AND aq.target IS NULL
  AND EXISTS (SELECT 1 FROM langs la WHERE la.code = :lang)
```

Bind parameters (named, via `sqlalchemy.text(...)`): `:lang`, `:cat`.

### 3.2 `exists_by_lang_and_category(lang, cat)`

```sql
SELECT
    c.article_id   AS title,
    c.category     AS category,
    ase.importance AS importance,
    rc.r_lead_refs AS r_lead_refs,
    rc.r_all_refs  AS r_all_refs,
    ep.en_views    AS en_views,
    q.qid          AS qid,
    w.w_lead_words AS w_lead_words,
    w.w_all_words  AS w_all_words,
    aq.target      AS target
FROM all_articles c
JOIN qids q                  ON q.title    = c.article_id
LEFT JOIN all_qids_exists aq ON aq.qid     = q.qid AND aq.code = :lang
LEFT JOIN assessments ase    ON ase.title  = c.article_id
LEFT JOIN enwiki_pageviews ep ON ep.title  = c.article_id
LEFT JOIN refs_counts rc     ON rc.r_title = c.article_id
LEFT JOIN words w            ON w.w_title  = c.article_id
WHERE c.category = :cat
  AND aq.target IS NOT NULL
  AND EXISTS (SELECT 1 FROM langs la WHERE la.code = :lang)
```

### 3.3 Reused queries (already implemented)

| Service call | Resulting SQL |
|---|---|
| `list_pages_by_lang_cat(lang, cat)` | `SELECT * FROM pages WHERE lang = :lang AND cat = :cat` (used to detect `via='td'`) |
| `list_in_process_by_lang(lang)` | `SELECT * FROM in_process WHERE lang = :lang` (filtered by title in Python) |
| `list_translate_types()` | `SELECT tt_id, tt_title, tt_lead, tt_full FROM translate_type` (split into `no_lead` + `full_only` lists) |
| `is_full_translator(username)` | `SELECT id, user, is_active FROM full_translators WHERE user = :user AND is_active = 1` |
| `get_setting_by_key("use_mdwikicx")` | `SELECT * FROM new_settings WHERE key = :key` (drives endpoint switch) |

> All raw SQL goes through `db.session.execute(text("..."), {"lang": ..., "cat": ...})`, never f-strings, never string concatenation. This is the exact pattern already used by `list_targets_by_lang()`.

---

## 4. Request handling — URL parameters

| GET param | Type | Source PHP | Behavior in publish_py |
|---|---|---|---|
| `code` | string | `load_request.php` | language code; validated via `get_lang_by_code(code)`; sets a flash error and skips results when invalid |
| `camp` | string | `load_request.php` | campaign name; cross-resolved to `cat` via the `categories` table |
| `cat` | string | `load_request.php` | category; if missing, resolved from `camp`; if both missing → no results card rendered |
| `type` | string | `load_request.php` (mapped to `tra_type`) | `'lead'` or `'all'`; if `allow_type_of_translate == "0"` from settings, force `'lead'` |
| `doit` | any | `load_request.php` | "submit" marker; PHP renders results when present, the Python port renders results when both `code` AND `camp` are resolved (matches PHP `if ($camp && $code)` final dispatch) |
| `exists` | any | `src/index.php` | when present, force `show_exists = True` even for non-coordinator users |
| `test` | any | `load_request.php` | toggles a small debug line above the results (kept for parity but not exposed in UI) |
| `filter_sparql` | bool | `load_request.php` | not used by 2026 flow; ignored (parsed for forward-compat) |

Internal flags computed in the Python route (mirroring PHP):

| Variable | Computation |
|---|---|
| `code_lang_name` | `get_lang_by_code(code).name` |
| `global_username` | `current_user().username` if authenticated, else `""` |
| `user_coord` | `bool(current_user() and current_user().username in active_coordinators())` |
| `show_exists` | `user_coord or 'exists' in request.args` |
| `translation_button` | `'1'` if `user_coord and setting('translation_button_in_progress_table') != "0"` else `'0'` (string for parity with PHP) |
| `full_tr_user` | `is_full_translator(global_username)` |
| `endpoint` | from `_get_endpoint()` reading `use_mdwikicx` setting |

---

## 5. Three rendering states

The PHP `results_loader_2026` always returns the same string shape and lets the data drive whether each card is visible. The Python port follows the same approach.

| State | Trigger | Output |
|---|---|---|
| **In-process** | `len(inprocess) > 0` | "In process: (N)" card with the in-process table |
| **Exists (already translated)** | `len(exists) > 1 AND show_exists` | "Exists: (N)" card with translated/translated-before table |
| **Results / Missing** | Always rendered | "Results: (N)" card with missing-titles table; if `len(missing) == 0` the card body is empty (mirrors PHP) |

**No results / table missing fallback:** When `code` or `camp` are missing or invalid, the route renders **only** the existing filter form and skips the results section entirely — the same fallback the current `index()` route already provides.

> The user requirement mentions "table missing" and "in-process" as orthogonal modes, but a careful read of `results_2026/index.php` shows they are sub-sections of a single render. The Python port therefore renders any subset of the three cards as appropriate, instead of treating them as mutually exclusive states. This is documented here to make the deviation from the prompt explicit and intentional.

---

## 6. Data shape passed to templates

`results_loader_2026(...)` returns a dataclass-like dict:

```python
{
  "ix": str,                          # summary HTML (counts + category link + lang link)
  "missing": list[MissingRow],        # for the "Results" table
  "inprocess": list[InProcessRow],    # for the "In process" table (empty list = card hidden)
  "exists":  list[ExistsRow],         # for the "Exists" table   (len <= 1 = card hidden unless show_exists)
  "show_exists": bool,
  "translation_button": str,          # '0' | '1', forwarded to templates
  "test": bool,
  "code": str,
  "camp": str,
  "cat": str,
  "tra_type": str,
  "code_lang_name": str,
  "global_username": str,
  "full_tr_user": bool,
  "endpoint": str,
}
```

Each row dict is **prepared in Python** (rather than in Jinja) so the templates stay simple and the URL/HTML escaping rules live in one place. Row schemas:

```python
MissingRow = {
  "n": int, "title": str, "mdwiki_url": str,
  "translate_html": str,        # already-built button(s); never stored as raw user input
  "en_views": int|str, "importance": str, "words": int, "refs": int,
  "qid_html": str, "is_full_row": bool,
}
InProcessRow = MissingRow + {"user": str, "date": str}
ExistsRow = {
  "n": int, "mdwiki_link_html": str, "translate_html": str,
  "translated_html": str,        # wikipedia_link if via='td' else ''
  "translated_before_html": str, # wikipedia_link if via='before' else ''
  "qid_html": str,
}
```

The `_html` suffixes signal that the value is already-built safe HTML produced by the helpers in `wiki_links.py`. Templates render these with `{{ row.translate_html|safe }}`. **No user-supplied free text is ever passed through `|safe`.** Title strings are rendered with normal Jinja escaping when used as text content.

---

## 7. Algorithm — `results_loader_2026(data)` step-by-step

Mirroring PHP:

1. **Inputs:** `code`, `camp`, `cat`, `tra_type`, `show_exists`, `translation_button`, `global_username`, `user_coord`, `test`, `code_lang_name`, `full_tr_user`, `endpoint`.
2. Call `get_results_2026(cat, code)`:
   1. `pages_via_td = list_pages_by_lang_cat(code, cat)` and index by `title`.
   2. `items_missing = missing_by_lang_and_category(code, cat)`.
   3. `items_exists  = exists_by_lang_and_category(code, cat)` indexed by `title`.
   4. Tag each exists row: `via = "td" if title in pages_via_td else "before"`.
   5. Compute `inprocess = {row.title: row for row in list_in_process_by_lang(code) if row.title in {m["title"] for m in items_missing}}`.
   6. Remove inprocess titles from `items_missing`.
   7. Build summary HTML: `"Found N pages in {cat_link}, {E} exists, and {M} missing in ({code_link}), {I} in process."`
   8. Sort `items_exists` by title key (matches PHP `ksort`).
   9. Return `{"ix": summary, "inprocess": inprocess, "exists": items_exists, "missing": items_missing}`.
3. Load auxiliary data once:
   - `nolead_titles = {tt.tt_title for tt in list_translate_types() if tt.tt_lead == 0}`
   - `full_titles   = {tt.tt_title for tt in list_translate_types() if tt.tt_full == 1}`
4. Sort `missing` by `en_views` desc (PHP `usort`); cap to a reasonable number? **No — PHP doesn't cap, so neither do we.**
5. Build per-row dicts:
   - **Missing rows** (PHP `_make_one_row_results`):
     - Detect `is_video = title.lower().startswith("video:")`. If video, force `tra_type='all'`.
     - Compute `words/refs` from row data, switching to `w_all_words/r_all_refs` when `tra_type=='all'`.
     - Build `mdwiki_url`, `qid_html`, `translate_html` per the four PHP branches:
       1. No user → "Login" button linking to `auth.login`.
       2. `full_tr_user and not is_video` → two buttons (Lead + Full) using `tr_link_medwiki`.
       3. Default → single "Translate" button using `tr_link_medwiki`.
     - Apply the lead/full filter logic from PHP:
       - If `do_full = (tra_type != 'all')` AND title in `nolead_titles` AND title not in `full_titles` → skip row entirely.
       - If `do_full` AND title in `full_titles` → emit an extra "Full" version of the row right after the lead row (PHP appends `cnt2.Full` numbering).
   - **In-process rows** (PHP `make_one_row_new_inprocess` + `make_translate_urls`):
     - Look up auxiliary metrics by joining the inprocess row with the missing/exists data already loaded (we **do not** re-query `assessments`/`words`/`refs_counts` per row; we build a single `titles_infos_by_title` dict from the union of `items_missing` and `items_exists` once). This avoids the N+1 query problem that PHP avoids via in-memory `array_column`.
     - Translate URL: only present when `translation_button == '1'` AND `global_username`. Otherwise empty.
     - When emitted: lead+full pair when `full_tr_user` and not video; single button otherwise.
   - **Exists rows** (PHP `make_one_row_exists_2026`):
     - `mdwiki_link_html = mdwiki_article_link(title)`.
     - `translate_html` = ContentTranslation button **only if** `global_username and user_coord` (matches PHP `(!empty($global_username) && $user_coord)`).
     - `translated_html` if `via == 'td'`, else `translated_before_html` if `via == 'before'`.
6. Return the bundle dict described in §6.

---

## 8. Template structure

`templates/index.html` — append below the existing form:

```jinja
{% if results %}
  <div class="container-fluid">
    {# logic from results_2026/index.php — Results_tables_2026 #}
    {% include "results_2026/_results_card.html" with context %}
  </div>
{% endif %}
```

`templates/results_2026/_results_card.html` orchestrates the three optional sub-cards:

```jinja
{# Missing/Results card — always rendered when results bundle present #}
{% set body %}{% include "results_2026/_results_table.html" %}{% endset %}
{% include "results_2026/_card.html" with context %}

{% if results.inprocess %}
  {% include "results_2026/_inprocess_table.html" %}
{% endif %}

{% if results.show_exists and results.exists|length > 1 %}
  {% include "results_2026/_exists_table.html" %}
{% endif %}
```

(Exact wiring will be finalized in implementation; the goal is one Jinja partial per PHP file.)

Each table partial uses the existing Bootstrap 5 + DataTables CSS classes (`table compact table-striped table_100 table_text_left table_responsive_main display`) so DataTables auto-init in `base.html` works out of the box. The collapsible card wrapper uses the same `data-card-widget="collapse"` markup wired in `static/js/card-tools.js`.

---

## 9. Edge cases / differences between PHP and Python

| # | PHP behavior | Port handling |
|---|---|---|
| 1 | `category_members` table | Use `all_articles` (same schema, the publish_py convention). Documented in §3. |
| 2 | `super_function()` switches between TD-API and SQL based on a setting | Always go through SQLAlchemy; the publish_py architecture has already chosen the SQL path. The "TD-API fallback" is irrelevant inside publish_py because publish_py *is* the SQL backend. |
| 3 | `htmlspecialchars` on inputs | Flask/Jinja autoescape covers display; `urllib.parse.quote` covers URL building; SQLAlchemy bound parameters cover queries. **No string concatenation in any SQL.** |
| 4 | PHP `str_replace('_', ' ', $title)` for display | Mirror via Python `title.replace("_", " ")` in row prep. |
| 5 | PHP `rawurlencode` | Use `urllib.parse.quote(value, safe="")`. |
| 6 | PHP heredoc HTML | Use Jinja templates instead — keeps escaping consistent. |
| 7 | PHP static caching inside helper functions (`static $foo = []`) | Use `functools.lru_cache(maxsize=1)` for the lookup helpers that are pure (translate_type, full_translators) — already done in publish_py for `active_coordinators()`. We will NOT cache user-specific lookups. |
| 8 | PHP loops emit "extra" Full row for some titles | Python emits two row dicts in sequence with `is_full_row=True` on the second; the template renders them identically. |
| 9 | PHP timestamps display `add_date` truncated at first space | Mirror via Python `date_str.split(" ")[0] if ":" in date_str else date_str`. |
| 10 | Empty `importance` shown as "Unknown" | Same default in Python row prep. |
| 11 | `Video:` prefix forces `tra_type='all'` and disables Full button | Same logic in Python row prep. |
| 12 | PHP `if ($camp && $code)` to dispatch results | Python: only call `results_loader_2026()` when both resolved AND `code_lang_name` is non-empty (matches the PHP path that requires a valid lang). |
| 13 | Anonymous users see "Login" button instead of "Translate" | Same — emitted by `wiki_links.login_button(url_for('auth.login'))` (or rendered directly in the template since it has no parameters). |
| 14 | PHP `make_tr_link_medwiki` produces `translate_med/index.php?…` | Python `tr_link_medwiki` produces the **same relative URL string** (`translate_med/index.php?…`) for parity, even though publish_py may not yet host that endpoint. The link target is the Translation-Dashboard PHP app, which is the same behavior the existing `index.html` form references via `?cat=RTT&depth=1&code=ceb&doit=1`. **Decision:** keep the relative path identical; revisit only if the user later requests a Python-side equivalent. |
| 15 | `use_mdwikicx` setting toggles endpoint between `medwiki.toolforge.org` and `mdwikicx.toolforge.org` | Mirror via `get_setting_by_key("use_mdwikicx")`. If the key is absent or value is `"0"`/`None`/falsy, default to `medwiki.toolforge.org` (PHP default). |
| 16 | PHP returns nothing when `code` or `camp` is empty | Python skips `results_loader_2026()` and renders only the form — the existing index() behavior. |
| 17 | The PHP `results_2026` flow does not use `depth` | Neither will the Python port. The existing `index.html` form already only cares about `code`, `camp`, `type`. |
| 18 | PHP fetches `get_td_or_sql_titles_infos()` — a large left-join used only as a fallback for inprocess rows | We avoid this query by reusing the `items_missing` + `items_exists` lookups already loaded for the same titles. This is faster and avoids a third large scan. |

---

## 10. Verification plan

After implementation, before commit:

1. **Static analysis:** `python -m compileall src/main_app` and run `ruff` / `mypy` if configured (per `pyproject.toml`).
2. **Smoke test:** Hit `/` with no params → form renders, no results card. Hit `/?code=ar&camp=Hearing` → up to three cards render. Hit `/?code=invalid` → flash error, form-only render.
3. **Unit tests (optional, only if requested):** none added unless the user asks; this matches the standing instruction.
4. **DB safety:** confirm every raw-SQL `text(...)` call uses bound parameters; grep for `f"{` and `% (` inside `results_2026_service.py` to be sure no string-built SQL slipped in.
5. **Existing routes:** explicitly retest `/results_api`, `/missing`, `/reports`, `/leaderboard/`, `/api/*` — none of these should change behavior.
6. **PR description:** include a section listing the new files, the modified files, and the PHP file → Python file mapping (this plan can be linked).

---

## 11. Commit & push policy

- Commit message: `feat: port results_2026 logic to index() route in Python/Flask`
- Single-purpose commit (no unrelated formatting changes).
- Push to a new branch like `port-results-2026` (never directly to `main`).
- Open a PR via `github_create_pull_request` with a body that summarises the change, lists the new files, and references this plan.
- Each new function will carry an inline comment such as `# logic from results_2026/get_results_2026.php` near its top, per the user requirement.

---

## 12. Open questions / assumptions

These are the assumptions made while writing the plan; if any is wrong, the user should correct them before implementation begins.

1. **`all_articles` is the publish_py-side name for `category_members`.** Verified by `list_targets_by_lang()` SQL, but worth flagging.
2. **`tr_link_medwiki` keeps the relative `translate_med/index.php` URL** — the Python port does not need a Python equivalent of that endpoint right now; the link is consumed by the PHP Translation-Dashboard. This is consistent with the example link already present in `templates/index.html`.
3. **`is_admin` (publish_py) ≡ `user_is_coordinator` (PHP).** Same predicate (`username in active_coordinators()`), so it doubles as `user_coord`.
4. **Setting key `translation_button_in_progress_table`** exists in the `new_settings` table; if not present in this DB, the port will treat its absence as `"0"` (matches PHP `?? '0'`).
5. **`use_mdwikicx`** likewise; default `"0"` if absent.
6. **The existing `/results_api` JSON endpoint stays unchanged.** Both endpoints can coexist and progressively diverge if future PHP updates require it.
