# PHP to Python Integration Plan

## Overview
This plan outlines the migration of two key PHP endpoints to Python:
1. **cxtoken** - `php_src/endpoints/cxtoken.php` → `src/app/app_routes/cxtoken/routes.py`
2. **post** - `php_src/endpoints/post.php` → `src/app/app_routes/post/routes.py`

---

## Phase 1: Shared Infrastructure

### 1.1 CORS Middleware
**PHP Source**: `php_src/bots/cors.php`
**Python Target**: New `src/app/middleware/cors.py`

Create a Flask middleware for domain validation:
- Check HTTP_REFERER and HTTP_ORIGIN headers
- Allow only `medwiki.toolforge.org` and `mdwikicx.toolforge.org`
- Return 403 if not authorized
- Set appropriate CORS headers

```python
# src/app/middleware/cors.py
ALLOWED_DOMAINS = ['medwiki.toolforge.org', 'mdwikicx.toolforge.org']

def check_request_origin(request):
    referer = request.headers.get('Referer', '')
    origin = request.headers.get('Origin', '')
    for domain in ALLOWED_DOMAINS:
        if domain in referer or domain in origin:
            return domain
    return None
```

### 1.2 Database Access Helpers
**PHP Source**: `php_src/bots/sql/access_helps.php`
**Python Target**: Update `src/app/db/db_access.py` (NEW)

Create a module for OAuth access key management:
- `get_access_from_db(user)` - Retrieve access_key and access_secret for a user
- `del_access_from_db(user)` - Delete access record for a user
- Decrypt stored credentials using existing `crypto.py`

---

## Phase 2: cxtoken Endpoint

### 2.1 OAuth Token Service
**PHP Source**: `php_src/bots/api/get_token.php`
**Python Target**: New `src/app/services/oauth_token.py`

Implement MediaWiki OAuth token retrieval:
- `get_client(wiki)` - Create OAuth client for a wiki
- `get_csrftoken(client, access_key, access_secret, api_url)` - Get CSRF token
- `post_params(apiParams, https_domain, access_key, access_secret)` - Make authenticated API calls
- `get_cxtoken(wiki, access_key, access_secret)` - Get CX token

**Dependencies**:
- Need to add `mwoauth` or `requests-oauthlib` to requirements

### 2.2 cxtoken Route Implementation
**PHP Source**: `php_src/endpoints/cxtoken.php`
**Python Target**: Update `src/app/app_routes/cxtoken/routes.py`

Implement the endpoint:
1. Apply CORS check middleware
2. Validate `wiki` and `user` query parameters
3. Apply special user mapping (`Mr. Ibrahem 1` → `Mr. Ibrahem`, `Admin` → `Mr. Ibrahem`)
4. Get access credentials from database
5. Return 403 if no access found
6. Call `get_cxtoken(wiki, access_key, access_secret)`
7. Check for `mwoauth-invalid-authorization-invalid-user` error and delete invalid access
8. Return JSON response

**HTTP Method**: GET
**Route**: `/cxtoken/`
**Query Parameters**: `wiki`, `user`

---

## Phase 3: post Endpoint

### 3.1 Helper Functions
**PHP Source**: `php_src/endpoints/post.php` (lines 14-45)
**Python Target**: New `src/app/services/post_helpers.py`

Implement helper functions:
- `make_summary(revid, sourcetitle, to, hashtag)` - Generate edit summary
- `format_title(title)` - Replace underscores and fix user paths
- `format_user(user)` - Apply special user mapping
- `determine_hashtag(title, user)` - Return `#mdwikicx` or empty string
- `handle_no_access(user, tab)` - Handle no access case, log to database

### 3.2 Revision ID Service
**PHP Source**: `php_src/bots/revids_bot.php`
**Python Target**: New `src/app/services/revid_service.py`

Implement revision ID retrieval:
- `get_revid(sourcetitle)` - Get revision ID from cache/JSON file
- `get_revid_db(sourcetitle)` - Fallback to database query

### 3.3 Text Processing Service
**PHP Source**: `php_src/text_change.php`
**Python Target**: New `src/app/services/text_fix.py`

Implement text modifications:
- `do_changes_to_text1(sourcetitle, title, text, lang, mdwiki_revid)`
- Currently a placeholder - same in Python

### 3.4 Wikidata Linking Service
**PHP Source**: `php_src/bots/wd.php`
**Python Target**: New `src/app/services/wikidata.py`

Implement Wikidata integration:
- `get_qid_for_mdtitle(title)` - Get Wikidata QID from database
- `get_title_info(targettitle, lang)` - Get page info from MediaWiki API
- `link_it(qid, lang, sourcetitle, targettitle, access_key, access_secret)` - Link page to Wikidata item
- `link_to_wikidata(sourcetitle, lang, user, targettitle, access_key, access_secret)` - Main linking function
- `retry_with_fallback_user(...)` - Fallback to Mr. Ibrahem for user page links

### 3.5 Edit Processing Service
**PHP Source**: `php_src/bots/api/process_edit.php`
**Python Target**: New `src/app/services/edit_processor.py`

Implement edit processing logic:
- `prepare_api_params(title, summary, text, request)` - Prepare MediaWiki API parameters
- `get_errors_file(editit, place_holder)` - Categorize errors for retry files
- `handle_successful_edit(...)` - Process successful edits and link to Wikidata
- `add_to_db(...)` - Add to database tables (pages/users tables)
- `process_edit(request, access, text, user, tab)` - Main edit processing function

**Note**: This uses `publish_do_edit` from `php_src/bots/api/do_edit.php`

### 3.6 Do Edit Service
**PHP Source**: `php_src/bots/api/do_edit.php`
**Python Target**: New `src/app/services/do_edit.py`

