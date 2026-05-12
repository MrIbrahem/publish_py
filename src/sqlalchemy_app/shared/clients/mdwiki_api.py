"""
MediaWiki API client for edit operations and category fetching.

Mirrors: results/getcats.php
"""

import json
import logging
import os
import re
from pathlib import Path
from typing import Any

import requests

from ...config import settings

logger = logging.getLogger(__name__)

NS_MAIN = 0
NS_CATEGORY = 14
NS_CUSTOM = 3000


class CategoryFetcher:
    """Fetch category members from mdwiki.org API with depth recursion and file cache.

    Mirrors: results/getcats.php (CategoryFetcher class)
    """

    def __init__(
        self,
        options: dict[str, Any] | None = None,
        endpoint: str = "",
    ):
        self.options = options or {}
        self.endpoint = endpoint or "https://mdwiki.org/w/api.php"
        self.debug = bool(self.options.get("debug", False))
        self.connect_timeout = self.options.get("connect_timeout", 10)
        self.timeout = self.options.get("timeout", 15)
        self.tables_dir = self.options.get("tablesDir", "")

    def get_mdwiki_cat_members(self, root_cat: str, depth: int = 0, use_cache: bool = True) -> list[str]:
        """Fetch all page titles under a category up to given depth.

        Args:
            root_cat: Category name (with or without 'Category:' prefix)
            depth: 0 = root only, 1 = include subcats one level, etc.
            use_cache: Whether to try file cache first

        Returns:
            Unique, filtered list of page titles
        """
        depth = max(0, depth)
        titles: list[str] = []
        cats: list[str] = [root_cat]
        depth_done = -1

        while cats and depth > depth_done:
            next_cats: list[str] = []
            for cat in cats:
                all_titles = self._get_cats_members(cat, use_cache)
                for title in all_titles:
                    if title.startswith("Category:"):
                        next_cats.append(title)
                    else:
                        titles.append(title)
            depth_done += 1
            cats = next_cats

        titles = list(dict.fromkeys(titles))
        return self._titles_filter(titles)

    def _get_cats_members(self, cat: str, use_cache: bool) -> list[str]:
        all_items: list[str] = []
        if use_cache:
            all_items = self._get_cats_from_cache(cat)
        if not all_items:
            all_items = self._fetch_cats_members_api(cat)
        return all_items

    def _fetch_cats_members_api(self, cat: str) -> list[str]:
        if not cat.startswith("Category:"):
            cat = f"Category:{cat}"

        params: dict[str, str] = {
            "action": "query",
            "list": "categorymembers",
            "cmtitle": cat,
            "cmlimit": "max",
            "cmtype": "page|subcat",
            "format": "json",
        }

        items: list[str] = []
        cmcontinue: str | None = "x"
        iteration = 0
        max_iterations = 100

        while cmcontinue and iteration < max_iterations:
            iteration += 1
            if cmcontinue != "x":
                params["cmcontinue"] = cmcontinue

            data = self._post_urls_mdwiki(params)
            members = data.get("query", {}).get("categorymembers", [])
            if not members:
                break

            cmcontinue = data.get("continue", {}).get("cmcontinue", "")

            for page in members:
                ns = page.get("ns", -1)
                if ns in (NS_MAIN, NS_CATEGORY, NS_CUSTOM):
                    items.append(page["title"])

        if iteration >= max_iterations:
            logger.warning("fetch_cats_members_api: Hit maximum iterations for '%s'", cat)

        return items

    def _get_cats_from_cache(self, cat: str) -> list[str]:
        if self.options.get("nocache"):
            return []
        data = self._open_tables_file(cat)
        if not data:
            return []
        lst = data.get("list")
        if not isinstance(lst, list):
            return []
        return lst

    def _open_tables_file(self, cat: str) -> dict | None:
        if not self.tables_dir:
            return None
        safe_cat = cat.replace("/", "").replace("\\", "").replace("..", "")
        file_path = Path(self.tables_dir) / "cats_cash" / f"{safe_cat}.json"
        if not file_path.is_file():
            return None
        try:
            with open(file_path, encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError) as e:
            logger.warning("Failed to read cache file %s: %s", file_path, e)
            return None

    def _titles_filter(self, titles: list[str]) -> list[str]:
        pattern = re.compile(r"^(File|Template|User):")
        disambig = re.compile(r"\(disambiguation\)$")
        result = []
        for t in titles:
            if not isinstance(t, str):
                continue
            if pattern.match(t):
                continue
            if disambig.search(t):
                continue
            result.append(t)
        return result

    def _post_urls_mdwiki(self, params: dict) -> dict:
        resp = requests.post(
            self.endpoint,
            data=params,
            headers={"User-Agent": settings.user_agent},
            timeout=(self.connect_timeout, self.timeout),
        )
        resp.raise_for_status()
        return resp.json()


def get_mdwiki_cat_members(cat: str, depth: int = 0, use_cache: bool = True) -> list[str]:
    """Convenience function: create fetcher with default options and fetch."""
    options = {
        "tablesDir": os.getenv("JSON_TABLES_PATH", ""),
    }
    fetcher = CategoryFetcher(options)
    return fetcher.get_mdwiki_cat_members(cat, depth, use_cache)
