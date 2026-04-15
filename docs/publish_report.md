# Publish Endpoint: PHP vs Python Comparison Report

## 1. Overview

The Python implementation is a thorough port of the PHP publish endpoint, covering the core flow: CORS validation, request parsing, access credential lookup, revid resolution, text processing (fix_refs), edit submission, Wikidata linking, database insertion, and report logging. The overall architecture is well-matched, with Flask blueprints replacing the flat PHP endpoint and modular services replacing the PHP namespace-based includes. However, several behavioral differences exist — some critical (e.g., missing `words` field in `tab`, different `determine_hashtag` logic, missing `tr_type` parameter, different `to_do` file output format) and some minor (e.g., different CORS resolution, `rand_id` handling, file-report directory structure).

---

## 2. ✅ What is correctly implemented

-   **POST-only endpoint**: Python enforces POST-only via Flask route (`methods=["POST"]`), mirroring PHP's `$_SERVER['REQUEST_METHOD'] !== 'POST'` check.
-   **CORS checking**: Both check Referer/Origin against allowed domains; both return 403 on failure. Python adds an explicit OPTIONS preflight handler.
-   **CORS headers on responses**: Both set `Access-Control-Allow-Origin` header on success responses.
-   **403 for no access**: Both return 403 when user credentials are not found (`handleNoAccess`/`_handle_no_access`).
-   **Request parameter mapping**: Both map `target` → `lang`, `sourcetitle`, `title`, `user`, `campaign`, `text`, `revid`/`revision`, `wpCaptchaId`, `wpCaptchaWord`.
-   **`formatUser`/`formatTitle`**: Both replace underscores with spaces and apply special user mappings.
-   **`make_summary`**: Both produce the same summary format: `Created by translating the page [[:mdwiki:Special:Redirect/revision/{revid}|{sourcetitle}]] to:{lang} {hashtag}`.
-   **`get_revid` / `get_revid_db`**: Both read a local JSON file first, then fall back to an API call. Both set `"empty revid"` flag and fall back to `request['revid']`/`request['revision']`.
-   **`do_changes_to_text` (text_changes)**: Both attempt to load the `fix_refs` module and call `DoChangesToText1`, falling back to returning the original text if unavailable.
-   **`publish_do_edit`**: Both construct the same API parameters (`action=edit`, `title`, `summary`, `text`, `format=json`, captcha params), get a CSRF token, and POST via OAuth. Both return the parsed JSON edit result.
-   **`shouldAddedToWikidata` / `GetTitleInfo`**: Both query the MediaWiki API with `formatversion=2` and check `ns == 2` to skip user pages.
-   **`link_to_wikidata` / `LinkToWikidata`**: Both look up the QID, call `wbsetsitelink` with `id` or `title/site`, detect `success` return, and return `{result: "success", qid}`.
-   **`retryWithFallbackUser`**: Both retry with a fallback user ("Mr. Ibrahem" / `settings.users.fallback_user`) when `get_csrftoken` fails, storing `fallback_user` and `original_user` in the result.
-   **`add_to_db` / `insert_to_db`**: Both normalize underscores, validate non-empty fields, compute `use_user_sql`, check for existing records, and insert into `pages` or `pages_users`.
-   **`InsertPublishReports`**: Both INSERT into `publish_reports` with `date`, `title`, `user`, `lang`, `sourcetitle`, `result`, `data` (JSON-encoded).
-   **`get_errors_file`**: Both match error strings against a main list (`protectedpage`, `titleblacklist`, etc.) or a Wikidata-specific map (`Links to user pages` → `wd_user_pages`, etc.).
-   **`load_to_do_file`**: Both classify edit results as `success`, `captcha`, or a specific error name.
-   **Encryption/decryption**: Both use Fernet/Defuse Crypto for encrypting OAuth tokens at rest.
-   **`find_exists_or_update`**: Both SELECT from the table, then UPDATE target+pupdate where target is empty or NULL.

---

## 3. ❌ What is missing

