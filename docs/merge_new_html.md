# Migration Plan: `mdwikicx/new_html` (PHP) → `publish_py` (Flask)

> **Status:** Planning (not yet implemented in `publish_py`).
> **Source repo:** https://github.com/mdwikicx/new_html > **Live PHP tool:** https://mdwikicx.toolforge.org/new_html_1 > **Target repo:** https://github.com/MrIbrahem/publish_py > **Owner of this plan:** `MrIbrahem` > **Last updated:** 2026-09-02

This document is the full porting plan for migrating the PHP `new_html` tool into the
Python `publish_py` Flask application as a new `new_html` blueprint. It is the companion
to `docs/merge.md` (which tracks each upstream endpoint's Flask status — `/new_html` is
currently listed as a _Code Source_ but has **no** Flask endpoint yet).

---

## 1. Goal & Scope

### Goal

Bring the `new_html` translation-prep tool into `publish_py` so that
`https://mdwikipy.toolforge.org/new_html/...` works the same way the PHP tool does today,
reusing existing `publish_py` infrastructure (config, HTTP clients, blueprint/route
patterns, pytest harness) wherever possible.

### What `new_html` actually does

For a given `mdwiki.org` article title it builds, caches, and returns **segmented content**
suitable for the ContentTranslation (`cx-1`) tool. The pipeline is:

1. **Fetch** wikitext + revision id from `mdwiki.org` (REST or API).
2. **Fix** the wikitext: strip translation-unfriendly constructs (templates, lead
   templates, bad/empty refs, videos, categories, missing images) and add a title heading.
3. **Transform** wikitext → HTML via the English Wikipedia REST `transform` endpoint.
4. **Segment** HTML → CX segments via the `HtmltoSegments` tool.
5. **Return** a JSON envelope (`sourceLanguage`, `title`, `revision`,
   `segmentedContent`, `categories`, `cache_data`, `error`) and **cache** each stage as files.

### In scope

-   All 8 PHP entry points (router, main API, `check`, `open`, `fix`, `revisions`,
    `revisions_api`, dashboard).
-   The domain "fix" pipeline and the three external-API clients (mdwiki fetch, transform, segment).
-   Filesystem cache + JSON title→revision index.
-   CORS, config/env, templates, and tests.

### Out of scope / notes

-   The `fix_wikitext` cleanup is **distinct** from the existing `refs` blueprint
    (`text_processor.do_changes_to_text_with_settings`), which _fixes references for
    publishing_. The `new_html` cleanup _strips content to prepare it for translation_.
    Keep them separate; only share low-level helpers if identical.
-   The `HtmltoSegments` endpoint is an **external** tool (maintained under `mdwikipy`); we
    only call it, we do not reimplement it.
-   `revisions.html` is a static PHP-generated page; we will render the dashboard from a
    Jinja template instead of copying static HTML.

---

## 2. Current PHP architecture (as-built)

### Entry points (`new_html/*.php`)

| File                                      | Role                                                                                                                                                                     |
| ----------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `index.php`                               | Router: empty/`?test` → dashboard; otherwise → `main.php`.                                                                                                               |
| `main.php`                                | Core API. Params: `title`, `new`, `all`, `printetxt` (`wikitext`\|`html`\|`seg`). Orchestrates the full pipeline and returns JSON (or raw text when `printetxt` is set). |
| `fix.php`                                 | Dev form: POST wikitext + title → returns `fix_wikitext` output.                                                                                                         |
| `check.php`                               | `?revid=` → `true`/`false` if both `seg.html` and `html.html` exist.                                                                                                     |
| `open.php`                                | `?revid=&file=` → serves `wikitext.txt`/`html.html`/`seg.html` (path-traversal protected, strips `data-parsoid`).                                                        |
| `revisions.php`                           | Dashboard: lists every revision dir with status badges + DataTable.                                                                                                      |
| `revisions_api.php`                       | JSON list of revision dirs.                                                                                                                                              |
| `revisions.html`                          | Static dashboard UI (generated).                                                                                                                                         |
| `bootstrap.php`/`require.php`/`utils.php` | Env, autoload, CORS, content-type, error helpers, `REVISIONS_PATH`/`JSON_FILE` constants.                                                                                |

### Service / domain layer (`src/`)

