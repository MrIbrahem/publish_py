"""
Configuration for the new_html module.
"""

import os
from pathlib import Path

# Base directory for storing revision caches
# You can override this with the REVISIONS_DIR environment variable
REVISIONS_PATH = Path(os.getenv("REVISIONS_DIR", Path.home() / "public_html" / "revisions_new1"))

# Ensure the revisions directory exists
REVISIONS_PATH.mkdir(parents=True, exist_ok=True)

# JSON files that map title → revision_id
JSON_FILE = REVISIONS_PATH / "json_data.json"
JSON_FILE_ALL = REVISIONS_PATH / "json_data_all.json"

# Create empty JSON files if they do not exist
for json_path in (JSON_FILE, JSON_FILE_ALL):
    if not json_path.exists():
        json_path.write_text("{}", encoding="utf-8")

# User-Agent used for external API requests
USER_AGENT = (
    "WikiProjectMed Translation Dashboard/1.0 (https://medwiki.toolforge.org/; tools.mdwikicx@toolforge.org)"
)

# Allowed origins for CORS
ALLOWED_ORIGINS = [
    "mdwikicx.toolforge.org",
    "mdwiki.toolforge.org",
    "medwiki.toolforge.org",
]