### 3.1 `rand_id` parameter omitted from `to_do` calls

-   **What it does in PHP**: `to_do($tab, $file_name, $rand_id)` creates a per-request directory `{YYYY/MM/DD}/{rand_id}/` and writes the report JSON file there. The `rand_id` is `time() . "-" . bin2hex(random_bytes(6))` generated at the start of each request.
-   **Where**: `start.php:92`, `process_edit.php:181`, `start.php:82`
-   **Impact**: **Minor** — Python generates its own `rand_id` via `uuid.uuid4().hex[:8]` but only once per process (module-level `_RAND_ID`), whereas PHP generates a new one per request. This means all requests in the same Python process share the same directory, unlike PHP which uses unique per-request directories.

### 3.2 `words` field not set in `tab`

-   **What it does in PHP**: `start.php:114` — `$tab['words'] = $Words_table[$title] ?? 0;` stores the word count from the words table in the `tab` dict, which is later passed to `add_to_db` and logged.
-   **Where**: `start.php:113-114`
-   **Impact**: **Minor** — The word count is still passed to `_add_to_db` via `get_word_count()` in Python, but it is not stored in `tab` for logging/debugging purposes. The `tab` dict written to reports will be missing the `words` key.

### 3.3 `tr_type` parameter not passed through from request

-   **What it does in PHP**: `start.php:116` — `$tr_type = $request['tr_type'] ?? 'lead';` reads `tr_type` from the request and passes it to `processEdit` → `add_to_db`, which uses it as `translate_type` in the INSERT.
-   **Where**: `start.php:116`, `process_edit.php:140`, `process_db_log.php:61`
-   **Impact**: **Critical** — Python always uses `tr_type="lead"` hardcoded in `insert_to_db_2()`. If the PHP endpoint receives `tr_type` with a different value, the Python implementation will INSERT incorrect data.

### 3.4 PHP prints JSON response directly; Python returns it via Flask

-   **What it does in PHP**: `start.php:87,145` — `print(json_encode($editit, JSON_PRETTY_PRINT));` directly outputs JSON to stdout.
-   **Where**: Multiple places in PHP
-   **Impact**: **Minor** — Python uses Flask's `jsonify()` which produces compact JSON (no `JSON_PRETTY_PRINT`). The response body format differs slightly.

### 3.5 `handleNoAccess` prints and exits; Python returns a dict

-   **What it does in PHP**: `start.php:75-88` — `handleNoAccess` prints JSON and calls `return` (implicit exit from `start()`), then `start.php:145` prints the result again. This means on no-access, PHP prints the no-access JSON **and does not print the normal result**.
-   **Where**: `start.php:107-111`
-   **Impact**: **Minor** — Python correctly returns a 403 response with the no-access dict. The behavior is functionally equivalent because Python's route handler returns the response immediately.

### 3.6 Load environment from file (`load_env.php`)

-   **What it does in PHP**: `load_env.php` explicitly sets environment variables with `putenv()`.
-   **Where**: `load_env.php`
-   **Impact**: **Not applicable** — Python uses `.env` file via `env_config.py` module. This is an architectural difference, not a bug.

---

## 4. ⚠️ What is implemented but incorrectly or partially

### 4.1 `determine_hashtag` logic differs

-   **PHP**: `strpos($title, "Mr. Ibrahem") !== false && $user == "Mr. Ibrahem"` — checks if `Mr. Ibrahem` appears **anywhere** in the title.
-   **Python**: `f"{exempt_user}/" in title or title == exempt_user` and `user == exempt_user` — checks if `Mr. Ibrahem/` is in the title (with trailing slash) OR title exactly equals `Mr. Ibrahem`.
-   **Exact difference**: PHP `"Mr. Ibrahem" in title` matches titles like `"Mr. Ibrahem"` (exact match) and `"Mr. Ibrahem/SomeArticle"`, but also `"SomeMr. IbrahemArticle"`. Python only matches `Mr. Ibrahem/` (with slash) or exact `Mr. Ibrahem`. This means `"Mr. Ibrahem SomePage"` would get a hashtag in Python but not in PHP.
-   **Impact**: **Minor** — In practice, titles containing `"Mr. Ibrahem"` without a `/` or being exactly `"Mr. Ibrahem"` are unlikely. But the logic is not identical.