-   `Application/Controllers/JsonDataController.php` — title→revision JSON index (`json_data.json`, `json_data_all.json`).
-   `Application/Handlers/WikitextHandler.php` — `get_wikitext(title, file, just_lead)`: fetches from mdwiki REST, follows `#REDIRECT`, records revid into the index, applies `fix_wikitext`.
-   `Services/Api/MdwikiApiService.php` — fetch wikitext+revid from `mdwiki.org` (API + REST).
-   `Services/Api/TransformApiService.php` — `POST …/transform/wikitext/to/html/{title}`.
-   `Services/Api/SegmentApiService.php` — `POST {HtmltoSegments}` → `{result}`.
-   `Services/Api/CommonsApiService.php` — Commons image existence check (used by image fixes).
-   `Services/Api/HttpClientService.php` — cURL wrapper (the only HTTP client).
-   `Services/Html/WikitextToHtmlService.php` — caches transform output, post-fixes HTML (`del_div_error`, `fix_link_red`).
-   `Services/Html/HtmlToSegmentsService.php` — caches segment output, normalizes empty/error strings.
-   `Services/Wikitext/WikitextFixerService.php` — `fix_wikitext()` orchestrator (see §2 pipeline order).
-   `Domain/Fixes/**` & `Domain/Parser/**` — the actual regex/parse logic (the bulk of the port).
-   `Infrastructure/Utils/HtmlUtils.php` (`remove_data_parsoid`, `del_div_error`, `fix_link_red`), `FileUtils.php`, `Debug/PrintHelper.php`.

### External APIs used by PHP

| Purpose             | Endpoint                                                                                             | Notes                                                                    |
| ------------------- | ---------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------ |
| Fetch source        | `https://mdwiki.org/w/rest.php/v1/page/{title}`                                                      | returns `{source, latest:{id}}`; fallback `https://mdwiki.org/w/api.php` |
| Wikitext→HTML       | `https://en.wikipedia.org/w/rest.php/v1/transform/wikitext/to/html/{titleEncoded}` (POST `wikitext`) | HTML may contain `data-parsoid`                                          |
| HTML→segments       | `https://mdwikipy.toolforge.org/HtmltoSegments` (POST `{html}`) → `{result}`                         | `as_json` flag for this host                                             |
| Commons image check | `https://commons.wikimedia.org/w/api.php` (imageinfo)                                                | via `CommonsApiService`                                                  |

### Storage layout (filesystem cache)

-   Root: `REVISIONS_PATH` (env `REVISIONS_DIR`; default `$HOME/public_html/revisions_new1`).
-   Per revision: `{revid}/` or `{revid}_all/` containing `wikitext.txt`, `html.html`, `seg.html`, `title.txt`.
-   Index files (title → revid): `json_data.json` (main) and `json_data_all.json` (`all`/Video pages).

---

## 3. Target Flask architecture

### 3.1 New blueprint

Add `src/main_app/public/routes/new_html/` mirroring the existing `refs` blueprint:

```
src/main_app/public/routes/new_html/
├── __init__.py
└── routes.py            # NewHtmlRoutes (class-based, like FixRefsRoutes)
```

Register it in `src/main_app/public/__init__.py` `PUBLIC_ROUTE_MODULES`:

```python
PublicRouteModule(NewHtmlRoutes, "new_html", "/new_html"),
```

Because the JSON API endpoints are called cross-origin from the mdwiki/medwiki/mdwikicx
toolforge domains, **CSRF-exempt the public API routes** exactly like the `publish`
blueprint (`csrf_exempt(app, new_html_bp)`). The `fix` dev form can stay CSRF-exempt too
for parity with the PHP behavior.

### 3.2 New service package

Add `src/main_app/services/new_html/` (keeps the PHP layering recognizable):

```
src/main_app/services/new_html/
├── __init__.py
├── clients.py          # mdwiki fetch + transform + segment (thin wrappers over requests)
├── fix_wikitext.py      # port of WikitextFixerService + Domain/Fixes logic
├── storage.py           # REVISIONS_DIR cache + JSON index (port of JsonDataController/FileUtils)
└── html_utils.py        # remove_data_parsoid / del_div_error / fix_link_red
```

