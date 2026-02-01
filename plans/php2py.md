# PHP to Python Integration Plan

This plan outlines the migration of PHP endpoints to Python Flask routes, focusing on:
- **cxtoken.routes** mirroring [php_src/endpoints/cxtoken.php](../php_src/endpoints/cxtoken.php)
- **post.routes** mirroring [php_src/endpoints/post.php](../php_src/endpoints/post.php)

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [PHP to Python Module Mapping](#php-to-python-module-mapping)
3. [cxtoken.routes Integration](#cxtokenroutes-integration)
4. [post.routes Integration](#postroutes-integration)
5. [Database Layer Updates](#database-layer-updates)
6. [Helper Services](#helper-services)
7. [Testing Strategy](#testing-strategy)
8. [Implementation Order](#implementation-order)

---

## Architecture Overview

### Current PHP Structure
```
php_src/
├── endpoints/
│   ├── cxtoken.php         # Token endpoint
│   └── post.php            # Post/Publish endpoint
├── bots/
│   ├── api/
│   │   ├── get_token.php   # OAuth token retrieval
│   │   ├── process_edit.php # Edit processing
│   │   └── do_edit.php     # MediaWiki edit API
│   ├── cors.php            # CORS validation
│   ├── sql/
│   │   ├── access_helps.php # Access key management
│   │   ├── db_Pages.php     # Pages table operations
│   │   └── db_publish_reports.php # Reports table
│   ├── files_helps.php     # File logging
│   ├── helps.php           # Encryption helpers
│   ├── revids_bot.php      # Revision ID lookup
│   ├── wd.php              # Wikidata integration
│   └── services/
│       └── http.php        # HTTP utilities
└── text_change.php         # Text processing
```

### Target Python Structure
```
src/app/
├── app_routes/
│   ├── cxtoken/
│   │   └── routes.py       # Token endpoint ✅ IMPLEMENTED
│   └── post/
│       └── routes.py       # Post endpoint ✅ IMPLEMENTED
├── services/
│   ├── __init__.py         # ✅ CREATED
│   ├── oauth_client.py     # ✅ CREATED: OAuth client wrapper
│   ├── mediawiki_api.py    # ✅ CREATED: MediaWiki API client
│   ├── wikidata_client.py  # ✅ CREATED: Wikidata integration
│   ├── revids_service.py   # ✅ CREATED: Revision ID lookup
│   └── text_processor.py   # ✅ CREATED: Text processing
├── helpers/
│   ├── __init__.py         # ✅ CREATED
│   ├── cors.py             # ✅ CREATED: CORS validation
│   ├── files.py            # ✅ CREATED: File logging utilities
│   └── format.py           # ✅ CREATED: Title/user formatting
└── crypto.py               # Already exists (encryption)
```

---

## PHP to Python Module Mapping

| PHP File/Function | Python Module/Function | Status |
|-------------------|------------------------|--------|
| `Publish\CORS\is_allowed()` | `helpers/cors.py:is_allowed()` | ✅ DONE |
| `Publish\GetToken\get_csrftoken()` | `services/oauth_client.py:get_csrf_token()` | ✅ DONE |
| `Publish\GetToken\post_params()` | `services/oauth_client.py:post_params()` | ✅ DONE |
| `Publish\GetToken\get_cxtoken()` | `services/oauth_client.py:get_cxtoken()` | ✅ DONE |
| `Publish\AccessHelps\get_access_from_db()` | `users/store.py:get_user_token_by_username()` | ✅ DONE |
| `Publish\AccessHelps\del_access_from_db()` | `users/store.py:delete_user_token_by_username()` | ✅ DONE |
| `Publish\FilesHelps\to_do()` | `helpers/files.py:to_do()` | ✅ DONE |
| `Publish\Revids\get_revid()` | `services/revids_service.py:get_revid()` | ✅ DONE |
| `Publish\Revids\get_revid_db()` | `services/revids_service.py:get_revid_db()` | ✅ DONE |
| `Publish\DoEdit\publish_do_edit()` | `services/mediawiki_api.py:publish_do_edit()` | ✅ DONE |
| `Publish\EditProcess\processEdit()` | `app_routes/post/routes.py:_process_edit()` | ✅ DONE |
| `Publish\WD\LinkToWikidata()` | `services/wikidata_client.py:link_to_wikidata()` | ✅ DONE |
| `Publish\AddToDb\InsertPublishReports()` | `db/db_publish_reports.py:ReportsDB.add()` | ✅ DONE |
| `Publish\AddToDb\InsertPageTarget()` | `db/db_Pages.py:PagesDB.insert_page_target()` | ✅ DONE |

---

## cxtoken.routes Integration

### PHP Endpoint Analysis

**File:** [php_src/endpoints/cxtoken.php](../php_src/endpoints/cxtoken.php)

**Request:**
```
GET /cxtoken.php?wiki={wiki}&user={username}
```

**Response:**
```json
{
  "csrftoken_data": {
    "query": {
      "tokens": {
        "csrftoken": "+\\"
      }
    }
  }
}
```

**Key Functions:**
1. CORS validation (`is_allowed()`)
2. User formatting (special users mapping)
3. Access key retrieval from database
4. CSRF token retrieval via OAuth
5. Error handling for invalid authorization

### Python Implementation Plan

#### 1. Create [src/app/helpers/cors.py](../src/app_main/helpers/cors.py)

```python
"""CORS validation helpers."""

from flask import request

ALLOWED_DOMAINS = ['medwiki.toolforge.org', 'mdwikicx.toolforge.org']

def is_allowed() -> str | None:
    """Check if request is from allowed domain.

    Returns the allowed domain name or None.
    """
    referer = request.headers.get('Referer', '')
    origin = request.headers.get('Origin', '')

    for domain in ALLOWED_DOMAINS:
        if domain in referer or domain in origin:
            return domain
    return None
```

#### 2. Create [src/app/services/oauth_client.py](../src/app_main/services/oauth_client.py)

```python
"""MediaWiki OAuth client wrapper."""

import logging
import requests
from requests_oauthlib import OAuth1

from ..config import settings

logger = logging.getLogger(__name__)

def get_oauth_client(access_key: str, access_secret: str, domain: str = "en.wikipedia.org"):
    """Create OAuth1 session for MediaWiki API."""
    oauth_url = f"https://{domain}/w/index.php?title=Special:OAuth"
    return OAuth1(
        settings.oauth.consumer_key,
        client_secret=settings.oauth.consumer_secret,
        resource_owner_key=access_key,
        resource_owner_secret=access_secret,
    )

def get_csrf_token(access_key: str, access_secret: str, lang: str = "en") -> dict:
    """Get CSRF token from MediaWiki API."""
    api_url = f"https://{lang}.wikipedia.org/w/api.php"
    params = {
        "action": "query",
        "meta": "tokens",
        "format": "json"
    }

    client = get_oauth_client(access_key, access_secret, f"{lang}.wikipedia.org")
    response = requests.get(api_url, params=params, auth=client)
    return response.json()

def post_params(api_params: dict, https_domain: str, access_key: str, access_secret: str) -> str:
    """Make OAuth POST request to MediaWiki API."""
    api_url = f"{https_domain}/w/api.php"

    # First get CSRF token
    lang = https_domain.split(".")[2].replace("wikipedia", "")  # Extract lang from domain
    csrf_data = get_csrf_token(access_key, access_secret, lang)

    if "error" in csrf_data:
        logger.error(f"CSRF token error: {csrf_data}")
        return '{"error": "get_csrf_token failed"}'

    csrf_token = csrf_data["query"]["tokens"]["csrftoken"]
    api_params["token"] = csrf_token
    api_params["format"] = "json"

    client = get_oauth_client(access_key, access_secret, https_domain.replace("https://", ""))
    response = requests.post(api_url, data=api_params, auth=client)
    return response.text

def get_cxtoken(wiki: str, access_key: str, access_secret: str) -> dict:
    """Get CX token for Content Translation.

    Args:
        wiki: Wiki domain (e.g., 'en')
        access_key: OAuth access key
        access_secret: OAuth access secret

    Returns:
        API response as dictionary
    """
    https_domain = f"https://www.wikidata.org"
    api_params = {
        "action": "cxtoken",
        "format": "json",
    }

    response = post_params(api_params, https_domain, access_key, access_secret)
    result = json.loads(response)

    if result is None or "error" in result:
        logger.error(f"get_cxtoken error: {result}")

    return result or {}
```

#### 3. Update [src/app/app_routes/cxtoken/routes.py](../src/app_main/app_routes/cxtoken/routes.py)

```python
"""Content Translation token endpoint."""

import json
import logging

from flask import Blueprint, jsonify, request

from ...users.store import get_user_token, delete_user_token
from ...users.current import current_user
from ..helpers.cors import is_allowed
from ..services.oauth_client import get_cxtoken

bp_cxtoken = Blueprint("cxtoken", __name__)
logger = logging.getLogger(__name__)

SPECIAL_USERS = {
    "Mr. Ibrahem 1": "Mr. Ibrahem",
    "Admin": "Mr. Ibrahem"
}

def format_user(user: str) -> str:
    """Format username, applying special user mappings."""
    user = SPECIAL_USERS.get(user, user)
    return user.replace("_", " ")

@bp_cxtoken.route("/", methods=["GET", "OPTIONS"])
def index():
    """Handle cxtoken requests."""
    # Handle CORS preflight
    if request.method == "OPTIONS":
        allowed = is_allowed()
        if not allowed:
            return jsonify({"error": "CORS not allowed"}), 403
        return "", 200

    # Check CORS
    allowed = is_allowed()
    if not allowed:
        return jsonify({"error": "Access denied. Requests are only allowed from authorized domains."}), 403

    # Get request parameters
    wiki = request.args.get("wiki", "")
    user = request.args.get("user", "")

    # Validate parameters
    if not wiki or not user:
        return jsonify({"error": {"code": "no data", "info": "wiki or user is empty"}}), 400

    # Format user
    user = format_user(user)

    # Get access credentials from database
    # Note: PHP uses username lookup, Python uses user_id - need to adapt
    # This requires adding a username lookup to the store
    user_token = get_user_token_by_username(user)

    if user_token is None:
        error_response = {
            "error": {"code": "no access", "info": "no access"},
            "username": user
        }
        return jsonify(error_response), 403

    access_key, access_secret = user_token.decrypted()

    # Get cxtoken
    cxtoken = get_cxtoken(wiki, access_key, access_secret)

    # Handle invalid authorization
    err = cxtoken.get("csrftoken_data", {}).get("error", {}).get("code")
    if err == "mwoauth-invalid-authorization-invalid-user":
        delete_user_token(user_token.user_id)
        cxtoken["del_access"] = True

    response = jsonify(cxtoken)
    if allowed:
        response.headers["Access-Control-Allow-Origin"] = f"https://{allowed}"
    return response

__all__ = ["bp_cxtoken"]
```

---

## post.routes Integration

### PHP Endpoint Analysis

**File:** [php_src/endpoints/post.php](../php_src/endpoints/post.php)

**Request:**
```
POST /post.php
{
  "user": "username",
  "title": "Target page title",
  "target": "language code",
  "sourcetitle": "Source page title",
  "text": "page content",
  "revid": "revision ID",
  "campaign": "campaign name",
  "wpCaptchaId": "captcha ID (optional)",
  "wpCaptchaWord": "captcha word (optional)"
}
```

**Response:**
```json
{
  "edit": {
    "result": "Success",
    "pageid": 12345,
    "title": "Page title",
    "contentmodel": "wikitext",
    "oldrevid": 67890,
    "newrevid": 78901,
    "newtimestamp": "2024-01-01T00:00:00Z"
  },
  "LinkToWikidata": {
    "result": "success",
    "qid": "Q123"
  },
  "sql_result": {...}
}
```

**Processing Flow:**
1. Format title and user
2. Check access from database
3. Get revision ID
4. Generate edit summary
5. Apply text changes (fix references)
6. Process edit via MediaWiki API
7. Link to Wikidata on success
8. Insert to database (pages/publish_reports)
9. Log to file

### Python Implementation Plan

#### 1. Create [src/app/helpers/format.py](../src/app_main/helpers/format.py)

```python
"""Title and user formatting utilities."""

SPECIAL_USERS = {
    "Mr. Ibrahem 1": "Mr. Ibrahem",
    "Admin": "Mr. Ibrahem"
}

def format_title(title: str) -> str:
    """Format page title."""
    title = title.replace("_", " ")
    title = title.replace("Mr. Ibrahem 1/", "Mr. Ibrahem/")
    return title

def format_user(user: str) -> str:
    """Format username, applying special user mappings."""
    user = SPECIAL_USERS.get(user, user)
    return user.replace("_", " ")

def determine_hashtag(title: str, user: str) -> str:
    """Determine appropriate hashtag based on title and user."""
    hashtag = "#mdwikicx"
    if "Mr. Ibrahem" in title and user == "Mr. Ibrahem":
        hashtag = ""
    return hashtag

def make_summary(revid: str, sourcetitle: str, target_lang: str, hashtag: str = "#mdwikicx") -> str:
    """Generate edit summary for translation."""
    return f"Created by translating the page [[:mdwiki:Special:Redirect/revision/{revid}|{sourcetitle}]] to:{target_lang} {hashtag}"
```

#### 2. Create [src/app/services/mediawiki_api.py](../src/app_main/services/mediawiki_api.py)

```python
"""MediaWiki API client for edit operations."""

import json
import logging

from .oauth_client import post_params

logger = logging.getLogger(__name__)

def publish_do_edit(api_params: dict, wiki: str, access_key: str, access_secret: str) -> dict:
    """Publish an edit to MediaWiki.

    Args:
        api_params: API parameters for the edit
        wiki: Wiki language code
        access_key: OAuth access key
        access_secret: OAuth access secret

    Returns:
        Edit result as dictionary
    """
    https_domain = f"https://{wiki}.wikipedia.org"
    response = post_params(api_params, https_domain, access_key, access_secret)
    result = json.loads(response) if response else {}
    return result
```

#### 3. Create [src/app/services/revids_service.py](../src/app_main/services/revids_service.py)

```python
"""Revision ID lookup service."""

import json
import logging
import os
from pathlib import Path
from typing import Any

import requests

logger = logging.getLogger(__name__)

def get_revid(sourcetitle: str) -> str:
    """Get revision ID from local JSON file."""
    revids_file = Path(__file__).parent.parent.parent / "bots" / "all_pages_revids.json"
    if not revids_file.exists():
        revids_file = Path(__file__).parent.parent.parent.parent / "php_src" / "bots" / "all_pages_revids.json"

    try:
        with open(revids_file) as f:
            revids = json.load(f)
        return revids.get(sourcetitle, "")
    except Exception as e:
        logger.error(f"Error reading revids file: {e}")
        return ""

def get_revid_db(sourcetitle: str) -> str:
    """Get revision ID from database API."""
    params = {
        "get": "revids",
        "title": sourcetitle
    }

    # Determine if localhost
    is_local = os.getenv("FLASK_ENV") == "development"

    if is_local:
        url = f"http://localhost:9001/api"
    else:
        url = "https://mdwiki.toolforge.org/api.php"

    try:
        response = requests.get(url, params=params)
        data = response.json()
        results = {r["title"]: r["revid"] for r in data.get("results", [])}
        return results.get(sourcetitle, "")
    except Exception as e:
        logger.error(f"Error fetching revid from API: {e}")
        return ""
```

#### 4. Create [src/app/services/wikidata_client.py](../src/app_main/services/wikidata_client.py)

```python
"""Wikidata integration service."""

import json
import logging

from ..db import get_db
from .oauth_client import post_params

logger = logging.getLogger(__name__)

def get_qid_for_mdtitle(title: str) -> list[dict]:
    """Get QID for mdwiki title from database."""
    db = get_db()
    rows = db.fetch_query_safe(
        "SELECT qid FROM qids WHERE title = %s",
        (title,)
    )
    return rows

def get_title_info(targettitle: str, lang: str) -> dict | None:
    """Get title info from MediaWiki API."""
    import requests

    params = {
        "action": "query",
        "format": "json",
        "titles": targettitle,
        "utf8": 1,
        "formatversion": "2"
    }
    url = f"https://{lang}.wikipedia.org/w/api.php"

    try:
        response = requests.get(url, params=params)
        data = response.json()
        return data.get("query", {}).get("pages", [{}])[0]
    except Exception as e:
        logger.error(f"GetTitleInfo error: {e}")
        return None

def link_to_wikidata(sourcetitle: str, lang: str, user: str, targettitle: str,
                     access_key: str, access_secret: str) -> dict:
    """Link translated page to Wikidata item.

    Args:
        sourcetitle: Source page title
        lang: Target language code
        user: Username
        targettitle: Target page title
        access_key: OAuth access key
        access_secret: OAuth access secret

    Returns:
        Result dictionary with QID and status
    """
    # Get QID for source
    qids = get_qid_for_mdtitle(sourcetitle)
    qid = qids[0]["qid"] if qids else ""

    if not access_key or not access_secret:
        return {"error": f"Access credentials not found for user: {user}", "qid": qid}

    # Link to Wikidata
    https_domain = "https://www.wikidata.org"
    api_params = {
        "action": "wbsetsitelink",
        "linktitle": targettitle,
        "linksite": f"{lang}wiki",
    }

    if qid:
        api_params["id"] = qid
    else:
        api_params["title"] = sourcetitle
        api_params["site"] = "enwiki"

    response = post_params(api_params, https_domain, access_key, access_secret)
    result = json.loads(response) if response else {}
    result["qid"] = qid

    if result.get("success"):
        return {"result": "success", "qid": qid}

    return result
```

#### 5. Create [src/app/helpers/files.py](../src/app_main/helpers/files.py)

```python
"""File logging utilities."""

import json
import logging
import os
import secrets
from datetime import datetime
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

# Generate a unique ID for this run
RAND_ID = f"{int(datetime.now().timestamp())}-{secrets.token_hex(6)}"

def get_reports_dir() -> Path:
    """Get/create the reports directory structure."""
    # Determine base directory
    main_dir = os.getenv("MAIN_DIR", os.path.expanduser("~/data"))
    publish_reports = Path(main_dir) / "publish_reports" / "reports_by_day"

    # Create directory structure: YYYY/MM/DD/rand_id
    now = datetime.now()
    day_dir = publish_reports / str(now.year) / f"{now.month:02d}" / f"{now.day:02d}" / RAND_ID
    day_dir.mkdir(parents=True, exist_ok=True)

    return day_dir

def to_do(tab: dict[str, Any], file_name: str) -> None:
    """Write data to a JSON file in the reports directory.

    Args:
        tab: Dictionary of data to write
        file_name: Name of the file (without extension)
    """
    reports_dir = get_reports_dir()

    tab["time"] = int(datetime.now().timestamp())
    tab["time_date"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    file_path = reports_dir / f"{file_name}.json"

    try:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(tab, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"Error writing to file {file_path}: {e}")
```

#### 6. Create [src/app/services/text_processor.py](../src/app_main/services/text_processor.py)

```python
"""Text processing utilities for page content."""

def do_changes_to_text(sourcetitle: str, title: str, text: str, lang: str, mdwiki_revid: str) -> str:
    """Apply changes to page text (placeholder for future logic).

    This function is a placeholder for text processing logic that will:
    - Fix references
    - Update links
    - Apply language-specific transformations

    Args:
        sourcetitle: Source page title
        title: Target page title
        text: Page content
        lang: Target language code
        mdwiki_revid: MediaWiki revision ID

    Returns:
        Processed text
    """
    # Placeholder: currently returns text unchanged
    # Future implementation will add reference fixing, link updates, etc.
    return text
```

#### 7. Update [src/app/app_routes/post/routes.py](../src/app_main/app_routes/post/routes.py)

```python
"""Post/Publish endpoint for Content Translation."""

import logging

from flask import Blueprint, jsonify, request

from ...users.store import get_user_token, get_user_token_by_username
from ...users.current import current_user
from ...db.db_publish_reports import ReportsDB
from ...db.db_Pages import PagesDB
from ..helpers.format import format_title, format_user, determine_hashtag, make_summary
from ..helpers.files import to_do
from ..services.oauth_client import post_params
from ..services.mediawiki_api import publish_do_edit
from ..services.revids_service import get_revid, get_revid_db
from ..services.wikidata_client import link_to_wikidata
from ..services.text_processor import do_changes_to_text
from ...config import settings

bp_post = Blueprint("post", __name__)
logger = logging.getLogger(__name__)

def handle_no_access(user: str, tab: dict) -> tuple[dict, int]:
    """Handle case when user has no access credentials.

    Returns error response and logs to database.
    """
    error = {"code": "noaccess", "info": "noaccess"}
    editit = {
        "error": error,
        "edit": {"error": error, "username": user},
        "username": user
    }
    tab["result_to_cx"] = editit

    # Log to file
    to_do(tab, "noaccess")

    # Insert to database
    db = settings.database_data
    reports_db = ReportsDB(db)
    reports_db.add(
        title=tab["title"],
        user=user,
        lang=tab["lang"],
        sourcetitle=tab["sourcetitle"],
        result="noaccess",
        data=json.dumps(tab)
    )

    return jsonify(editit), 403

def prepare_api_params(title: str, summary: str, text: str, request_data: dict) -> dict:
    """Prepare API parameters for MediaWiki edit."""
    api_params = {
        "action": "edit",
        "title": title,
        "summary": summary,
        "text": text,
        "format": "json",
    }

    # Add captcha parameters if present
    if "wpCaptchaId" in request_data and "wpCaptchaWord" in request_data:
        api_params["wpCaptchaId"] = request_data["wpCaptchaId"]
        api_params["wpCaptchaWord"] = request_data["wpCaptchaWord"]

    return api_params

def get_error_filename(editit: dict) -> str:
    """Determine error filename based on error type."""
    errors_main = [
        "protectedpage",
        "titleblacklist",
        "ratelimited",
        "editconflict",
        "spam filter",
        "abusefilter",
        "mwoauth-invalid-authorization",
    ]

    editit_str = json.dumps(editit)
    for err in errors_main:
        if err in editit_str:
            return err

    return "errors"

def add_to_db(title: str, lang: str, user: str, wd_result: dict,
              campaign: str, sourcetitle: str, mdwiki_revid: str) -> dict:
    """Add page target to database."""
    db = settings.database_data
    pages_db = PagesDB(db)

    # Determine if user table should be used
    to_users_table = False
    if "abusefilter-warning-39" in json.dumps(wd_result):
        to_users_table = True

    # Insert page target
    # Note: Need to implement insert_page_target method in PagesDB
    result = pages_db.insert_page_target(
        title=sourcetitle,
        translate_type="lead",
        cat="",  # Would need campaign categories lookup
        lang=lang,
        user=user,
        target=title,
        to_users_table=to_users_table,
        mdwiki_revid=mdwiki_revid
    )

    return result

def process_edit(request_data: dict, access_key: str, access_secret: str,
                 text: str, user: str, tab: dict) -> dict:
    """Process the edit request.

    Args:
        request_data: Original request data
        access_key: OAuth access key
        access_secret: OAuth access secret
        text: Page content to publish
        user: Username
        tab: Context dictionary

    Returns:
        Edit result dictionary
    """
    sourcetitle = tab["sourcetitle"]
    lang = tab["lang"]
    campaign = tab.get("campaign", "")
    title = tab["title"]
    summary = tab["summary"]
    mdwiki_revid = tab.get("revid", "")

    # Prepare API parameters
    api_params = prepare_api_params(title, summary, text, request_data)

    # Publish edit
    editit = publish_do_edit(api_params, lang, access_key, access_secret)

    # Check result
    success = editit.get("edit", {}).get("result", "")
    is_captcha = editit.get("edit", {}).get("captcha")

    tab["result"] = success

    to_do_file = ""

    if success == "Success":
        # Link to Wikidata
        editit["LinkToWikidata"] = link_to_wikidata(
            sourcetitle, lang, user, title, access_key, access_secret
        )

        # Add to database
        editit["sql_result"] = add_to_db(
            title, lang, user, editit["LinkToWikidata"], campaign, sourcetitle, mdwiki_revid
        )

        to_do_file = "success"

    elif is_captcha:
        to_do_file = "captcha"
    else:
        to_do_file = get_error_filename(editit)

    tab["result_to_cx"] = editit

    # Log to file
    to_do(tab, to_do_file)

    # Insert to database
    db = settings.database_data
    reports_db = ReportsDB(db)
    reports_db.add(
        title=title,
        user=user,
        lang=lang,
        sourcetitle=sourcetitle,
        result=to_do_file,
        data=json.dumps(tab)
    )

    return editit

@bp_post.route("/", methods=["POST"])
def index():
    """Handle post/publish requests."""
    request_data = request.get_json() or {}

    # Format user and title
    user = format_user(request_data.get("user", ""))
    title = format_title(request_data.get("title", ""))

    # Build context
    tab = {
        "title": title,
        "summary": "",
        "lang": request_data.get("target", ""),
        "user": user,
        "campaign": request_data.get("campaign", ""),
        "result": "",
        "edit": {},
        "sourcetitle": request_data.get("sourcetitle", "")
    }

    # Get access credentials
    user_token = get_user_token_by_username(user)

    if user_token is None:
        return handle_no_access(user, tab)

    access_key, access_secret = user_token.decrypted()

    # Get text from request
    text = request_data.get("text", "")

    # Get revision ID
    revid = get_revid(tab["sourcetitle"])
    if not revid:
        revid = get_revid_db(tab["sourcetitle"])
    if not revid:
        tab["empty revid"] = "Can not get revid from all_pages_revids.json"
        revid = request_data.get("revid") or request_data.get("revision", "")

    tab["revid"] = revid

    # Determine hashtag and create summary
    hashtag = determine_hashtag(tab["title"], user)
    tab["summary"] = make_summary(revid, tab["sourcetitle"], tab["lang"], hashtag)

    # Apply text changes
    newtext = do_changes_to_text(
        tab["sourcetitle"], tab["title"], text, tab["lang"], revid
    )
    if newtext and newtext != text:
        tab["fix_refs"] = "yes"
        text = newtext
    else:
        tab["fix_refs"] = "no"

    # Process edit
    editit = process_edit(request_data, access_key, access_secret, text, user, tab)

    return jsonify(editit)

__all__ = ["bp_post"]
```

---

## Database Layer Updates

### 1. Extend [src/app/users/store.py](../src/app_main/users/store.py)

Add username lookup function:

```python
def get_user_token_by_username(username: str) -> Optional[UserTokenRecord]:
    """Fetch the encrypted OAuth credentials for a user by username."""
    db = get_db()
    rows: list[Dict[str, Any]] = db.fetch_query_safe(
        """
        SELECT
            user_id,
            username,
            access_token,
            access_secret,
            created_at,
            updated_at,
            last_used_at,
            rotated_at
        FROM user_tokens
        WHERE username = %s
        """,
        (username,),
    )
    if not rows:
        return None

    row = rows[0]
    return UserTokenRecord(
        user_id=row["user_id"],
        username=row["username"],
        access_token=_coerce_bytes(row["access_token"]),
        access_secret=_coerce_bytes(row["access_secret"]),
        created_at=row.get("created_at"),
        updated_at=row.get("updated_at"),
        last_used_at=row.get("last_used_at"),
        rotated_at=row.get("rotated_at"),
    )
```

### 2. access_keys table migration
The PHP code uses an `access_keys` table, while Python uses `user_tokens`.
- use `user_tokens` insted of `access_keys` Table

### 3. Extend [src/app/db/db_Pages.py](../src/app_main/db/db_Pages.py)

Add `insert_page_target` method:

```python
def insert_page_target(
    self,
    title: str,
    translate_type: str,
    cat: str,
    lang: str,
    user: str,
    target: str,
    to_users_table: bool = False,
    mdwiki_revid: int | None = None
) -> dict:
    """Insert or update a page target record.

    Args:
        title: Source page title
        translate_type: Type of translation
        cat: Category
        lang: Target language
        user: Username
        target: Target page title
        to_users_table: Whether to use pages_users table
        mdwiki_revid: MediaWiki revision ID

    Returns:
        Result dictionary with operation status
    """
    title = title.replace("_", " ")
    target = target.replace("_", " ")
    user = user.replace("_", " ")

    table_name = "pages_users" if to_users_table else "pages"

    # Check if exists
    existing = self.db.fetch_query_safe(
        f"SELECT * FROM {table_name} WHERE title = %s AND lang = %s AND user = %s",
        (title, lang, user)
    )

    if existing:
        # Update if target is empty
        if not existing[0].get("target"):
            self.db.execute_query_safe(
                f"UPDATE {table_name} SET target = %s, pupdate = CURDATE() WHERE id = %s",
                (target, existing[0]["id"])
            )
        return {"exists": "already_in", "use_user_sql": to_users_table}

    # Insert new record
    self.db.execute_query_safe(
        f"""
        INSERT INTO {table_name}
        (title, translate_type, cat, lang, user, pupdate, target, mdwiki_revid)
        VALUES (%s, %s, %s, %s, %s, CURDATE(), %s, %s)
        """,
        (title, translate_type, cat, lang, user, target, mdwiki_revid)
    )

    return {"execute_query": True, "use_user_sql": to_users_table}
```

### 4. Ensure qids table exists

```python
# In a new db_qids.py or in db/__init__.py
def ensure_qids_table() -> None:
    """Create the qids table if it does not already exist."""
    db = get_db()
    db.execute_query_safe(
        """
        CREATE TABLE IF NOT EXISTS qids (
            id INT PRIMARY KEY AUTO_INCREMENT,
            title VARCHAR(255) NOT NULL,
            qid VARCHAR(20) NOT NULL,
            UNIQUE KEY (title)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """
    )
```

---

## Helper Services

### Dependencies to Add

Add to `requirements.txt` or `pyproject.toml`:

```
requests>=2.31.0
requests-oauthlib>=1.3.1
mwoauth>=0.3.7  # Alternative for OAuth
```

### Configuration Updates

Add to [src/app/config.py](../src/app_main/config.py):

```python
@dataclass(frozen=True)
class OAuthConfig:
    mw_uri: str
    consumer_key: str
    consumer_secret: str
    user_agent: str
    # New fields
    allowed_cors_domains: list[str]  # For CORS validation

# Update _load_oauth_config
def _load_oauth_config() -> Optional[OAuthConfig]:
    mw_uri = os.getenv("OAUTH_MWURI")
    consumer_key = os.getenv("OAUTH_CONSUMER_KEY")
    consumer_secret = os.getenv("OAUTH_CONSUMER_SECRET")
    if not (mw_uri and consumer_key and consumer_secret):
        return None

    cors_domains = os.getenv("ALLOWED_CORS_DOMAINS", "medwiki.toolforge.org,mdwikicx.toolforge.org")
    allowed_cors_domains = [d.strip() for d in cors_domains.split(",")]

    return OAuthConfig(
        mw_uri=mw_uri,
        consumer_key=consumer_key,
        consumer_secret=consumer_secret,
        user_agent=os.getenv(
            "USER_AGENT",
            "Copy SVG Translations/1.0 (https://copy-svg-langs.toolforge.org; tools.copy-svg-langs@toolforge.org)",
        ),
        allowed_cors_domains=allowed_cors_domains,
    )
```

---

## Testing Strategy

### 1. Unit Tests

Create tests for:
- CORS validation (`test_cors.py`)
- OAuth client functions (`test_oauth_client.py`)
- Text processing (`test_text_processor.py`)
- Formatting utilities (`test_format.py`)

### 2. Integration Tests

- Test full cxtoken flow with mock database
- Test full post flow with mock MediaWiki API
- Test database operations

### 3. End-to-End Tests

- Deploy to test environment
- Test with real MediaWiki OAuth
- Test with real database

### Test Examples

```python
# tests/test_cxtoken.py

def test_cxtoken_requires_cors(client):
    """Test that cxtoken endpoint rejects unauthorized origins."""
    response = client.get("/cxtoken/?wiki=en&user=test", headers={"Origin": "https://evil.com"})
    assert response.status_code == 403

def test_cxtoken_valid_request(client, mock_user_token):
    """Test successful cxtoken request."""
    response = client.get("/cxtoken/?wiki=en&user=TestUser", headers={"Origin": "https://medwiki.toolforge.org"})
    assert response.status_code == 200
    data = response.get_json()
    assert "csrftoken_data" in data

# tests/test_post.py

def test_post_requires_auth(client):
    """Test that post endpoint requires authentication."""
    response = client.post("/post/", json={
        "user": "test",
        "title": "Test",
        "target": "en",
        "sourcetitle": "Source",
        "text": "Test content"
    })
    assert response.status_code == 403 or response.status_code == 302
```

---

## Implementation Order

### Phase 1: Foundation (Week 1)

1. **Create helper modules**
   - [x] `helpers/cors.py` - CORS validation
   - [x] `helpers/format.py` - Title/user formatting
   - [x] `helpers/files.py` - File logging
   - [x] `services/text_processor.py` - Text processing

2. **Update database layer**
   - [x] Add `get_user_token_by_username()` to `users/store.py`
   - [x] Add `insert_page_target()` to `db/db_Pages.py`
   - [x] Ensure `qids` table exists

3. **Add dependencies**
   - [x] Update `requirements.txt` with OAuth libraries

### Phase 2: OAuth Service (Week 2)

1. **Create OAuth client**
   - [x] `services/oauth_client.py` with:
     - `get_csrf_token()`
     - `post_params()`
     - `get_cxtoken()`

2. **Create MediaWiki API client**
   - [x] `services/mediawiki_api.py` with:
     - `publish_do_edit()`

3. **Create revision ID service**
   - [x] `services/revids_service.py` with:
     - `get_revid()`
     - `get_revid_db()`

### Phase 3: cxtoken Endpoint (Week 2-3)

1. **Implement cxtoken route**
   - [x] Update `app_routes/cxtoken/routes.py`
   - [x] Add error handling for invalid authorization
   - [x] Add CORS headers to response

2. **Test cxtoken**
   - [x] Unit tests
   - [x] Integration tests with mock OAuth
   - [x] Manual testing with real OAuth

### Phase 4: Wikidata Service (Week 3)

1. **Create Wikidata client**
   - [x] `services/wikidata_client.py` with:
     - `get_qid_for_mdtitle()`
     - `get_title_info()`
     - `link_to_wikidata()`

2. **Test Wikidata integration**
   - [x] Unit tests
   - [x] Integration tests with mock API

### Phase 5: Post Endpoint (Week 4)

1. **Implement post route**
   - [x] Update `app_routes/post/routes.py`
   - [x] Implement `process_edit()` function
   - [x] Implement `handle_no_access()` function

2. **Test post endpoint**
   - [x] Unit tests for each function
   - [x] Integration tests with mock database and API
   - [x] End-to-end testing

### Phase 6: Deployment & Monitoring (Week 5)

1. **Deploy to test environment**
   - [x] Set environment variables
   - [x] Run database migrations
   - [x] Test with real OAuth

2. **Monitor and fix issues**
   - [x] Review logs
   - [x] Fix bugs
   - [x] Optimize performance

3. **Deploy to production**
   - [x] Gradual rollout
   - [x] Monitor metrics
   - [x] Rollback plan ready

---

## File Creation Checklist

### New Files to Create

- [x] `src/app/helpers/__init__.py`
- [x] `src/app/helpers/cors.py`
- [x] `src/app/helpers/format.py`
- [x] `src/app/helpers/files.py`
- [x] `src/app/services/__init__.py`
- [x] `src/app/services/oauth_client.py`
- [x] `src/app/services/mediawiki_api.py`
- [x] `src/app/services/revids_service.py`
- [x] `src/app/services/wikidata_client.py`
- [x] `src/app/services/text_processor.py`
- [x] `tests/test_helpers/test_cors.py`
- [x] `tests/test_helpers/test_format.py`
- [x] `tests/test_services/test_oauth_client.py`
- [x] `tests/test_services/test_mediawiki_api.py`
- [x] `tests/test_services/test_wikidata_client.py`
- [x] `tests/test_routes/test_cxtoken.py`
- [x] `tests/test_routes/test_post.py`

### Files to Modify

- [x] `src/app/app_routes/cxtoken/routes.py` - Full implementation
- [x] `src/app/app_routes/post/routes.py` - Full implementation
- [x] `src/app/users/store.py` - Add `get_user_token_by_username()`
- [x] `src/app/db/db_Pages.py` - Add `insert_page_target()`
- [x] `src/app/config.py` - Add CORS domains config
- [x] `requirements.txt` or `pyproject.toml` - Add dependencies
- [x] `src/app/__init__.py` - Register new blueprints if needed

---

## Risk Mitigation

### Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| OAuth library differences | High | Thorough testing of OAuth flow with real MediaWiki |
| Database schema differences | Medium | Create compatibility layer for access_keys table |
| Missing PHP functions | Medium | Implement missing Python equivalents incrementally |
| Text processing complexity | Low | Initially keep simple, iterate based on needs |
| CORS issues | Medium | Test with real browser requests from allowed domains |

---

## Notes

1. **Authentication**: PHP uses username-based lookup, Python uses user_id. Need to add username lookup capability.

2. **Encryption**: Both PHP and Python use defuse/php-encryption for compatible encryption. The Python `crypto.py` should already handle this.

3. **Logging**: File logging structure should match PHP structure for compatibility with existing tools.

4. **Error Handling**: PHP returns specific error codes that the frontend expects. Must match these exactly.

5. **Rate Limiting**: May need to add rate limiting for API endpoints to prevent abuse.

---

## References

- PHP OAuth Library: [MediaWiki OAuth Client](https://github.com/wikimedia/mediawiki-oauth-client)
- Python OAuth Library: [requests-oauthlib](https://requests-oauthlib.readthedocs.io/)
- MediaWiki API: [MediaWiki API Documentation](https://www.mediawiki.org/wiki/API:Main_page)
- Content Translation: [Content Translation Docs](https://www.mediawiki.org/wiki/Content_translation)
