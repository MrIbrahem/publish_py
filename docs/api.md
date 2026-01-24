# API Documentation

This document describes the REST API endpoints available in the publish_py application.

## Base URL

All API endpoints are prefixed with `/api`.

---

## Publish Reports API

### GET `/api/publish_reports`

Retrieves publish reports with optional filtering.

#### Query Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `year` | number | Filter by year extracted from date (e.g., `2026`) |
| `month` | number | Filter by month extracted from date (e.g., `1` for January) |
| `title` | string | Filter by page title |
| `user` | string | Filter by username |
| `lang` | string | Filter by language code (e.g., `ar`, `en`) |
| `sourcetitle` | string | Filter by source title |
| `result` | string | Filter by result status |
| `select` | string | Comma-separated list of fields to return |
| `limit` | number | Maximum number of results to return |

#### Special Filter Values

| Value | Behavior |
|-------|----------|
| `not_mt` / `not_empty` | Field is not empty |
| `mt` / `empty` | Field is empty |
| `>0` | Field is greater than 0 |
| `all` | Skip this filter (return all values) |

#### Response Format

**Success Response (200 OK)**

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

**Error Response (500 Internal Server Error)**

```json
{
    "error": "An internal error occurred while fetching reports"
}
```

#### Example Requests

**Get all reports for a specific user:**
```
GET /api/publish_reports?user=JohnDoe
```

**Get reports for a specific year and month:**
```
GET /api/publish_reports?year=2026&month=1
```

**Get reports for a specific language and user:**
```
GET /api/publish_reports?lang=ar&user=MrIbrahem
```

**Get reports with non-empty results:**
```
GET /api/publish_reports?result=not_empty
```

**Get specific fields only:**
```
GET /api/publish_reports?user=Admin&select=title,date,result
```

**Combined filters with limit:**
```
GET /api/publish_reports?year=2026&lang=en&limit=100
```

---

## CORS

The API supports CORS for the following domains (configurable via environment):
- `medwiki.toolforge.org`
- `mdwikicx.toolforge.org`

Preflight requests (OPTIONS) are handled automatically.

---

## Authentication

The `/api/publish_reports` endpoint is a public read-only endpoint and does not require authentication.

---

## Rate Limiting

No rate limiting is currently implemented. Please use responsibly.