> **Reuse, don't reimplement:**
>
> -   `settings.other.user_agent` for all outbound requests (same as `text_api`/`mdwiki_api`).
> -   `requests` is already a dependency (used by `mdwiki_api`, `mediawiki_api`).
> -   `settings.cors.allowed_domains` for CORS (mirror `services/core/cors/is_allowed_checker.py`).
> -   Blueprint + `RouteRegistrar` pattern (template: `refs/routes.py`).
> -   Config dataclass + `@lru_cache` singleton pattern (`config/classes.py`, `main_settings.py`).
> -   pytest `unit`/`network` markers + `conftest.py` (AGENTS.md).

---

## 4. Endpoint mapping (PHP → Flask)

| PHP endpoint                     | Flask route                                       | Method   | Notes                                                                         |
| -------------------------------- | ------------------------------------------------- | -------- | ----------------------------------------------------------------------------- |
| `index.php` (no `title`)         | `GET /new_html/`                                  | GET      | Render dashboard template (port `revisions.php`).                             |
| `index.php?title=…` → `main.php` | `GET /new_html/?title=…`                          | GET      | Core pipeline; `printetxt` → raw `wikitext`/`html`/`seg`; else JSON envelope. |
| `check.php?revid=`               | `GET /new_html/check?revid=`                      | GET      | Return `true`/`false`.                                                        |
| `open.php?revid=&file=`          | `GET /new_html/open?revid=&file=`                 | GET      | Serve cached file with content-type; strip `data-parsoid`; block traversal.   |
| `fix.php` (GET/POST)             | `GET,POST /new_html/fix`                          | GET,POST | Dev form; POST runs `fix_wikitext` and re-renders.                            |
| `revisions.php`                  | `GET /new_html/revisions` (or reuse `/new_html/`) | GET      | Dashboard table.                                                              |
| `revisions_api.php`              | `GET /new_html/revisions_api`                     | GET      | JSON list of revision dirs.                                                   |
| `revisions.html`                 | template `new_html/index.html`                    | —        | Replaces static HTML.                                                         |

CORS headers (`Access-Control-Allow-Origin` for `mdwikicx/mdwiki/medwiki.toolforge.org`)
must be emitted by `main`, `check`, `open`, `revisions_api` (mirror `utils.php::set_cors_headers`).

---

## 5. Implementation phases (ordered)

### Phase 0 — Scaffolding

1. Add `NewHtmlConfig` dataclass in `src/main_app/config/classes.py` and load it in
   `src/main_app/config/main_settings.py` (`load_new_html_config()`), wire into `Settings`
   and `get_settings()`, and create the dir in `ensure_directories()`.
2. Add `src/main_app/public/routes/new_html/{__init__,routes}.py` with a `NewHtmlRoutes`
   skeleton and register it in `public/__init__.py` (`PUBLIC_ROUTE_MODULES`).
3. Add `src/main_app/services/new_html/` package with empty modules + `__init__`.
4. Append new env vars to `.env.example`.

### Phase 1 — Configuration (new vars)

| Env var              | Default                                  | Used for              |
| -------------------- | ---------------------------------------- | --------------------- |
| `REVISIONS_DIR`      | `~/public_html/revisions_new1`           | filesystem cache root |
| `TRANSFORM_BASE_URL` | `https://en.wikipedia.org/w/rest.php/v1` | wikitext→HTML         |

### Phase 2 — Storage (`storage.py`)

Port `JsonDataController` + `FileUtils`:

-   `get_file_dir(revid, all_flag)` → `Path(REVISIONS_DIR)/{revid}[_all]`.
-   `read_file`/`file_write` (atomic `Path.write_text`).
-   `get_title_revision(title, all_flag)` and `add_title_revision(title, revid, all_flag)`
    over `json_data.json` / `json_data_all.json`.
-   `list_revisions()` → sorted (by `wikitext.txt` mtime) list of `{number, lastModified, title, dir_path, oldid, wikitext_exists, html_exists, seg_exists}` (port `revisions_api.php`).

### Phase 3 — Clients (`clients.py`)

-   `get_mdwiki_wikitext(title)` → `(source, revid)`: call
    `https://mdwiki.org/w/rest.php/v1/page/{title}`; follow `#REDIRECT [[…]]`; on empty fall
    back to `https://mdwiki.org/w/api.php`. Use `settings.other.user_agent`.
