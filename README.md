
# Overview
This repository manages the final steps in the process of publishing Wikipedia articles that have been translated using the [ContentTranslation tool](https://github.com/mdwikicx/cx-1) in [medwiki.toolforge.org](http://medwiki.toolforge.org/). It takes the translated text in wikitext format, refines it further, and then publishes it to Wikipedia.

# API Documentation

## REST API Endpoints

### GET `/api/publish_reports`

Retrieves publish reports with optional filtering.

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `year` | number | Filter by year (e.g., `2026`) |
| `month` | number | Filter by month (1-12) |
| `title` | string | Filter by page title |
| `user` | string | Filter by username |
| `lang` | string | Filter by language code |
| `sourcetitle` | string | Filter by source title |
| `result` | string | Filter by result status |
| `select` | string | Comma-separated fields to return |
| `limit` | number | Maximum results to return |

**Special Filter Values:** `not_empty`, `empty`, `>0`, `all`

**Example:**
```
GET /api/publish_reports?year=2026&user=JohnDoe&limit=100
```

**Response:**
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
            "data": "{}"
        }
    ],
    "count": 1
}
```

For complete API documentation, see [docs/api.md](docs/api.md).

For OpenAPI/Swagger specification, see [docs/openapi.yaml](docs/openapi.yaml).

# How it's working
Before publishing to Wikipedia, this process uses the [fix_refs](https://github.com/MrIbrahem/fix_refs_new_py) repository to make several changes to the wikitext. These changes include:

* **Fixing References:** Correcting and standardizing reference formatting.
* **Expanding Infoboxes:** Enhancing infoboxes with more relevant information.
* **Adding Categories:** Ensuring appropriate categories are assigned to the articles.
* **Other changes:** Adding and correcting other minor issues in wikitext.