### 4.2 `format_title` applies special user path replacements differently

-   **PHP**: Only replaces `"Mr. Ibrahem 1/"` with `"Mr. Ibrahem/"` (hardcoded).
-   **Python**: Iterates over `settings.users.special_users` and replaces `{alt_user}/` with `{canonical_user}/` for each mapping (configurable, includes `"Mr. Ibrahem 1/"` → `"Mr. Ibrahem/"` and also `Admin/` replacements).
-   **Exact difference**: Python applies **all** special user mappings to title paths, not just the one hardcoded replacement. This is more flexible but technically different.
-   **Impact**: **Minor** — More mappings are applied in Python, but the primary case (`Mr. Ibrahem 1/` → `Mr. Ibrahem/`) is handled identically.

### 4.3 CORS `is_allowed` returns domain string vs boolean-like values

-   **PHP**: Returns the matched domain string (e.g., `"mdwikicx.toolforge.org"`) or `false`. The endpoint uses `if (!$is_allowed)` for validation.
-   **Python**: Returns the matched domain string or `None`. When CORS is disabled, returns `origin or 1` (truthy value including integer `1`).
-   **Exact difference**: When CORS is disabled in Python, `is_allowed()` returns `origin` or `1`, which would make the `Access-Control-Allow-Origin` header be set to `1` or the raw Origin header value, not a validated domain. PHP has no such "CORS disabled" bypass.
-   **Impact**: **Minor** — Only active when `CORS_DISABLED` config is set, which is presumably development-only.

### 4.4 `to_do` file structure differs

-   **PHP**: Creates `{PUBLISH_REPORTS_PATH}/reports_by_day/{YYYY}/{MM}/{DD}/{rand_id}/{file_name}.json` and writes `tab` JSON with `JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE`. The `tab` dict includes `time` (Unix timestamp from `time()`) and `time_date` (formatted with `date()`).
-   **Python**: Creates a similar directory structure plus writes to a daily JSON-lines log file. The `tab` dict includes `time`, `time_date`, **and** `status` (extra field not in PHP). Also, the `rand_id` is generated once per process rather than per request.
-   **Exact difference**: (1) Python adds a `status` field to the `to_do` JSON that PHP doesn't. (2) `rand_id` is per-process not per-request. (3) Python writes a secondary JSON-lines log that PHP does not.
-   **Impact**: **Minor** — Extra `status` field and dual logging don't break anything but produce slightly different output files.

### 4.5 `_handle_no_access` logs to reports but also passes `tab` to `to_do`; PHP prints JSON directly

-   **PHP**: `handleNoAccess` calls `to_do($tab, "noaccess", $rand_id)` then `InsertPublishReports(...)`, then `print(json_encode($editit))`.
-   **Python**: `_handle_no_access` calls `to_do(tab, "noaccess")` then `reports_db.add(...)`, then **returns** `editit`. The route handler then sets `response.status_code = 403` and adds CORS headers.
-   **Exact difference**: Functionally equivalent logging, but Python returns the editit dict and lets the route handler set the HTTP status code, while PHP directly prints JSON output with implicit 200 status (no explicit `http_response_code` for no-access case).
-   **Impact**: **Minor** — Python correctly returns 403 for no-access; PHP would return 200 with an error body. Python is arguably more correct here.

### 4.6 `Wikidata` fallback user retrieval differs