-   `transform_wikitext_to_html(wikitext, title)` → POST
    `{TRANSFORM_BASE_URL}/transform/wikitext/to/html/{titleEncoded}` with `wikitext`.
-   `commons_image_exists(filename)` (optional, only if image-fix parity is needed) →
    `https://commons.wikimedia.org/w/api.php` imageinfo.

### Phase 4 — `fix_wikitext` pipeline (`fix_wikitext.py`)

Port `WikitextFixerService::fix_wikitext()` **in the same order**, one function per PHP
fixture (read each fixture file before porting — behavior must match):

1. `{{drugbox`/`{{Drugbox` → `{{Infobox drug`
2. `remove_templates` (`Domain/Fixes/Templates/DeleteTemplatesFixture.php`)
3. `remove_lead_templates` (`Domain/Fixes/Templates/FixTemplatesFixture.php`? verify)
4. `remove_bad_refs` (`Domain/Fixes/References/RefWorkerFixture.php`)
5. `del_empty_refs` (`Domain/Fixes/References/DeleteEmptyRefsFixture.php`)
6. `remove_videos` (`Domain/Fixes/Media/FixImagesFixture.php`? verify — `remove_videos`)
7. `remove_categories` (`Domain/Fixes/Structure/FixCategoriesFixture.php`)
8. `removeMissingImages` (`Domain/Fixes/Media/RemoveMissingImagesService.php`)
9. `add_missing_title(text, title)` (`Domain/Fixes/Templates/...` — read to port exactly)

> Each step is a function with its own pytest parity test using the PHP fixtures in
> `new_html/tests/` as golden inputs/outputs.

### Phase 5 — `html_utils.py`

Port `remove_data_parsoid`, `del_div_error`, `fix_link_red` from `HtmlUtils.php`.

### Phase 6 — Core API route (`routes.py`)

Port `main.php` `start()` into a route handler:

-   Resolve `title` (ucfirst), `new`, `all` (force `all` when title starts with `Video`), `printetxt`.
-   `get_wikitext(title, all_flag)` → fetch + fix + record revid + write `wikitext.txt`, `title.txt`.
-   `wiki_text_to_html(...)` with cache (read `html.html` unless `new`) → `remove_data_parsoid`.
-   `html_to_seg(...)` with cache (read `seg.html` unless `new`) → `remove_data_parsoid`.
-   Build and return the JSON envelope (`cache_data`, `sourceLanguage:"en"`, `title`, `revision`,
    `segmentedContent`, `categories:[]`, `error*`); `404` when empty.
-   Honor `printetxt` → `text/plain`/`text/html` raw output.

### Phase 7 — Supporting routes

-   `check` → `true`/`false`.
-   `open` → validate `revid` (`^\d+(_all)?$`) and `file ∈ {wikitext.txt,html.html,seg.html}`;
    set content-type; strip `data-parsoid` for html/seg; `400`/`404` on bad input.
-   `fix` → GET shows form (port `fix.php` HTML); POST runs `fix_wikitext` and re-renders.
-   `revisions` / `revisions_api` → from `storage.list_revisions()`.

### Phase 8 — Templates

-   `templates/new_html/index.html` — dashboard (port `revisions.php`: navbar, DataTable of
    revisions with status badges, "Re create" links). Reuse existing `base.html`/CSS where possible.
-   `templates/new_html/fix.html` — the dev fix form.

### Phase 9 — Tests (see §7)

Port PHPUnit fixtures → pytest; add route/integration tests; add `network`-marked tests.
Ensure `pytest` (default, no network) is green.

### Phase 10 — Docs & deploy

-   Update `docs/merge.md` (add a **New HTML** section with status ✔️ once merged).
-   Add toolforge env vars (`toolforge envvars create …`) for the four new vars.
-   Deploy via `shs/deploy_repo.sh publish_py <target>`.

---

## 6. Reuse & do-not-reimplement checklist

