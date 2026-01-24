# API Endpoint Plan: `publish_reports` Python Flask Route

This document outlines the implementation plan for migrating the PHP `/api/index.php?get=publish_reports` endpoint to a Python Flask route.

## Table of Contents

1. [Endpoint Overview](#endpoint-overview)
2. [Current State](#current-state)
3. [Target Architecture](#target-architecture)
4. [Database Handler Updates](#database-handler-updates)
5. [Route Implementation](#route-implementation)
6. [Query Parameters](#query-parameters)
7. [Special Value Handling](#special-value-handling)
8. [Frontend Template Update](#frontend-template-update)
9. [Example API Calls](#example-api-calls)
10. [Response Format](#response-format)
11. [Implementation Checklist](#implementation-checklist)

---

## Endpoint Overview

| Property | Value |
|----------|-------|
| **PHP URL** | `/api/index.php?get=publish_reports` |
| **Python URL** | `/api/publish_reports` |
| **Method** | `GET` |
| **Blueprint** | `bp_api` (new) or extend existing `bp_main` |
| **Database Handler** | `src/app/db/db_publish_reports.py` (existing - needs extension) |

---

## Current State

### Existing Database Handler
**File:** [`src/app/db/db_publish_reports.py`](../src/app/db/db_publish_reports.py)

The existing `ReportsDB` class provides basic CRUD operations:
- `list()` - Returns all records (no filtering)
- `add()` - Insert new record
- `delete()` - Delete by ID
- `_fetch_by_id()` - Fetch single record

**Missing Functionality:**
- Dynamic query filtering by parameters
- Support for `year`, `month` extraction from `date`
- Special value handling (`not_empty`, `empty`, `>0`)
- Field selection (`select` parameter)

### Existing Routes Structure
**File:** [`src/app/app_routes/__init__.py`](../src/app/app_routes/__init__.py)

```python
from .auth.routes import bp_auth
from .cxtoken.routes import bp_cxtoken
from .main.routes import bp_main
from .post.routes import bp_post
```

---

## Target Architecture

### New Files to Create

```
src/app/
├── app_routes/
│   └── api/
│       ├── __init__.py
│       └── routes.py          # NEW: API routes including publish_reports
└── db/
    └── db_publish_reports.py  # UPDATE: Add query_with_filters() method
```

### Updated Files

| File | Changes |
|------|---------|
| `src/app/db/db_publish_reports.py` | Add `query_with_filters()` method |
| `src/app/app_routes/__init__.py` | Register new `bp_api` blueprint |
| `src/app/app.py` (or main app file) | Register blueprint with prefix |
| `src/templates/reports.html` | Update API endpoint URLs |

---

## Database Handler Updates

### New Method: `query_with_filters()`

Add to `ReportsDB` class in `src/app/db/db_publish_reports.py`:

```python
from typing import Optional, List, Dict, Any

# Parameter configuration matching PHP endpoint_params
PUBLISH_REPORTS_PARAMS = [
    {"name": "year", "column": "YEAR(date)", "type": "number"},
    {"name": "month", "column": "MONTH(date)", "type": "number"},
    {"name": "title", "column": "title", "type": "text"},
    {"name": "user", "column": "user", "type": "text"},
    {"name": "lang", "column": "lang", "type": "text"},
    {"name": "sourcetitle", "column": "sourcetitle", "type": "text"},
    {"name": "result", "column": "result", "type": "text"},
]

class ReportsDB:
    # ... existing methods ...

    def query_with_filters(
        self,
        filters: Dict[str, Any],
        select_fields: Optional[List[str]] = None,
        limit: Optional[int] = None,
    ) -> List[ReportRecord]:
        """Query reports with dynamic filtering.
        
        Args:
            filters: Dictionary of filter parameters
            select_fields: Optional list of fields to return
            limit: Optional result limit
            
        Returns:
            List of matching ReportRecord objects
        """
        # Build SELECT clause
        if select_fields:
            valid_fields = {"id", "date", "title", "user", "lang", "sourcetitle", "result", "data"}
            fields = [f for f in select_fields if f in valid_fields]
            select_clause = ", ".join(fields) if fields else "*"
        else:
            select_clause = "id, date, title, user, lang, sourcetitle, result, data"
        
        query = f"SELECT DISTINCT {select_clause} FROM publish_reports"
        params = []
        conditions = []
        
        for param_def in PUBLISH_REPORTS_PARAMS:
            name = param_def["name"]
            column = param_def["column"]
            
            if name not in filters:
                continue
                
            value = filters[name]
            
            # Handle special values
            if value in ("not_mt", "not_empty"):
                conditions.append(f"({column} != '' AND {column} IS NOT NULL)")
            elif value in ("mt", "empty"):
                conditions.append(f"({column} = '' OR {column} IS NULL)")
            elif value in (">0", "&#62;0"):
                conditions.append(f"{column} > 0")
            elif str(value).lower() == "all":
                continue  # Skip this filter
            else:
                conditions.append(f"{column} = %s")
                params.append(value)
        
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        
        query += " ORDER BY id DESC"
        
        if limit:
            query += f" LIMIT {int(limit)}"
        
        rows = self.db.fetch_query_safe(query, tuple(params) if params else None)
        return [self._row_to_record(row) for row in rows]
```

---

## Route Implementation

### New File: `src/app/app_routes/api/routes.py`

```python
"""API endpoints for publish_reports.

Mirrors: php_src/endpoints/index.php?get=publish_reports
"""

import logging
from typing import Any, Dict, List, Optional

from flask import Blueprint, Response, jsonify, request

from ...config import settings
from ...db.db_publish_reports import ReportsDB
from ...helpers.cors import is_allowed

bp_api = Blueprint("api", __name__)
logger = logging.getLogger(__name__)


def _parse_select_fields(select_param: Optional[str]) -> Optional[List[str]]:
    """Parse the select parameter into a list of field names."""
    if not select_param:
        return None
    return [f.strip() for f in select_param.split(",") if f.strip()]


def _record_to_dict(record) -> Dict[str, Any]:
    """Convert a ReportRecord to a dictionary."""
    return {
        "id": record.id,
        "date": record.date.isoformat() if hasattr(record.date, 'isoformat') else str(record.date),
        "title": record.title,
        "user": record.user,
        "lang": record.lang,
        "sourcetitle": record.sourcetitle,
        "result": record.result,
        "data": record.data,
    }


@bp_api.route("/publish_reports", methods=["GET", "OPTIONS"])
def get_publish_reports() -> Response:
    """Handle publish_reports API requests.
    
    Query Parameters:
        year: Filter by year of date
        month: Filter by month of date
        title: Filter by page title
        user: Filter by username
        lang: Filter by language code
        sourcetitle: Filter by source title
        result: Filter by result status
        select: Comma-separated list of fields to return
        limit: Maximum number of results
        
    Special Values:
        not_empty / not_mt: Field is not empty
        empty / mt: Field is empty
        >0: Field is greater than 0
        all: Skip this filter
        
    Returns:
        JSON response with matching reports or error
    """
    # Handle CORS preflight
    allowed = is_allowed()
    
    if request.method == "OPTIONS":
        if not allowed:
            return jsonify({"error": "CORS not allowed"}), 403
        response = Response("", status=200)
        response.headers["Access-Control-Allow-Origin"] = f"https://{allowed}"
        response.headers["Access-Control-Allow-Methods"] = "GET, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type"
        return response

    try:
        # Extract filter parameters
        filters = {}
        filter_params = ["year", "month", "title", "user", "lang", "sourcetitle", "result"]
        
        for param in filter_params:
            value = request.args.get(param)
            if value is not None and value != "":
                filters[param] = value
        
        # Extract select fields
        select_param = request.args.get("select")
        select_fields = _parse_select_fields(select_param)
        
        # Extract limit
        limit = request.args.get("limit", type=int)
        
        # Query database
        db = ReportsDB(settings.db_data)
        records = db.query_with_filters(filters, select_fields, limit)
        
        # Build response
        data = [_record_to_dict(r) for r in records]
        
        response_data = {
            "results": data,
            "count": len(data),
        }
        
        response = jsonify(response_data)
        
        if allowed:
            response.headers["Access-Control-Allow-Origin"] = f"https://{allowed}"
        
        return response
        
    except Exception as e:
        logger.exception("Error fetching publish_reports")
        return jsonify({
            "error": str(e)
        }), 500


__all__ = ["bp_api"]
```

### New File: `src/app/app_routes/api/__init__.py`

```python
from .routes import bp_api

__all__ = ["bp_api"]
```

### Update: `src/app/app_routes/__init__.py`

```python
from .api.routes import bp_api
from .auth.routes import bp_auth
from .cxtoken.routes import bp_cxtoken
from .main.routes import bp_main
from .post.routes import bp_post

__all__ = [
    "bp_api",
    "bp_auth",
    "bp_main",
    "bp_cxtoken",
    "bp_post",
]
```

### Register Blueprint (in main app file)

```python
from app_routes import bp_api

app.register_blueprint(bp_api, url_prefix="/api")
```

---

## Query Parameters

### Available Filters

| Parameter | Column/Expression | Type | Description |
|-----------|-------------------|------|-------------|
| `year` | `YEAR(date)` | number | Filter by year extracted from date |
| `month` | `MONTH(date)` | number | Filter by month extracted from date |
| `title` | `title` | text | Filter by page title |
| `user` | `user` | text | Filter by username |
| `lang` | `lang` | text | Filter by language code |
| `sourcetitle` | `sourcetitle` | text | Filter by source title |
| `result` | `result` | text | Filter by result status |
| `select` | - | text | Comma-separated fields to return |
| `limit` | - | number | Maximum results to return |

---

## Special Value Handling

| Value | Behavior | SQL Generated |
|-------|----------|---------------|
| `not_mt` / `not_empty` | Column is not empty | `(column != '' AND column IS NOT NULL)` |
| `mt` / `empty` | Column is empty | `(column = '' OR column IS NULL)` |
| `>0` / `&#62;0` | Column greater than 0 | `column > 0` |
| `all` | Skip this filter | *(parameter ignored)* |

---

## Frontend Template Update

### File: `src/templates/reports.html`

The frontend template currently uses the PHP API endpoint. Update the following JavaScript code to use the new Python Flask endpoint:

#### Changes Required

**Line 176** - Update filter options loader:
```javascript
// OLD:
$.getJSON('/api/index.php?get=publish_reports')

// NEW:
$.getJSON('/api/publish_reports')
```

**Line 190** - Update DataTable AJAX URL:
```javascript
// OLD:
ajax: {
    url: '/api/index.php?get=publish_reports',
    ...
}

// NEW:
ajax: {
    url: '/api/publish_reports',
    ...
}
```

#### Full Updated JavaScript Section

```javascript
$(document).ready(function() {
    // Load filters once only
    $.getJSON('/api/publish_reports')  // <-- UPDATED
        .done(function(json) {
            if (json && json.results) {
                populateFilterOptions(json.results);
            }
        })
        .fail(function(xhr, status, error) {
            console.error('Failed to load filter options:', error);
        });

    // DataTable setup
    let table = $('#resultsTable').DataTable({
        ajax: {
            url: '/api/publish_reports',  // <-- UPDATED
            data: function(d) {
                const formData = $('#filterForm').serializeArray();
                formData.forEach(field => {
                    if (field.value.trim()) {
                        d[field.name] = field.value;
                    }
                });
            },
            dataSrc: function(json) {
                // ... rest of the code remains the same
            }
        },
        // ... rest of DataTable config
    });
    // ... rest of the code
});
```

---

## Example API Calls

### 1. Get all reports for a specific user
```
GET /api/publish_reports?user=JohnDoe
```

### 2. Get reports for a specific year and month
```
GET /api/publish_reports?year=2026&month=1
```

### 3. Get reports for a specific language and user
```
GET /api/publish_reports?lang=ar&user=MrIbrahem
```

### 4. Get reports with non-empty results
```
GET /api/publish_reports?result=not_empty
```

### 5. Get specific fields only
```
GET /api/publish_reports?user=Admin&select=title,date,result
```

### 6. Combined filters with limit
```
GET /api/publish_reports?year=2026&lang=en&limit=100
```

---

## Response Format

### Success Response
```json
{
    "results": [
        {
            "id": 123,
            "date": "2026-01-24T10:30:00",
            "title": "Example_Page",
            "user": "JohnDoe",
            "lang": "en",
            "sourcetitle": "Source_Example",
            "result": "success",
            "data": "{\"key\": \"value\"}"
        }
    ],
    "count": 1
}
```

### Error Response
```json
{
    "error": "Error description"
}
```

---

## Implementation Checklist

### Phase 1: Database Layer
- [x] Add `PUBLISH_REPORTS_PARAMS` configuration to `db_publish_reports.py`
- [x] Implement `query_with_filters()` method in `ReportsDB` class
- [x] Add unit tests for new database method

### Phase 2: Route Layer
- [x] Create `src/app/app_routes/api/` directory
- [x] Create `src/app/app_routes/api/__init__.py`
- [x] Create `src/app/app_routes/api/routes.py` with `get_publish_reports()` endpoint
- [x] Update `src/app/app_routes/__init__.py` to export `bp_api`
- [x] Register blueprint in main app file

### Phase 3: Frontend Update
- [x] Update `src/templates/reports.html` line 176: change `/api/index.php?get=publish_reports` to `/api/publish_reports`
- [x] Update `src/templates/reports.html` line 190: change `/api/index.php?get=publish_reports` to `/api/publish_reports`
- [x] Test frontend functionality with new endpoint

### Phase 4: Testing
- [x] Test each parameter filter individually
- [x] Test combined parameter filters
- [x] Test special values (`not_empty`, `empty`, `>0`)
- [x] Test `select` field filtering
- [x] Test `limit` parameter
- [x] Verify CORS handling
- [x] Test frontend integration

### Phase 5: Documentation
- [x] Update API documentation (see `docs/api.md`)
- [x] Add OpenAPI/Swagger spec (see `docs/openapi.yaml`)

---

## Security Considerations

1. **Parameterized Queries**: All user values use `%s` placeholders
2. **Field Validation**: Only predefined fields from `PUBLISH_REPORTS_PARAMS` are accepted
3. **Select Field Validation**: Only valid column names allowed in `select`
4. **Limit Validation**: Cast to integer to prevent injection
5. **CORS**: Uses existing `is_allowed()` helper for domain validation
6. **Special Value Whitelist**: Special values are hardcoded, not user-defined
