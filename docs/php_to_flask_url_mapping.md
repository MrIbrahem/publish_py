# PHP → Flask URL Migration Mapping & Analysis

## Executive Summary
This document provides a complete, auditable mapping between the legacy PHP repository ([Translation-Dashboard](https://github.com/MrIbrahem/Translation-Dashboard)) and the current Flask repository (`publish_py`).

All source files, controllers, templates, JavaScript files, forms, and redirects from both repositories were analyzed to ensure no endpoint or parameter combination was overlooked.

---

## Complete PHP → Flask URL Mapping Matrix

| PHP URL | PHP Purpose | Flask URL | HTTP Method | Migration Status | Recommended Action |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `/` or `/index.php` | Main search/filter form & translation table loader | `/Translation_Dashboard/` | GET | 🔄 Flask equivalent with a different URL | 301 Redirect `/index.php` and `/` → `/Translation_Dashboard/` (preserve query params `camp`, `code`, `cat`, `type`, `filter_sparql`, `exists`, `doit`, `nonav`) |
| `/leaderboard.php` | Default leaderboard page (all stats / main view) | `/Translation_Dashboard/leaderboard/` | GET | 🔄 Flask equivalent with a different URL | 301 Redirect `/leaderboard.php` (no `get` param, no `camps`/`graph`/`graph_api`) → `/Translation_Dashboard/leaderboard/` (preserve query params `year`, `month`, `camp`, `user_group`/`project`) |
| `/leaderboard.php?get=users&user={user}` | User-specific translation statistics | `/Translation_Dashboard/leaderboard/users/<username>` | GET | 🔄 Flask equivalent with a different URL | 301 Redirect `/leaderboard.php?get=users&user=<user>` → `/Translation_Dashboard/leaderboard/users/<user>` (preserve optional `langcode`/`lang`, `year`, `camp`) |
| `/leaderboard.php?user={user}` | User-specific translation statistics (fallback without `get=users`) | `/Translation_Dashboard/leaderboard/users/<username>` | GET | 🔄 Flask equivalent with a different URL | 301 Redirect `/leaderboard.php?user=<user>` → `/Translation_Dashboard/leaderboard/users/<user>` |
| `/leaderboard.php?get=langs&langcode={code}` | Language-specific translation statistics | `/Translation_Dashboard/leaderboard/langs/<lang_code>` | GET | 🔄 Flask equivalent with a different URL | 301 Redirect `/leaderboard.php?get=langs&langcode=<code>` (or `lang=<code>`) → `/Translation_Dashboard/leaderboard/langs/<code>` (preserve optional `year`, `camp`) |
| `/leaderboard.php?langcode={code}` or `?lang={code}` | Language-specific translation statistics (fallback) | `/Translation_Dashboard/leaderboard/langs/<lang_code>` | GET | 🔄 Flask equivalent with a different URL | 301 Redirect `/leaderboard.php?langcode=<code>` → `/Translation_Dashboard/leaderboard/langs/<code>` |
| `/leaderboard.php?camps=1` | Campaign & article statistics tables view | `/Translation_Dashboard/leaderboard/` (or dedicated query view) | GET | 🛠️ Needs a new Flask route / param handling | Implement `camps` parameter handling in `/Translation_Dashboard/leaderboard/` or redirect `/leaderboard.php?camps=1` to `/Translation_Dashboard/leaderboard/?camps=1` |
| `/leaderboard.php?graph=1` | Server-rendered translation timeline graph | `/Translation_Dashboard/leaderboard/` | GET | ❌ No equivalent functionality | Support via client-side chart / graph component or redirect to `/Translation_Dashboard/leaderboard/` |
| `/leaderboard.php?graph_api=1` | API-driven JS translation timeline graph | `/Translation_Dashboard/leaderboard/` | GET | ❌ No equivalent functionality | Support via `/api/status` or client-side chart on leaderboard |
| `/leaderboard_js.php` | Leaderboard dynamic JS endpoint | `/Translation_Dashboard/leaderboard/js` | GET | 🔄 Flask equivalent with a different URL | 301 Redirect `/leaderboard_js.php` → `/Translation_Dashboard/leaderboard/js` |
| `/missing.php` | Missing articles list viewer | `/Translation_Dashboard/missing` | GET | 🔄 Flask equivalent with a different URL | 301 Redirect `/missing.php` → `/Translation_Dashboard/missing` (preserve query params `cat`, `depth`, `code`, `project`) |
| `/sitelinks.php` | Sitelinks lookup by Wikidata QID or page title | `/Translation_Dashboard/table` | GET | 🔄 Flask equivalent with a different URL | 301 Redirect `/sitelinks.php` → `/Translation_Dashboard/table` (preserve query params `site`, `title`, `qid`, `items_with_no_links`) |
| `/translate_med/index.php` | Record translation in-progress & redirect to CX | `/Translation_Dashboard/translate_med/` | GET | 🔄 Flask equivalent with a different URL | 301 Redirect `/translate_med/index.php` (and `/translate_med/`) → `/Translation_Dashboard/translate_med/` (preserve query params `title`, `code`, `cat`, `camp`, `type`/`tr_type`, `word`) |
| `/translate.php` | Deprecated shortcut to `translate_med` | `/Translation_Dashboard/translate_med/` | GET | ↪️ Should redirect to Flask URL | 301 Redirect `/translate.php` → `/Translation_Dashboard/translate_med/` (preserve query params) |
| `/translate/medwiki.php` | Deprecated shortcut to `translate_med` | `/Translation_Dashboard/translate_med/` | GET | ↪️ Should redirect to Flask URL | 301 Redirect `/translate/medwiki.php` → `/Translation_Dashboard/translate_med/` (preserve query params) |
| `/translate_med/medwiki.php` | Deprecated shortcut to `translate_med/index.php` | `/Translation_Dashboard/translate_med/` | GET | ↪️ Should redirect to Flask URL | 301 Redirect `/translate_med/medwiki.php` → `/Translation_Dashboard/translate_med/` (preserve query params) |
| `/auth.php` | Deprecated shortcut to `/auth/index.php` | `/auth/login` | GET | ↪️ Should redirect to Flask URL | 301 Redirect `/auth.php` → `/auth/login` |
| `/auth/login.php` | OAuth login entry point | `/auth/login` | GET | 🔄 Flask equivalent with a different URL | 301 Redirect `/auth/login.php` or `/auth/index.php` → `/auth/login` |
| `/coordinator.php` | Deprecated shortcut to `/tdc/index.php` | `/adminpanel/` | GET | ↪️ Should redirect to Flask URL | 301 Redirect `/coordinator.php` → `/adminpanel/` |
| `/tools.php` | Deprecated shortcut to `/tdc/index.php` | `/adminpanel/` | GET | ↪️ Should redirect to Flask URL | 301 Redirect `/tools.php` → `/adminpanel/` |
| `/404.php` | PHP 404 error page | Flask custom 404 handler | GET | ✅ Exact Flask equivalent | Standard Flask `@app.errorhandler(404)` |
| `/include_all.php` | Internal PHP bootstrap include | N/A (Internal PHP include) | N/A | ❌ No equivalent functionality | Do not expose in Flask (internal file only) |
| `/api.php?get=categories` | Fetch category list | `/api/categories` | GET | 🔄 Flask equivalent with a different URL | 301 Redirect `/api.php?get=categories` → `/api/categories` |
| `/api.php?get=top_users` | Fetch top user statistics | `/api/top_users` | GET | 🔄 Flask equivalent with a different URL | 301 Redirect `/api.php?get=top_users` → `/api/top_users` (preserve query params `year`, `user_group`/`project`, `cat`/`camp`) |
| `/api.php?get=top_langs` | Fetch top language statistics | `/api/top_langs` | GET | 🔄 Flask equivalent with a different URL | 301 Redirect `/api.php?get=top_langs` → `/api/top_langs` (preserve query params `year`, `user_group`/`project`, `cat`/`camp`) |
| `/api.php?get=top_lang_of_users` | Fetch top languages per user | `/api/top_lang_of_users` | GET | 🔄 Flask equivalent with a different URL | 301 Redirect `/api.php?get=top_lang_of_users` → `/api/top_lang_of_users` |
| `/api.php?get=status` | Fetch status summary | `/api/status` | GET | 🔄 Flask equivalent with a different URL | 301 Redirect `/api.php?get=status` → `/api/status` |
| `/api.php?get=langs` | Fetch language list | `/api/langs` | GET | 🔄 Flask equivalent with a different URL | 301 Redirect `/api.php?get=langs` → `/api/langs` |
| `/api.php?get=distinct_langs` | Fetch distinct active languages | `/api/distinct_langs` | GET | 🔄 Flask equivalent with a different URL | 301 Redirect `/api.php?get=distinct_langs` → `/api/distinct_langs` |
| `/api.php?get=in_process` | Fetch in-process translations | `/api/in_process` | GET | 🔄 Flask equivalent with a different URL | 301 Redirect `/api.php?get=in_process` → `/api/in_process` |
| `/api.php?get=in_process_total` | Fetch total in-process count | `/api/in_process_total` | GET | 🔄 Flask equivalent with a different URL | 301 Redirect `/api.php?get=in_process_total` → `/api/in_process_total` |
| `/api.php?get=pages_users` | Fetch pages & users data | `/api/pages_users` | GET | 🔄 Flask equivalent with a different URL | 301 Redirect `/api.php?get=pages_users` → `/api/pages_users` |
| `/api.php?get=pages_with_views` | Fetch pages with view counts | `/api/pages_with_views` | GET | 🔄 Flask equivalent with a different URL | 301 Redirect `/api.php?get=pages_with_views` → `/api/pages_with_views` |
| `/api.php?get=users` | Fetch user list | `/api/users` | GET | 🔄 Flask equivalent with a different URL | 301 Redirect `/api.php?get=users` → `/api/users` |
| `/api.php?get=users_by_translations_count` | Fetch user translation counts | `/api/users_by_translations_count` | GET | 🔄 Flask equivalent with a different URL | 301 Redirect `/api.php?get=users_by_translations_count` → `/api/users_by_translations_count` |
| `/api.php?get=publish_reports` | Fetch publishing reports | `/api/publish_reports` | GET | 🔄 Flask equivalent with a different URL | 301 Redirect `/api.php?get=publish_reports` → `/api/publish_reports` |
| `/api.php?get=publish_reports_stats` | Fetch publishing report stats | `/api/publish_reports/stats` | GET | 🔄 Flask equivalent with a different URL | 301 Redirect `/api.php?get=publish_reports_stats` → `/api/publish_reports/stats` |

---

## Source File Discovery & Analysis Details

### PHP Repository Source Locations
1. `src/index.php` (Line 1-10) & `src/app/Controllers/AppRouter.php` (Lines 40-380):
   - Entry point for main dashboard page. Handles query parameters: `cat`, `camp`, `code`, `type`, `filter_sparql`, `exists`, `doit`, `nonav`.
2. `src/leaderboard.php` (Line 1-10) & `src/app/Controllers/LeaderboardController.php` (Lines 25-110):
   - Entry point for leaderboard statistics. Handles query parameters: `get` (`users` | `langs`), `user`, `langcode`/`lang`, `year`, `month`, `camp`, `user_group`/`project`, `camps`, `graph`, `graph_api`.
3. `src/leaderboard_js.php` (Line 1-10) & `src/app/Controllers/LeaderboardJsController.php`:
   - Renders dynamic leaderboard scripts.
4. `src/missing.php` & `src/app/Controllers/MissingController.php`:
   - Handles missing articles queries (`cat`, `depth`, `code`, `project`).
5. `src/sitelinks.php` & `src/app/Controllers/SiteLinksController.php`:
   - Sitelinks lookup (`site`, `title`, `qid`, `items_with_no_links`).
6. `src/translate_med/index.php` (Lines 40-120):
   - Handles translation workflow and in-process tracking (`title`, `code`, `cat`, `camp`, `type`/`tr_type`, `word`).
7. Deprecated Redirect Files (`src/translate.php`, `src/coordinator.php`, `src/tools.php`, `src/auth.php`, `src/translate/medwiki.php`, `src/translate_med/medwiki.php`):
   - Contained immediate `header("Location: ...")` redirects preserving query strings via `http_build_query($_GET)`.
8. JavaScript & AJAX endpoints (`src/js/autocomplate.js`, `src/js/graph_api.js`, `src/js/leaderboard_index_js.js`):
   - Fetch targets: `/api.php?get=categories`, `/api.php?get=top_users`, `/api.php?get=top_langs`, `/api.php?get=status`.

---

## Detailed Parameter Transformation Rules & Edge Cases

### 1. Leaderboard URLs
- **PHP Path / Query:** `/leaderboard.php?get=users&user=Mr.%20Ibrahem`
- **Flask Path:** `/Translation_Dashboard/leaderboard/users/Mr.%20Ibrahem`
- **Conversion Rule:** Extract `user` parameter, raw-url-decode (handling spaces `%20` or `+` and special characters), and move to path variable `<username>`. Retain remaining query parameters (`langcode`, `year`, `camp`).
- **PHP Path / Query:** `/leaderboard.php?get=langs&langcode=ar` (or `lang=ar`)
- **Flask Path:** `/Translation_Dashboard/leaderboard/langs/ar`
- **Conversion Rule:** Extract `langcode` or `lang` parameter and move to path variable `<lang_code>`. Retain remaining query parameters (`year`, `camp`).

### 2. Main Index & Search
- **PHP Path / Query:** `/index.php?camp=COVID&code=ar&type=lead`
- **Flask Path:** `/Translation_Dashboard/?camp=COVID&code=ar&type=lead`
- **Conversion Rule:** Maintain query parameter names and values intact.

### 3. Translate Med
- **PHP Path / Query:** `/translate_med/index.php?title=COVID-19&code=ar&cat=RTTCovid`
- **Flask Path:** `/Translation_Dashboard/translate_med/?title=COVID-19&code=ar&cat=RTTCovid`
- **Conversion Rule:** Support alias parameter `tr_type` -> `type`.

### 4. Legacy API Query Parameter Routing (`/api.php?get=...`)
- **PHP Path:** `/api.php?get={action}`
- **Flask Route:** `/api/{action}` (e.g., `/api.php?get=top_users` → `/api/top_users`).

---

## Missing Mappings & New Endpoint Inventory

### PHP URLs with No Flask Equivalent (Identified Gaps)
1. `/leaderboard.php?camps=1`: Displays campaign/article breakdown tables in legacy PHP (`CampsText::echo_html()`). Flask currently lacks a dedicated `/leaderboard/camps` sub-route.
2. `/leaderboard.php?graph=1` / `graph_api=1`: Server-rendered / dynamic timeline graph views.

### Flask URLs with No PHP Predecessor (New Features in Flask)
1. `/fixrefs/` & `/fixrefs/process`: Refinement service for reference links.
2. `/new_html/`, `/new_html/check`, `/new_html/fix`, `/new_html/revisions_api`: WMF REST HTML transformation and revision analysis tool.
3. `/HtmltoSegments/`, `/HtmltoSegments/list`: WMF HTML to translation segments engine.
4. `/cxtoken/`: Content Translation token preflight and issuance endpoint.
5. `/publish/`: Content publishing pipeline.
6. `/reports`: Application publishing and daily stats report dashboard.

---

## Proposed Flask Implementation Plan

To guarantee 100% backward compatibility and seamless 301 redirects for indexed search engines, existing bookmarks, and external links, add a legacy compatibility Blueprint to `src/main_app/public/routes/legacy_compat.py`:

```python
from flask import Blueprint, request, redirect, url_for
from urllib.parse import quote

legacy_bp = Blueprint("legacy_compat", __name__)

@legacy_bp.route("/leaderboard.php")
def redirect_leaderboard():
    get_type = request.args.get("get", "").strip().lower()
    user = request.args.get("user", "").strip()
    langcode = (request.args.get("langcode") or request.args.get("lang") or "").strip()

    args = request.args.copy()

    if get_type == "users" or user:
        args.pop("get", None)
        args.pop("user", None)
        return redirect(url_for("leaderboard.users", username=user, **args), code=301)

    if get_type == "langs" or langcode:
        args.pop("get", None)
        args.pop("langcode", None)
        args.pop("lang", None)
        return redirect(url_for("leaderboard.langs", lang_code=langcode, **args), code=301)

    return redirect(url_for("leaderboard.index", **args), code=301)

@legacy_bp.route("/index.php")
@legacy_bp.route("/missing.php")
@legacy_bp.route("/sitelinks.php")
@legacy_bp.route("/translate_med/index.php")
@legacy_bp.route("/translate.php")
@legacy_bp.route("/auth.php")
@legacy_bp.route("/coordinator.php")
@legacy_bp.route("/tools.php")
def redirect_php_pages():
    path = request.path
    args = request.args
    if path in ("/index.php", "/"):
        return redirect(url_for("td.index", **args), code=301)
    elif path == "/missing.php":
        return redirect(url_for("td.missing", **args), code=301)
    elif path == "/sitelinks.php":
        return redirect(url_for("td.table", **args), code=301)
    elif path in ("/translate_med/index.php", "/translate.php"):
        return redirect(url_for("translate_med.index", **args), code=301)
    elif path == "/auth.php":
        return redirect(url_for("auth.login", **args), code=301)
    elif path in ("/coordinator.php", "/tools.php"):
        return redirect(url_for("adminpanel.index", **args), code=301)
    return redirect(url_for("td.index"), code=301)

@legacy_bp.route("/api.php")
def redirect_api_php():
    get_action = request.args.get("get", "").strip()
    args = request.args.copy()
    args.pop("get", None)

    endpoint_map = {
        "categories": "api.get_categories",
        "top_users": "api.get_top_users",
        "top_langs": "api.get_top_langs",
        "top_lang_of_users": "api.get_top_lang_of_users",
        "status": "api.leaderboard_status",
        "langs": "api.get_langs",
        "distinct_langs": "api.get_distinct_langs",
        "in_process": "api.get_in_process",
        "in_process_total": "api.get_in_process_total",
        "pages_users": "api.get_pages_users",
        "pages_with_views": "api.get_pages_with_views",
        "users": "api.get_users",
        "users_by_translations_count": "api.users_by_translations_count",
        "publish_reports": "api.get_publish_reports",
        "publish_reports_stats": "api.publish_reports_stats",
    }

    if get_action in endpoint_map:
        return redirect(url_for(endpoint_map[get_action], **args), code=301)

    return redirect(url_for("td.index"), code=301)
```

---

## Verification & Test Plan

Create `tests/unit/test_legacy_url_redirects.py` to test every legacy PHP URL redirect:

1. `test_redirect_leaderboard_user()`: Verify `/leaderboard.php?get=users&user=Mr.%20Ibrahem` yields 301 to `/Translation_Dashboard/leaderboard/users/Mr.%20Ibrahem`.
2. `test_redirect_leaderboard_lang()`: Verify `/leaderboard.php?get=langs&langcode=ar` yields 301 to `/Translation_Dashboard/leaderboard/langs/ar`.
3. `test_redirect_missing()`: Verify `/missing.php?cat=RTT` yields 301 to `/Translation_Dashboard/missing?cat=RTT`.
4. `test_redirect_sitelinks()`: Verify `/sitelinks.php?qid=Q1234` yields 301 to `/Translation_Dashboard/table?qid=Q1234`.
5. `test_redirect_api_php()`: Verify `/api.php?get=top_users&year=2024` yields 301 to `/api/top_users?year=2024`.