| Need                          | Reuse from `publish_py`                                                              |
| ----------------------------- | ------------------------------------------------------------------------------------ |
| HTTP client + UA              | `requests` + `settings.other.user_agent` (see `services/clients/mdwiki_api.py`)      |
| CORS domain check             | `settings.cors.allowed_domains` + `services/core/cors/is_allowed_checker.py`         |
| Route/blueprint pattern       | `public/routes/refs/routes.py` (`FixRefsRoutes`) + `public/__init__.py` registrar    |
| CSRF exemption for public API | `extensions.csrf_exempt` (see `publish` blueprint)                                   |
| Config pattern                | `config/classes.py` dataclasses + `main_settings.py` loader + `ensure_directories()` |
| Test harness                  | `conftest.py`, `pytest.ini`, `@pytest.mark.unit`/`network`, SQLite in-memory         |
| Arbritary-wiki wikitext fetch | `services/clients/text_api.get_wikitext` (for non-mdwiki needs only)                 |

---

## 7. Testing strategy

-   **Unit (no network, default `pytest`):**
    -   `tests/unit/services/new_html/test_fix_wikitext.py` — one parametrized test per fix step,
        using the PHP fixtures in `new_html/tests/WikiTextFixes/*` as golden data.
    -   `tests/unit/services/new_html/test_storage.py` — `get_file_dir`, JSON index read/write,
        `list_revisions` using `tmp_path`.
    -   `tests/unit/services/new_html/test_html_utils.py` — `remove_data_parsoid`/`del_div_error`/`fix_link_red`.
    -   `tests/unit/public/routes/new_html/test_routes.py` — route wiring, CORS header presence,
        `open` path-traversal rejection, `check` true/false.
-   **Mocked client tests:** `tests/unit/services/new_html/test_clients.py` — patch
    `requests` (or use `responses`/`requests_mock`) for mdwiki REST, transform, segment.
-   **Network (marked `@pytest.mark.network`, skipped offline):** mirror PHP
    `tests/NetworkRealTests/*` — real mdwiki REST, transform, segment; skip on connection failure.
-   **Integration:** `tests/integration/public/routes/new_html/` — full pipeline via
    `app.test_client()` for a known `mdwiki.org` title (guarded by `network` marker).

---

## 8. Risks & open questions

1. **Fix parity is the hard part.** The `Domain/Fixes` regexes are the bulk of behavior.
   Port one fixture at a time with golden tests; do not "improve" them during the move.
2. **`remove_videos` / `add_missing_title` / `remove_lead_templates`** mapping to PHP
   fixtures must be confirmed by reading the actual files (the `fix_wikitext` orchestrator
   imports were verified; the exact fixture per step should be re-checked during Phase 4).
3. **External dependency** `HtmltoSegments` is operated by `mdwikipy`. Make its URL
   configurable and fail gracefully (return `404`/empty seg, matching PHP).
4. **Transform endpoint** uses **enwiki** REST even though source is mdwiki — preserve this.
5. **`Video`/`all` pages** use the `_all` cache dir + `json_data_all.json`; keep the branch.
6. **Caching semantics**: PHP reads cache unless `?new=1`. Flask must honor the same so the
   dashboard "Re create" link (`/new_html/?new=1&title=…`) works.
7. **CSRF**: exempt the public API routes (mirror `publish`); keep the dev `fix` form exempt
   for parity.

---

## 9. Acceptance criteria (Definition of Done)

-   [ ] `GET /new_html/?title=<mdwiki title>` returns the same JSON envelope shape as PHP
        (`sourceLanguage`, `title`, `revision`, `segmentedContent`, `categories`, `cache_data`,
        `error*`).
-   [ ] `printetxt=wikitext|html|seg` return the correct raw content-type + body.
-   [ ] `check`, `open` (with traversal protection), `fix`, `revisions`, `revisions_api` all work.
-   [ ] Filesystem cache under `REVISIONS_DIR` is created and reused; JSON index updated.
-   [ ] CORS works for `mdwikicx/mdwiki/medwiki.toolforge.org`.
-   [ ] `pytest` (default, no network) is green; `pytest -m network` passes where APIs reachable.
-   [ ] `docs/merge.md` updated with a **New HTML** section and ✔️ status.
-   [ ] New env vars documented in `.env.example` and set on Toolforge.

---

## 10. Rollout

1. Branch `feature/new-html-blueprint` (or `docs/merge-new-html-plan` for this doc PR).
2. Implement phases 0–9; run `black`/`isort`/`ruff` before committing (AGENTS.md).
3. Open PR against `main`; link this plan.
4. After merge: add Toolforge env vars, deploy via `shs/deploy_repo.sh`.
5. Smoke test live `/new_html/?title=Trifluoperazine` and the dashboard.