-   **PHP**: `retryWithFallbackUser()` in `wd.php:83` calls `get_user_access('Mr. Ibrahem')` to get fresh credentials from the database.
-   **Python**: `_retry_with_fallback_user()` in `worker.py:116` calls `get_user_token_by_username(fallback_user)` which looks up from the `access_keys` table.
-   **Exact difference**: PHP's `get_user_access` tries `keys_new` table first, then falls back to `access_keys` table. Python's `get_user_token_by_username` only queries the `access_keys` table by username. The `keys_new` table lookup (with decryption of `u_n` column) is not implemented.
-   **Impact**: **Minor** — If the `keys_new` table is the primary key store, this could cause fallback failures. But in practice the `access_keys` table is likely the active one.

### 4.7 `get_revid_db` API URL construction differs

-   **PHP**: `start.php:24-28` — Uses `http://localhost:9001/api?get=revids&title=...` in dev, `https://mdwiki.toolforge.org/api.php?get=revids&title=...` in prod, using `http_build_query()` with `PHP_QUERY_RFC3986`.
-   **Python**: `revids_service.py` — Uses `settings.revids_api_url` (default `https://mdwiki.toolforge.org/api.php`) with `requests.get()` and `params` dict, which uses URL-encoded `+` for spaces.
-   **Exact difference**: PHP uses `?get=revids&title=` with RFC 3986 encoding (spaces as `%20`). Python's `requests` library defaults to URL encoding (spaces as `+`). Also, PHP appends query string to the base URL directly; Python uses the params dict which may encode differently.
-   **Impact**: **Minor** — The API likely accepts both encoding styles, but edge cases with special characters could differ.

### 4.8 `InsertPageTarget` INSERT statement differs

-   **PHP**: `add_to_db.php:36-39` — `INSERT INTO $table_name (title, word, translate_type, cat, lang, user, pupdate, target, mdwiki_revid) SELECT ?, ?, ?, ?, ?, ?, DATE(NOW()), ?, ?` — uses `SELECT` clause for values, applies `DATE(NOW())` server-side.
-   **Python**: `db_pages.py` `insert_page_target()` — Likely uses a standard INSERT with parameterized values, applying the date from Python rather than `DATE(NOW())`.
-   **Exact difference**: PHP uses `INSERT ... SELECT` with `DATE(NOW())` for the `pupdate` column. Python likely sends the date as a parameter.
-   **Impact**: **Minor** — The `pupdate` value may differ by timezone (PHP uses MySQL's `NOW()`, Python uses Python's datetime).

### 4.9 `_get_errors_file` comparison logic differs

-   **PHP**: `get_errors_file` uses `strpos($c_text, $err) !== false` for string containment check, which is case-sensitive.
-   **Python**: `_get_errors_file` uses `if err in c_text` for the main errors list, and `if err in c_text` for dictionary keys.
-   **Exact difference**: Functionally identical — both are case-sensitive substring checks.
-   **Impact**: **None** — Behavior is equivalent.

### 4.10 Wikidata `WIKIDATA_DOMAIN` hardcoded vs configurable

-   **PHP**: `wd.php:31` — `$wikidata_domain = getenv('WIKIDATA_DOMAIN') ?: 'www.wikidata.org'` — configurable via environment.
-   **Python**: `wikidata_client.py:_link_it` — Hardcodes `https://www.wikidata.org`.
-   **Exact difference**: Python does not read `WIKIDATA_DOMAIN` from environment; it always uses `www.wikidata.org`.
-   **Impact**: **Critical** — already fixed

### 4.11 `link_to_wikidata` credential fallback differs from `getAccessCredentials`

-   **PHP**: `wd.php:getAccessCredentials()` — If `access_key` and `access_secret` are both provided, uses them directly. Otherwise, falls back to `get_user_access($user)` to fetch from DB.
-   **Python**: `wikidata_client.py:link_to_wikidata()` — If either `access_key` or `access_secret` is empty, immediately returns an error without attempting DB fallback.
-   **Exact difference**: PHP has a fallback path where if credentials are missing, it fetches fresh ones from the database. Python returns an error immediately.
-   **Impact**: **Critical** — If credentials are somehow empty/invalid for a user who exists in the DB, PHP would recover and proceed, while Python would fail with an error.

---

## 5. 🔧 Required actions

