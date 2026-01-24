[![Ask DeepWiki](https://deepwiki.com/badge.svg)](https://deepwiki.com/Mdwiki-TD/publish)

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
Before publishing to Wikipedia, this process uses the [fix_refs](https://github.com/Mdwiki-TD/fix_refs) repository to make several changes to the wikitext. These changes include:

* **Fixing References:** Correcting and standardizing reference formatting.
* **Expanding Infoboxes:** Enhancing infoboxes with more relevant information.
* **Adding Categories:** Ensuring appropriate categories are assigned to the articles.
* **Other changes:** Adding and correcting other minor issues in wikitext.

These pre-processing steps help ensure the quality and consistency of articles published to Wikipedia.

# Usage
The main script to run is `index.php`. It processes the publishing of Wikipedia articles by performing the following steps:

1. **Read Revision ID:** The script reads the `all_pages_revids.json` file to get the revision ID of the source title.
2. **Make Summary:** Creates a summary for the edit based on the revision ID, source title, target language, and hashtag.
3. **Pre-process Text:** Uses the `fix_refs` repository to make necessary changes to the wikitext.
4. **Prepare API Parameters:** Prepares the parameters needed for the Wikipedia API request.
5. **Handle No Access:** If the user does not have access, it logs the error.
6. **Process Edit:** If the user has access, it processes the edit by making the API request to Wikipedia.
7. **Handle Successful Edit:** If the edit is successful, it links the article to Wikidata and logs the result.

# Functions
The main functions in `index.php` include:

- `get_revid($sourcetitle)`: Reads the revision ID from `all_pages_revids.json`.
- `make_summary($revid, $sourcetitle, $to, $hashtag)`: Creates the edit summary.
- `to_do($tab, $dir)`: Logs the tasks to a file.
- `formatTitle($title)`: Formats the title.
- `formatUser($user)`: Formats the user name.
- `determineHashtag($title, $user)`: Determines the hashtag to be used.
- `prepareApiParams($title, $summary, $text, $request)`: Prepares the API parameters for the edit request.
- `handleNoAccess($user, $tab)`: Handles cases where the user does not have access.
- `processEdit($access, $sourcetitle, $text, $lang, $revid, $campaign, $user, $title, $summary, $request, $tab)`: Processes the edit request.
- `handleSuccessfulEdit($sourcetitle, $campaign, $lang, $user, $title, $editit, $access_key, $access_secret)`: Handles successful edits and links the article to Wikidata.
- `start($request)`: The main function that starts the process based on the request parameters.

# Notes
- Ensure that the necessary dependencies and files, such as `all_pages_revids.json`, are available in the directory.
- The script uses several helper functions from other included files, such as `fix_refs`, `DoChangesToText`, and `LinkToWikidata`.

# License
# Diagram
```mermaid

```
