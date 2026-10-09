# PHP → Flask URL Migration Mapping & Architecture Specification

## Executive Summary
This document provides a complete, production-grade specification and mapping matrix between the legacy PHP repository ([Translation-Dashboard](https://github.com/MrIbrahem/Translation-Dashboard)) and the current Flask repository (`publish_py`).

This updated revision incorporates critical architectural guidelines to guarantee **100% backward compatibility**, prevent silent feature loss, prevent query-string pollution through parameter whitelisting (`allowed_args`), handle special characters/URL encoding properly, and mandate two-stage integration test assertions (`301 Redirect → 200 OK`).

---

## Machine-Readable Route Configuration Matrix (`LEGACY_ROUTES`)

To maintain a single source of truth for both implementation and test suites, legacy routes are defined via the machine-readable data dictionary below:

```python
LEGACY_ROUTES = {
    "/index.php": {
        "target_endpoint": "td.index",
        "allowed_params": {"camp", "code", "cat", "type", "filter_sparql", "exists", "doit", "nonav"},
        "methods": ["GET"],
    },
    "/missing.php": {
        "target_endpoint": "td.missing",
        "allowed_params": {"cat", "depth", "code", "project"},
        "methods": ["GET"],
    },
    "/sitelinks.php": {
        "target_endpoint": "td.table",
        "allowed_params": {"site", "title", "qid", "items_with_no_links"},
        "methods": ["GET"],
    },
    "/translate_med/index.php": {
        "target_endpoint": "translate_med.index",
        "allowed_params": {"title", "code", "cat", "camp", "type", "tr_type", "word"},
        "methods": ["GET"],
    },
    "/translate.php": {
        "target_endpoint": "translate_med.index",
        "allowed_params": {"title", "code", "cat", "camp", "type", "tr_type", "word"},
        "methods": ["GET"],
    },
    "/translate/medwiki.php": {
        "target_endpoint": "translate_med.index",
        "allowed_params": {"title", "code", "cat", "camp", "type", "tr_type", "word"},
        "methods": ["GET"],
    },
    "/translate_med/medwiki.php": {
        "target_endpoint": "translate_med.index",
        "allowed_params": {"title", "code", "cat", "camp", "type", "tr_type", "word"},
        "methods": ["GET"],
    },
    "/auth.php": {
        "target_endpoint": "auth.login",
        "allowed_params": set(),
        "methods": ["GET"],
    },
    "/auth/login.php": {
        "target_endpoint": "auth.login",
        "allowed_params": set(),
        "methods": ["GET"],
    },
    "/coordinator.php": {
        "target_endpoint": "adminpanel.index",
        "allowed_params": set(),
        "methods": ["GET"],
    },
    "/tools.php": {
        "target_endpoint": "adminpanel.index",
        "allowed_params": set(),
        "methods": ["GET"],
    },
    "/leaderboard_js.php": {
        "target_endpoint": "leaderboard.index_js",
        "allowed_params": set(),
        "methods": ["GET"],
    },
}
```

---

## Complete PHP → Flask URL Mapping Matrix

| PHP URL | PHP Purpose | Flask Target Route | HTTP Method | Migration Status | Recommended Action | Whitelisted Query Params |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `/index.php` | Main search & translation table | `/Translation_Dashboard/` | GET | 🔄 Flask equivalent with different URL | 301 Redirect to `/Translation_Dashboard/` | `camp`, `code`, `cat`, `type`, `filter_sparql`, `exists`, `doit`, `nonav` |
| `/` | Application root entry | `/` or `/Translation_Dashboard/` | GET | ✅ Direct Flask Route | Direct view or dedicated redirect rule (separate from `/index.php`) | N/A |
| `/leaderboard.php` | Main Leaderboard | `/Translation_Dashboard/leaderboard/` | GET | 🔄 Flask equivalent with different URL | Whitelisted 301 Redirect to `/Translation_Dashboard/leaderboard/` | `year`, `month`, `camp`, `user_group`, `project` |
| `/leaderboard.php?get=users&user={user}` | User Stats | `/Translation_Dashboard/leaderboard/users/<username>` | GET | 🔄 Flask equivalent with different URL | Whitelisted 301 Redirect extracting `user` to path | `year`, `month`, `camp`, `langcode`, `lang` |
| `/leaderboard.php?user={user}` | User Stats (fallback) | `/Translation_Dashboard/leaderboard/users/<username>` | GET | 🔄 Flask equivalent with different URL | Whitelisted 301 Redirect extracting `user` to path | `year`, `month`, `camp`, `langcode`, `lang` |
| `/leaderboard.php?get=langs&langcode={code}` | Language Stats | `/Translation_Dashboard/leaderboard/langs/<lang_code>` | GET | 🔄 Flask equivalent with different URL | Whitelisted 301 Redirect extracting `langcode`/`lang` to path | `year`, `month`, `camp` |
| `/leaderboard.php?langcode={code}` or `?lang={code}` | Language Stats (fallback) | `/Translation_Dashboard/leaderboard/langs/<lang_code>` | GET | 🔄 Flask equivalent with different URL | Whitelisted 301 Redirect extracting `langcode`/`lang` to path | `year`, `month`, `camp` |
| `/leaderboard.php?camps=1` | Campaign & Article Tables | `/Translation_Dashboard/leaderboard/camps` | GET | 🛠️ Needs new Flask route | Implement `/leaderboard/camps` sub-route before issuing 301 redirect | `year`, `month` |
| `/leaderboard.php?graph=1` | Server-rendered graph | `/Translation_Dashboard/leaderboard/graph` | GET | 🛠️ Needs new Flask route | Implement client-side or server graph endpoint before issuing 301 redirect | `year`, `camp` |
| `/leaderboard.php?graph_api=1` | API-driven JS graph | `/Translation_Dashboard/leaderboard/graph_api` | GET | 🛠️ Needs new Flask route | Implement API-driven chart handler before issuing 301 redirect | `year`, `camp` |
| `/leaderboard_js.php` | Leaderboard dynamic JS | `/Translation_Dashboard/leaderboard/js` | GET | 🔄 Flask equivalent with different URL | 301 Redirect to `/Translation_Dashboard/leaderboard/js` | None |
| `/missing.php` | Missing articles list | `/Translation_Dashboard/missing` | GET | 🔄 Flask equivalent with different URL | Whitelisted 301 Redirect | `cat`, `depth`, `code`, `project` |
| `/sitelinks.php` | Sitelinks lookup | `/Translation_Dashboard/table` | GET | 🔄 Flask equivalent with different URL | Whitelisted 301 Redirect | `site`, `title`, `qid`, `items_with_no_links` |
| `/translate_med/index.php` | CX Translate Trigger | `/Translation_Dashboard/translate_med/` | GET | 🔄 Flask equivalent with different URL | Whitelisted 301 Redirect | `title`, `code`, `cat`, `camp`, `type`, `tr_type`, `word` |
| `/translate.php` | Legacy alias to CX | `/Translation_Dashboard/translate_med/` | GET | ↪️ Shortcut 301 Redirect | Whitelisted 301 Redirect | `title`, `code`, `cat`, `camp`, `type`, `tr_type`, `word` |
| `/translate/medwiki.php` | Legacy alias to CX | `/Translation_Dashboard/translate_med/` | GET | ↪️ Shortcut 301 Redirect | Whitelisted 301 Redirect | `title`, `code`, `cat`, `camp`, `type`, `tr_type`, `word` |
| `/translate_med/medwiki.php` | Legacy alias to CX | `/Translation_Dashboard/translate_med/` | GET | ↪️ Shortcut 301 Redirect | Whitelisted 301 Redirect | `title`, `code`, `cat`, `camp`, `type`, `tr_type`, `word` |
| `/auth.php` | Legacy login alias | `/auth/login` | GET | ↪️ Shortcut 301 Redirect | 301 Redirect to `/auth/login` | None |
| `/auth/login.php` | OAuth Login | `/auth/login` | GET | 🔄 Flask equivalent with different URL | 301 Redirect to `/auth/login` | None |
| `/coordinator.php` | Admin alias | `/adminpanel/` | GET | ↪️ Shortcut 301 Redirect | 301 Redirect to `/adminpanel/` | None |
| `/tools.php` | Admin alias | `/adminpanel/` | GET | ↪️ Shortcut 301 Redirect | 301 Redirect to `/adminpanel/` | None |
| `/404.php` | PHP 404 handler | Flask errorhandler(404) | GET | ✅ Exact Flask equivalent | Custom Flask 404 handler | None |
| `/include_all.php` | Internal PHP include | N/A | N/A | ❌ No equivalent functionality | Do not expose in Flask | None |

---

## Architectural Guidelines & Implementation Requirements

### 1. Query Parameter Whitelisting (`allowed_args`)
To prevent query string pollution, invalid key collisions, and `url_for()` parameter mismatch errors, all redirects MUST filter incoming `request.args` against an allowed whitelist:

```python
def allowed_args(args: dict, allowed_keys: set) -> dict:
    return {k: v for k, v in args.items() if k in allowed_keys and v != ""}
```

### 2. Separation of Root `/` and `/index.php`
- `/` is the modern application root endpoint handled directly by `main.index` or `td.index`. It MUST NOT be grouped in legacy wildcard redirect logic.
- `/index.php` is explicitly a legacy PHP page route and MUST issue a 301 redirect to `/Translation_Dashboard/` with whitelisted query parameters.

### 3. Gap Endpoints Handling (`camps=1`, `graph=1`, `graph_api=1`)
To prevent **silent feature loss**, legacy URLs requesting specialized views MUST NOT be blindly redirected to the generic leaderboard index.
- `/leaderboard.php?camps=1`: Must route to a dedicated campaign view endpoint (e.g., `/Translation_Dashboard/leaderboard/camps`) or return campaign table HTML once implemented.
- `/leaderboard.php?graph=1` & `?graph_api=1`: Must route to dedicated graph views once ported, or abort with clear notice rather than serving wrong content under 301.

### 4. URL Encoding & Special Characters
Path parameters extracted from query strings (such as usernames and language codes) must be processed carefully:
- `Mr.%20Ibrahem` / `Mr.+Ibrahem`: Extracted by Flask's `request.args.get('user')` automatically unquotes to `Mr. Ibrahem`.
- Passing `username="Mr. Ibrahem"` to `url_for("leaderboard.users", username=user)` formats it safely to `/Translation_Dashboard/leaderboard/users/Mr.%20Ibrahem` without double-encoding (`%2520`).
- Usernames containing slashes (`/` or `%2F`) must use Werkzeug path converters `<path:username>` if permitted or be safely sanitized.

### 5. Modular Flask Blueprint Registration Class (`LegacyRoutes`)

```python
from flask import Blueprint, request, redirect, url_for, abort, Response
from typing import Dict, Any, Set

def allowed_args(args: Any, allowed_keys: Set[str]) -> Dict[str, str]:
    return {k: v for k, v in args.items() if k in allowed_keys and v != ""}

class LegacyRoutes:

    @classmethod
    def register(cls, bp: Blueprint) -> None:
        bp.add_url_rule("/leaderboard.php", view_func=cls.legacy_leaderboard, methods=["GET"])
        bp.add_url_rule("/index.php", view_func=cls.legacy_index, methods=["GET"])
        bp.add_url_rule("/missing.php", view_func=cls.legacy_missing, methods=["GET"])
        bp.add_url_rule("/sitelinks.php", view_func=cls.legacy_sitelinks, methods=["GET"])

        for path in ["/translate_med/index.php", "/translate.php", "/translate/medwiki.php", "/translate_med/medwiki.php"]:
            bp.add_url_rule(path, view_func=cls.legacy_translate, methods=["GET"])

        for path in ["/auth.php", "/auth/login.php"]:
            bp.add_url_rule(path, view_func=cls.legacy_auth, methods=["GET"])

        for path in ["/coordinator.php", "/tools.php"]:
            bp.add_url_rule(path, view_func=cls.legacy_admin, methods=["GET"])

        bp.add_url_rule("/leaderboard_js.php", view_func=cls.legacy_leaderboard_js, methods=["GET"])

    @staticmethod
    def legacy_leaderboard() -> Response:
        get_type = request.args.get("get", "").strip().lower()
        user = request.args.get("user", "").strip()
        lang = (request.args.get("langcode") or request.args.get("lang") or "").strip()
        camps = request.args.get("camps", "").strip()
        graph = request.args.get("graph", "").strip()
        graph_api = request.args.get("graph_api", "").strip()

        # Handle specialized views (camps / graph)
        if camps == "1":
            params = allowed_args(request.args, {"year", "month"})
            return redirect(url_for("leaderboard.camps", **params), code=301)

        if graph == "1" or graph_api == "1":
            params = allowed_args(request.args, {"year", "camp"})
            return redirect(url_for("leaderboard.graph", **params), code=301)

        # User Leaderboard
        if get_type == "users" or user:
            if not user:
                abort(400, description="User parameter is required for user leaderboard")
            params = allowed_args(request.args, {"year", "month", "camp", "langcode", "lang"})
            return redirect(url_for("leaderboard.users", username=user, **params), code=301)

        # Language Leaderboard
        if get_type == "langs" or lang:
            if not lang:
                abort(400, description="Language parameter is required for language leaderboard")
            params = allowed_args(request.args, {"year", "month", "camp"})
            return redirect(url_for("leaderboard.langs", lang_code=lang, **params), code=301)

        # Main Leaderboard
        params = allowed_args(request.args, {"year", "month", "camp", "user_group", "project"})
        return redirect(url_for("leaderboard.index", **params), code=301)

    @staticmethod
    def legacy_index() -> Response:
        params = allowed_args(request.args, {"camp", "code", "cat", "type", "filter_sparql", "exists", "doit", "nonav"})
        return redirect(url_for("td.index", **params), code=301)

    @staticmethod
    def legacy_missing() -> Response:
        params = allowed_args(request.args, {"cat", "depth", "code", "project"})
        return redirect(url_for("td.missing", **params), code=301)

    @staticmethod
    def legacy_sitelinks() -> Response:
        params = allowed_args(request.args, {"site", "title", "qid", "items_with_no_links"})
        return redirect(url_for("td.table", **params), code=301)

    @staticmethod
    def legacy_translate() -> Response:
        params = allowed_args(request.args, {"title", "code", "cat", "camp", "type", "tr_type", "word"})
        return redirect(url_for("translate_med.index", **params), code=301)

    @staticmethod
    def legacy_auth() -> Response:
        return redirect(url_for("auth.login"), code=301)

    @staticmethod
    def legacy_admin() -> Response:
        return redirect(url_for("adminpanel.index"), code=301)

    @staticmethod
    def legacy_leaderboard_js() -> Response:
        return redirect(url_for("leaderboard.index_js"), code=301)
```

---

## Two-Stage Redirect Verification Strategy (`301 Redirect → 200 OK`)

To verify that legacy PHP URLs are properly migrated and that destination endpoints exist and respond correctly, test cases MUST assert both HTTP status codes in sequence:

1. Request legacy PHP URL -> Assert status `301 Moved Permanently` and location header.
2. Request redirected destination URL -> Assert status `200 OK` (or `302` for auth redirects).

### Example Test Suite (`tests/unit/test_legacy_url_redirects.py`)

```python
import pytest
from flask.testing import FlaskClient

class TestLegacyUrlRedirects:

    def test_leaderboard_user_two_stage_redirect(self, client: FlaskClient):
        # Stage 1: Legacy PHP URL -> 301
        res1 = client.get("/leaderboard.php?get=users&user=Mr.%20Ibrahem&foo=bar")
        assert res1.status_code == 301
        assert "/Translation_Dashboard/leaderboard/users/Mr.%20Ibrahem" in res1.location
        assert "foo=bar" not in res1.location  # Whitelist verification

        # Stage 2: Destination URL -> 200 OK
        res2 = client.get(res1.location)
        assert res2.status_code == 200

    def test_missing_two_stage_redirect(self, client: FlaskClient):
        res1 = client.get("/missing.php?cat=RTT&depth=1")
        assert res1.status_code == 301
        assert "/Translation_Dashboard/missing?cat=RTT&depth=1" in res1.location

        res2 = client.get(res1.location)
        assert res2.status_code == 200
```