Ordered by priority (critical first):

1. **Add `tr_type` parameter from request**: Read `tr_type` from `request_data` in `routes.py:70` and pass it through `_process_edit` → `_add_to_db` → `insert_to_db_2` instead of hardcoding `"lead"`. In `routes.py`, add `tr_type = request_data.get("tr_type", "lead")` and thread it through `_process_edit(tab, tr_type)`.

2. **Implement credential fallback in `link_to_wikidata`**: In `wikidata_client.py:link_to_wikidata()`, when `access_key` or `access_secret` is empty, attempt to fetch credentials from the database via `get_user_token_by_username(user)` before returning an error, matching PHP's `getAccessCredentials` behavior.

3. **Fix `determine_hashtag` to match PHP's `strpos` behavior**: Change the condition from `f"{exempt_user}/" in title or title == exempt_user` to `exempt_user in title` (matching PHP's `strpos($title, "Mr. Ibrahem") !== false`).

4. **Add `words` field to `tab` dict**: In `worker.py:_process_edit`, add `tab["words"] = get_word_count(sourcetitle)` after processing, matching PHP's `$tab['words'] = $Words_table[$title] ?? 0`.

5. **Make `rand_id` per-request instead of per-process**: Change `files.py` to generate a new `rand_id` for each request (e.g., using `uuid.uuid4().hex[:12]`) rather than caching `_RAND_ID` at module level. This matches PHP's `time() . "-" . bin2hex(random_bytes(6))`.

6. **Make `WIKIDATA_DOMAIN` configurable**: In `wikidata_client.py:_link_it`, read `WIKIDATA_DOMAIN` from environment/config instead of hardcoding `https://www.wikidata.org`.

7. **Remove extra `status` field from `to_do` output**: In `files.py:to_do()`, remove the `log_entry["status"] = status` line to match PHP's output format, or document this as an intentional enhancement.

8. **Match `http_response_code` for no-access in PHP**: PHP's `handleNoAccess` does NOT set a 403 HTTP status code — it prints JSON with a 200 status. The Python implementation correctly returns 403. Decide if Python's behavior is the intended one and document the difference, or align with PHP by removing the 403 status code.

---

## 6. Code snippets

### 6.1 Add `tr_type` parameter (Critical — Item #1)

**PHP (`start.php:116`):**

```php
$tr_type = $request['tr_type'] ?? 'lead';
```

**Python fix (`routes.py`):**

```python
# In index() function, after request_data:
tr_type = request_data.get("tr_type", "lead")

# Pass to _process_edit:
editit = _process_edit(access_key, access_secret, text, tab, tr_type)
```

**Python fix (`worker.py:_process_edit`):**

```python
def _process_edit(
    access_key: str,
    access_secret: str,
    text: str,
    tab: dict[str, Any],
    tr_type: str = "lead",
) -> dict[str, Any]:
    # ... existing code ...
    sql_result = _add_to_db(
        title,
        lang,
        user,
        link_to_wd,
        campaign,
        sourcetitle,
        mdwiki_revid,
        tr_type=tr_type,
    )
```

**Python fix (`worker.py:_add_to_db`):**

```python
def _add_to_db(
    target, lang, user, wd_result, campaign, sourcetitle, mdwiki_revid, tr_type="lead",
):
    # ... existing code ...
    return insert_to_db(target, lang, user, sourcetitle, mdwiki_revid, cat, word, to_users_table, tr_type=tr_type)
```

---

### 6.2 Implement credential fallback (Critical — Item #2)

**PHP (`wd.php:9-27`):**

```php
function getAccessCredentials($user, $access_key, $access_secret)
{
    if ($access_key && $access_secret) {
        return [$access_key, $access_secret];
    }
    $access = get_user_access($user);
    if (empty($access)) {
        error_log("user = $user");
        error_log("access == null");
        return null;
    }
    $access_key = $access['access_key'];
    $access_secret = $access['access_secret'];
    return [$access_key, $access_secret];
}
```

