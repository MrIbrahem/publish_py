# Mirror `translate_med.php` → `translate_med.py`

Port the PHP "go translate" endpoint into the existing Flask route class
`TranslateRoutes`, so that
[src/main_app/public/routes/td/translate_med.py](../../src/main_app/public/routes/td/translate_med.py)
is a faithful mirror of
[src/main_app/public/routes/td/translate_med.php](../../src/main_app/public/routes/td/translate_med.php).

---

## Table of Contents

1. [Endpoint Facts](#endpoint-facts)
2. [PHP Behavior Reference](#php-behavior-reference)
3. [Gap Analysis of the Current Stub](#gap-analysis-of-the-current-stub)
4. [Target Implementation](#target-implementation)
5. [Template](#template)
6. [Deviations and Rationale](#deviations-and-rationale)
7. [Security Considerations](#security-considerations)
8. [Testing Strategy](#testing-strategy)
9. [Implementation Checklist](#implementation-checklist)

---

## Endpoint Facts

| Item | Value |
|---|---|
| Blueprint name | `translate_med` |
| URL prefix | `/Translation_Dashboard/translate_med` |
| Route rule | `GET /` (i.e. `/Translation_Dashboard/translate_med/`) |
| Endpoint name | `translate_med.index` |
| Registration | [src/main_app/public/__init__.py:45](../../src/main_app/public/__init__.py#L45) |
| Inbound links | `tr_link_medwiki()` in [services/utils/wiki_links.py:80](../../src/main_app/services/utils/wiki_links.py#L80), used by `results_2026/rows/missing_row_builder.py`, `results_2026/mapping/missing_mapping.py`, `admin/routes/email_msg.py` |

Query string emitted by every in-repo caller (`tr_link_medwiki`):

```
?title=…&langcode=…&cat=…&camp=…&word=…&tra_type=…
```

The route **must** accept all six names, plus `test` used by the PHP page.

---

## PHP Behavior Reference

Line-by-line reading of [translate_med.php](../../src/main_app/public/routes/td/translate_med.php):

| PHP lines | Behavior |
|---|---|
| 6–26 | `execute_query()` — raw SQL helper (no Python equivalent needed; replaced by services). |
| 27–52 | `make_ContentTranslation_url()` — builds `Special:ContentTranslation` URL; `%20` → `_` in the title; query params `title`, `tr_type`, `from=mdwiki`, `to`, `campaign`, `page`. |
| 54–65 | `get_td_or_sql_users_no_inprocess()` — map `user` → `is_active`. |
| 67–81 | `get_td_or_sql_categories()` — map `category` → `campaign`. |
| 83–88 | `get_endpoint()` — constant `https://mdwikicx.toolforge.org/w/index.php`. |
| 90–108 | `insertPage()` — **dead code in this file** (never called from the main flow); inserts into the `pages` table. |
| 110–129 | `insertPage_inprocess()` — `INSERT … WHERE NOT EXISTS` guarded insert into `in_process`. |
| 131–163 | `go_to_translate_url()` — echoes an `<h2>` "Click here" link; when `$_GET['test']` is empty also emits `window.open(url, '_self')` + two `<meta http-equiv="refresh">` tags. |
| 165–167 | Reads `code` (lowercased), `title`, and `$GLOBALS['global_username']`. |
| 169–184 | No user → render a Bootstrap login card linking to `/auth/login.php`, then `exit`. |
| 186–205 | Requires `title` **and** `code`; reads `cat`, `camp`, `type` (default `lead`), `word` (int, default 0, `min_range` 0). |
| 207–209 | If `camp` empty and `cat` set → `camp = cats_data[cat]`. |
| 211–215 | `rawurldecode()` on user, cat, title, camp. |
| 216–218 | Insert into `in_process` **only if** the user is not an active `users_no_inprocess` member. |
| 220–229 | Build the URL and emit the redirect page. |
| 232–240 | Echo the layout closing tags (handled by the base template in Python). |

---

## Gap Analysis of the Current Stub

State of [translate_med.py](../../src/main_app/public/routes/td/translate_med.py) versus the PHP flow,
after the `redirect(...)` return was added:

| # | Gap | Status |
|---|---|---|
| 1 | `index()` fell through and returned `None`. | **Fixed** — now ends in `redirect(content_translation_url(...))` at [translate_med.py:68](../../src/main_app/public/routes/td/translate_med.py#L68). |
| 2 | No `cat → campaign` resolution when `camp` is omitted. | Open — PHP lines 207–209 have no counterpart. |
| 3 | `users_no_inprocess` gate missing. | Open — every logged-in user gets an `in_process` row; PHP skips active members of that table. |
| 4 | Required-args check rejects a missing `tra_type`/`cat`. | Open — PHP defaults `type` to `lead` and tolerates an empty `cat`; the current check 404s valid links. |
| 5 | `word` read with `type=int` but no `min_range` clamp. | Open — negative values pass through; PHP clamps to 0. |
| 6 | `test` flag. | **Dropped** — meaningless with a 302 (see [Deviations](#deviations-and-rationale)); the PHP preview mode has no intermediate page to render. |
| 7 | Anonymous user returns the bare string `"Not logged in"`; invalid args return `"Invalid request"`. | Open — both are valid Flask responses, but neither renders the PHP login card / error markup. |
| 8 | `get_current_user` imported from `....services.auth` (package) while [td_route.py:26](../../src/main_app/public/routes/td/td_route.py#L26) imports from `....services.auth.utils`. | Open — both work; standardize on `.utils` for consistency. |
| 9 | No use of the already-ported `content_translation_url()` / `get_endpoint()` helpers. | **Fixed** — both are now imported and used at [translate_med.py:15](../../src/main_app/public/routes/td/translate_med.py#L15). |

---

## Target Implementation

### Route skeleton

```python
"""
Mirror of src/main_app/public/routes/td/translate_med.php — redirects the
logged-in translator to Special:ContentTranslation after registering the
title in the in_process table.
"""

from __future__ import annotations

import logging

from flask import (
    Blueprint,
    redirect,
    render_template,
    request,
    url_for,
)

from ....database.services import (
    CategoryService,
    InProcessService,
    UsersNoInprocessService,
)
from ....services.auth.utils import get_current_user
from ....services.utils.wiki_links import (
    content_translation_url,
    get_endpoint,
)

logger = logging.getLogger(__name__)

_DEFAULT_TRA_TYPE = "lead"


class TranslateRoutes:
    def __init__(self, bp: Blueprint) -> None:
        self.bp = bp
        self.in_process_service = InProcessService()
        self.category_service = CategoryService()
        self.no_inprocess_service = UsersNoInprocessService()
        self._setup_routes()

    def _setup_routes(self) -> None:
        routes = [
            ("/", "GET", self.index),
        ]
        for rule, method, target in routes:
            self.bp.route(rule, methods=[method])(target)

    def index(self) -> str:
        user = get_current_user()
        if user is None:
            # PHP: login card linking to /auth/login.php, then exit.
            return render_template(
                "td/translate_med.html",
                login_url=url_for("auth.login"),
            )

        title = _normalize(request.args.get("title"))
        langcode = _normalize(request.args.get("langcode")).lower()

        # PHP requires both title and code; otherwise it renders an empty page.
        if not title or not langcode:
            return render_template("td/translate_med.html")

        cat = _normalize(request.args.get("cat"))
        camp = _normalize(request.args.get("camp"))
        tra_type = _normalize(request.args.get("tra_type")) or _DEFAULT_TRA_TYPE
        word = _word(request.args.get("word"))

        # PHP lines 207-209: resolve the campaign from the category.
        if not camp and cat:
            camp = self._campaign_of(cat)

        if not self.no_inprocess_service.should_hide_from_inprocess(user.username):
            self._register_in_process(
                title=title,
                user=user.username,
                lang=langcode,
                cat=cat,
                tra_type=tra_type,
                word=word,
            )

        # PHP prints an intermediate page with a "Click here" link plus a
        # JS/meta auto-redirect; this port issues a straight 302 instead.
        return redirect(
            content_translation_url(
                title=title,
                code=langcode,
                campaign=camp,
                tra_type=tra_type,
                endpoint=get_endpoint(),
            )
        )
```

### Argument parsing helpers

| PHP | Python | Notes |
|---|---|---|
| `filter_input(INPUT_GET, 'code')` + `strtolower` | `_normalize(request.args.get("langcode")).lower()` | Name stays `langcode` — see [Deviations](#deviations-and-rationale). |
| `filter_input(INPUT_GET, 'title')` | `_normalize(request.args.get("title"))` | `_normalize` = `strip()`; mirrors the PHP `trim()` calls (lines 195–197). |
| `$_GET['type'] ?? 'lead'` | `tra_type or _DEFAULT_TRA_TYPE` | PHP default is `"lead"`. |
| `FILTER_VALIDATE_INT, min_range 0, default 0` | `_word()` helper: `max(int(value or 0), 0)` with `try/except ValueError` | Clamp negative values to 0. |
| `$_GET['test'] ?? ''` (truthy = keep the page) | — | **Dropped.** The 302 has no intermediate page to preview, so the flag serves no purpose. |

### Service / helper reuse map

| PHP construct | Python replacement | Already exists |
|---|---|---|
| `get_td_or_sql_categories()` + `array_column(…, "campaign", "category")` | `CategoryService().list_categories()` → `{r.category: r.campaign for r in rows}` | yes — [category_service.py:105](../../src/main_app/database/services/content/category_service.py#L105) |
| `get_td_or_sql_users_no_inprocess()` + `is_active` check | `UsersNoInprocessService().should_hide_from_inprocess(user)` | yes — [users_no_inprocess_service.py:76](../../src/main_app/database/services/users/users_no_inprocess_service.py#L76) |
| `insertPage_inprocess()` (idempotent insert) | `InProcessService.get_in_process_by_title_user_lang()` then `add_in_process()` | yes — [in_process_service.py:53-89](../../src/main_app/database/services/pages/in_process_service.py#L53) |
| `make_ContentTranslation_url()` | `content_translation_url()` | yes — [wiki_links.py:99](../../src/main_app/services/utils/wiki_links.py#L99) |
| `get_endpoint()` | `get_endpoint()` | yes — [wiki_links.py:148](../../src/main_app/services/utils/wiki_links.py#L148) |
| `insertPage()` (pages table) | — | **skip**: unreachable in the PHP flow; if ever needed it belongs in `PagesService`, not here. |

`_register_in_process()` must stay idempotent: PHP uses
`INSERT … WHERE NOT EXISTS`, and the dashboard links fire repeatedly.

---

## Template

**No longer required for the happy path.** With the 302 in place, the redirect
branch produces no HTML of its own, so `td/translate_med.html` is only relevant
to the two non-redirect branches — which currently return bare strings
(`"Not logged in"`, `"Invalid request"`). Porting the PHP login card is
optional polish; if added, extend the existing TD base layout
([td_base.html](../../src/templates/td/td_base.html), which provides
`{% block content %}`):

```html
{% extends "td/td_base.html" %}

{% block title %}Translate — Translation Dashboard{% endblock %}

{% block content %}
<div class="container py-4">
  {% if login_url %}
    <div class="card">
      <div class="card-body">
        <a role="button" class="btn btn-outline-primary" href="{{ login_url }}">
          <i class="fas fa-sign-in-alt fa-sm fa-fw me-1"></i><span>Login</span>
        </a>
      </div>
    </div>
  {% else %}
    <div class="alert alert-warning">
      Invalid request — <code>title</code> and <code>langcode</code> are required.
    </div>
  {% endif %}
</div>
{% endblock %}
```

The two mutually exclusive states map to the remaining PHP branches:
anonymous (`login_url` set) and missing params.

---

## Deviations and Rationale

1. **`langcode` instead of PHP's `code`.**
   Every Python caller already emits `langcode` via `tr_link_medwiki()`
   ([wiki_links.py:90](../../src/main_app/services/utils/wiki_links.py#L90)).
   Renaming the route param to `code` would break those callers, so the port
   keeps `langcode`. This matches the current stub and the
   `plan_port_results_2026.md` decision to preserve the relative link shape.

2. **`tra_type` instead of PHP's `type`.**
   Same reason — `tr_link_medwiki()` emits `tra_type`, and commit
   `2ce6d943` ("Use tra_type for translation links") already standardized the
   dashboard on that name. The value is passed straight through to the CX URL
   as `tr_type` by `content_translation_url()`.

3. **No double `rawurldecode()`.**
   PHP calls `rawurldecode()` on values that `filter_input` already decoded
   once, i.e. a historical double-decode. Werkzeug decodes query args exactly
   once; adding a second decode would mangle titles containing literal `%`
   sequences. Documented deviation — flag for review if a legacy link is found
   that relies on the double decode.

4. **Response is an HTTP 302, not the PHP intermediate page.**
   `index()` ends with `redirect(content_translation_url(...))`
   ([translate_med.py:68](../../src/main_app/public/routes/td/translate_med.py#L68))
   instead of echoing an intermediate page that carries a "Click here" link
   plus `window.open(..., '_self')` and `<meta http-equiv="refresh">` tags.
   The 302 needs no JavaScript, so the PHP fallback markup and the `test`
   preview flag that gated it are dropped. *(This supersedes the earlier
   revision of this plan, which recommended the rendered page; the 302 is now
   the chosen behavior.)* The intermediate page can still be reproduced later,
   e.g. behind `test=1`, if a debug view is ever wanted.

5. **No `insertPage()` port.**
   The function is defined but never invoked by this PHP file. Port it into
   `PagesService` only if another route turns out to need it.

---

## Security Considerations

The PHP page interpolates `$url` directly into single-quoted HTML attributes
and a `<meta http-equiv="refresh">` tag, so a crafted `title`/`camp`/`coden`
can inject markup (attribute breakout via `'`, or `">` in the meta tag). The
302 port removes that whole surface — there is no template rendering on the
happy path:

- `content_translation_url()` runs every component through
  `urlencode(…, quote_via=quote)`, so the `Location` value is well-formed and
  cannot smuggle CR/LF (header injection) or markup.
- Werkzeug escapes the target URL inside the small redirect body it renders,
  so nothing from the query string reaches the response as raw HTML.
- The endpoint is an **intentional** open redirect: its only job is to send the
  user to `Special:ContentTranslation`. `get_endpoint()` is a hardcoded
  `mdwikicx.toolforge.org` constant
  ([wiki_links.py:148](../../src/main_app/services/utils/wiki_links.py#L148))
  and `content_translation_url()` assembles the URL from it, so a request
  cannot point the redirect at an arbitrary host — keep that constant the sole
  source of the host.
- If the intermediate page is ever reintroduced, render `{{ url }}` with plain
  Jinja (**no `|safe`**) and add `rel="noopener"` to any `target="_blank"` link.

---

## Testing Strategy

New test module `tests/unit/public/routes/td/test_translate_med.py`, following
the fixture style of
[test_api_routes_unit.py](../../tests/unit/public/routes/api/test_api_routes_unit.py)
(seeded services, real test DB, no ORM mocks).

Cases to cover:

| Case | Assertion |
|---|---|
| Anonymous request | 200; response contains a link to the auth login URL; **no** `in_process` row created. |
| Missing `title` or `langcode` | Non-3xx response (current code returns the string `"Invalid request"`); no `in_process` row, no `Location` header. |
| Logged-in, valid params | **302**; `Location` header contains `mdwikicx.toolforge.org` with `page=<title>`, `to=<langcode>`, `campaign=<camp>`; exactly one `in_process` row for (title, user, lang). |
| Repeated request (same title/user/lang) | Still one row — idempotent insert. |
| `cat` given, `camp` omitted | Campaign resolved from the seeded category. |
| `word` negative or non-numeric | Clamped/fallback to 0; no 500. |
| Active `users_no_inprocess` user | No `in_process` row inserted; 302 still issued. |
| Injected markup in `title` (e.g. `'"><script>` or `%0d%0a`) | No header injection, no raw `<script>` in the redirect body; the title stays percent-encoded inside `Location`. |

Route wiring is already covered by the blueprint registration; no changes to
`public/__init__.py` are expected.

---

## Implementation Checklist

### Phase 1 — Route logic

- [ ] Replace the argument parsing in `translate_med.py` with the six-param
      scheme (`title`, `langcode`, `cat`, `camp`, `tra_type`, `word`) plus
      `test`.
- [ ] Fix the `get_current_user` import to `....services.auth.utils`.
- [ ] Add `CategoryService` + `UsersNoInprocessService` to `__init__`.
- [ ] Implement the `cat → campaign` fallback.
- [ ] Implement the `users_no_inprocess` gate around the `in_process` insert.
- [ ] Build the CX URL via `content_translation_url()` + `get_endpoint()`.

### Phase 2 — Response

- [x] End `index()` with `redirect(content_translation_url(...))`.
- [ ] Return a value from every branch — the `None` fall-through is gone, but
      the two string branches (`"Not logged in"`, `"Invalid request"`) still
      diverge from the PHP login card / error markup.
- [ ] (Optional) Add `src/templates/td/translate_med.html` for the login-card
      and invalid-request branches only — not for the redirect path.

### Phase 3 — Tests

- [ ] Add `tests/unit/public/routes/td/test_translate_med.py` with the cases
      listed above.
- [ ] Run `pytest tests/unit/public/routes/td` and the full suite.
- [ ] Run `ruff check` / `ruff format` / `black` / `isort` on touched files.

### Phase 4 — Verification

- [ ] Click a Translate/Lead/Full button on the local dashboard and confirm
      a single 302 hop lands the browser on `Special:ContentTranslation`, with
      the `in_process` row created.
- [ ] Compare a side-by-side URL dump from the PHP and Python endpoints for
      the same input tuple (`title`, `code`, `cat`, `camp`, `type`, `word`).