Implement MediaWiki edit execution:
- `get_edits_token(client, accessToken, apiUrl)` - Get edit CSRF token
- `publish_do_edit(apiParams, wiki, access_key, access_secret)` - Execute the edit

### 3.7 File Helpers
**PHP Source**: `php_src/bots/files_helps.php`
**Python Target**: New `src/app/services/file_helpers.py`

Implement file operations:
- `to_do(tab, file_name)` - Write JSON files for retry/error tracking
- Need to determine where these files should be stored (configurable path)

### 3.8 post Route Implementation
**PHP Source**: `php_src/endpoints/post.php`
**Python Target**: Update `src/app/app_routes/post/routes.py`

Implement the endpoint:
1. Extract `user`, `title`, `target` (lang), `campaign`, `sourcetitle`, `text` from request
2. Format user and title using helper functions
3. Build `tab` dictionary with all metadata
4. Get access credentials from database
5. Handle no access case if credentials not found
6. Get revision ID (revid) from cache/database
7. Generate edit summary
8. Apply text fixes if available
9. Process the edit
10. Link to Wikidata on success
11. Log to database and files
12. Return JSON response

**HTTP Method**: POST
**Route**: `/post/`
**Request Parameters** (JSON body):
- `user` - Username
- `title` - Target page title
- `target` - Target language code
- `campaign` - Campaign name
- `sourcetitle` - Source page title
- `text` - Page content
- `revid` (optional) - Revision ID

---

## Phase 4: Database Updates

### 4.1 Create `access_keys` Table
**PHP Source**: Implicit in `php_src/bots/sql/access_helps.php`
**Python Target**: Add to `src/app/db/db_access.py`

```sql
CREATE TABLE IF NOT EXISTS `access_keys` (
    `user_name` varchar(255) NOT NULL,
    `access_key` text NOT NULL,
    `access_secret` text NOT NULL,
    PRIMARY KEY (`user_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

### 4.2 Create `qids` Table
**PHP Source**: `php_src/bots/wd.php`
**Python Target**: Add to `src/app/db/db_qids.py` (NEW)

```sql
CREATE TABLE IF NOT EXISTS `qids` (
    `id` int NOT NULL AUTO_INCREMENT,
    `title` varchar(255) NOT NULL,
    `qid` varchar(255) NOT NULL,
    PRIMARY KEY (`id`),
    KEY `idx_title` (`title`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

### 4.3 Create `campaign_categories` Table
**PHP Source**: `php_src/bots/api/process_edit.php`
**Python Target**: Add to appropriate DB module

```sql
CREATE TABLE IF NOT EXISTS `campaign_categories` (
    `campaign` varchar(255) NOT NULL,
    `category` varchar(255) NOT NULL,
    PRIMARY KEY (`campaign`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

---

## Phase 5: Configuration

### 5.1 OAuth Configuration
**PHP Source**: `php_src/bots/config.php`
**Python Target**: Update `src/app/config.py`

Ensure existing `OAuthConfig` includes:
- `consumer_key`
- `consumer_secret`
- `user_agent` - `mdwiki MediaWiki OAuth Client/1.0`

### 5.2 Database Configuration
**PHP Source**: `php_src/bots/services/sql_db.php`
**Python Target**: Verify `src/app/config.py` database configuration

Ensure multi-database support (mdwiki, mdwiki_new) exists for different tables.

---

## Phase 6: Testing

### 6.1 Unit Tests
- Test CORS validation
- Test access key retrieval and deletion
- Test token generation
- Test helper functions (format_user, make_summary, etc.)
- Test revision ID retrieval
- Test Wikidata linking
- Test edit processing

### 6.2 Integration Tests
- Test cxtoken endpoint with valid credentials
- Test cxtoken endpoint with invalid credentials
- Test post endpoint with successful edit
- Test post endpoint with no access
- Test post endpoint with captcha
- Test post endpoint with various error conditions

### 6.3 Manual Testing
- Test from medwiki.toolforge.org
- Test from mdwikicx.toolforge.org
- Test with special users (Mr. Ibrahem, Admin)
- Test error recovery and fallback mechanisms

---

## Phase 7: Dependencies

### 7.1 Add to Requirements
```
mwoauth>=0.3.8
requests>=2.31.0
requests-oauthlib>=1.3.1
```

### 7.2 Optional Dependencies
```
mwclient>=0.11.0  # Alternative MediaWiki API client
```

---

## Implementation Order

1. **Week 1**: Phase 1 (CORS middleware, DB access helpers)
2. **Week 2**: Phase 2 (cxtoken endpoint) + Phase 4.1 (access_keys table)
3. **Week 3**: Phase 3.1-3.4 (Helpers, Revision, Text, Wikidata) + Phase 4.2-4.3 (Additional tables)
4. **Week 4**: Phase 3.5-3.8 (Edit processing, Do edit, File helpers, post endpoint)
5. **Week 5**: Phase 5 (Configuration updates) + Phase 6 (Testing)

---

## Notes

### Special User Mapping
Both endpoints use special user mapping:
- `"Mr. Ibrahem 1"` → `"Mr. Ibrahem"`
- `"Admin"` → `"Mr. Ibrahem"`

This should be implemented as a constant in a shared location.

### Error Handling
- 403 Forbidden for unauthorized domains
- 403 Forbidden for missing access credentials
- Appropriate error messages for API failures
- Delete invalid access tokens on `mwoauth-invalid-authorization-invalid-user` errors

### Logging
- Use Python's standard `logging` module
- Mirror PHP's `logger_debug()` function behavior (respect debug/test mode)

### Encryption
- Reuse existing `src/app/crypto.py` for encryption/decryption
- Ensure compatibility with PHP's Defuse\Crypto

### File Paths
- Determine where JSON retry files should be stored
- Make paths configurable via environment variables