**Python fix (`wikidata_client.py`):**

```python
def link_to_wikidata(sourcetitle, lang, user, targettitle, access_key, access_secret):
    qid = get_qid_for_mdtitle(sourcetitle) or ""

    if not access_key or not access_secret:
        from ..users.store import get_user_token_by_username
        token = get_user_token_by_username(user)
        if token is not None:
            access_key, access_secret = token.decrypted()
        else:
            return {"error": f"Access credentials not found for user: {user}", "qid": qid}

    link_result = _link_it(qid, lang, sourcetitle, targettitle, access_key, access_secret)
    link_result["qid"] = qid
    if link_result.get("success"):
        logger.debug("Wikidata link success")
        return {"result": "success", "qid": qid}
    return link_result
```

---

### 6.3 Fix `determine_hashtag` (Minor — Item #3)

**PHP (`start_utils.php:28-36`):**

```php
function determineHashtag($title, $user)
{
    $hashtag = "#mdwikicx";
    if (strpos($title, "Mr. Ibrahem") !== false && $user == "Mr. Ibrahem") {
        $hashtag = "";
    }
    return $hashtag;
}
```

**Python fix (`helpers/format.py`):**

```python
def determine_hashtag(title: str, user: str) -> str:
    hashtag = "#mdwikicx"
    for exempt_user in settings.users.users_without_hashtag:
        if exempt_user in title and user == exempt_user:
            hashtag = ""
            break
    return hashtag
```

---

### 6.4 Add `words` field to `tab` (Minor — Item #4)

**PHP (`start.php:113-114`):**

```php
$Words_table = load_words_table();
$tab['words'] = $Words_table[$title] ?? 0;
```

**Python fix (`worker.py:_process_edit`):**

```python
def _process_edit(access_key, access_secret, text, tab, tr_type="lead"):
    # ... after getting mdwiki_revid ...
    tab["words"] = get_word_count(tab["sourcetitle"])
    # ... rest of function
```

---

### 6.5 Per-request `rand_id` (Minor — Item #5)

**PHP (`start.php:92`):**

```php
$rand_id = time() .  "-" . bin2hex(random_bytes(6));
```

**Python fix (`helpers/files.py`):**

```python
import time
import secrets

def to_do(tab: dict[str, Any], status: str) -> None:
    rand_id = f"{int(time.time())}-{secrets.token_hex(6)}"
    # ... use rand_id for directory creation instead of _RAND_ID
```

---

### 6.6 Configurable `WIKIDATA_DOMAIN` (Minor — Item #6)

**PHP (`wd.php:31`):**

```php
$wikidata_domain = getenv('WIKIDATA_DOMAIN') ?: 'www.wikidata.org';
$https_domain = "https://$wikidata_domain";
```

**Python fix (`wikidata_client.py:_link_it`):**

```python
import os

def _link_it(qid, lang, sourcetitle, targettitle, access_key, access_secret):
    wikidata_domain = os.getenv("WIKIDATA_DOMAIN", "www.wikidata.org")
    https_domain = f"https://{wikidata_domain}"
    # ... rest of function
```

---

### 6.7 Remove extra `status` field (Minor — Item #7)

**PHP (`files_helps.php:6-16`):** No `status` field added to `$tab`.

**Python fix (`helpers/files.py:to_do`):** Remove the line:

```python
log_entry["status"] = status  # Remove this — PHP does not add this field
```

---

### 6.8 HTTP status code for no-access (Design decision — Item #8)

**PHP (`start.php:75-88`):** No explicit `http_response_code(403)` — returns 200 with error JSON.

**Python (`routes.py:93-97`):** Returns 403 with error JSON.

This is arguably a **better** implementation in Python. If you want to match PHP exactly:

```python
# Change from:
response = jsonify(_handle_no_access(tab))
response.status_code = 403
# To:
response = jsonify(_handle_no_access(tab))
# (No explicit 403 status code)
```

However, **keeping 403 is recommended** as it's more semantically correct for an access-denied response.
