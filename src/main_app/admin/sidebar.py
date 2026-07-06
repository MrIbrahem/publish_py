from __future__ import annotations

import functools
import logging
from dataclasses import dataclass
from typing import Any

from flask import has_request_context, url_for

logger = logging.getLogger(__name__)

@dataclass
class SidebarItem:
    """Sidebar menu item definition."""

    id: str
    admin: int
    href: str
    title: str
    icon: str | None = None
    target: str | None = None
    disabled: bool = False


def _safe_url_for(endpoint: str, fallback: str, **values) -> str:
    if has_request_context():
        return url_for(endpoint, **values)
    return fallback

def generate_list_item(item: SidebarItem) -> str:
    """Generate HTML for a single navigation link."""
    href_full = item.href if item.target else f"/admin/{item.href}"
    if item.href.startswith("/admin/"):
        href_full = item.href

    icon_tag = f"<i class='bi {item.icon} me-1'></i>" if item.icon else ""
    target_attr = "target='_blank'" if item.target else ""
    link = f"""
        <a {target_attr} class='link_nav rounded' href='{href_full}' title='{item.title}'
           data-bs-toggle='tooltip' data-bs-placement='right'>
            {icon_tag}
            <span class='hide-on-collapse-inline'>{item.title}</span>
        </a>
    """
    return link.strip()


class Sidebar:
    def __init__(
        self,
        menu: dict[str, list[SidebarItem]],
        menu_icons: dict[str, str],
        active_route: str,
        path: str | None = None,
    ) -> None:
        self.menu = menu
        self.menu_icons = menu_icons
        self.active_route = active_route
        self.path = path

    def get_the_active_group_and_sub(self) -> tuple[str, str]:
        """
        Determines the active menu group and the active menu item ID based on the current path or active route.

        This method iterates through the menu items to find an exact match for the current path.
        If an exact match is found, it immediately sets the corresponding group and item ID as active.
        If no exact match is found, it falls back to checking if the current path starts with an item's href,
        or if an item's ID matches the active_route attribute.
        If no active group is determined after checking all items, it defaults to the first group in the menu.

        Returns:
            tuple[str, int]: A tuple containing the active group key (str) and the active item ID (int).
        """
        active_group = ""
        active_id = 0

        for key, items in self.menu.items():
            active_hrefs = [item.href for item in items if self.path == item.href]
            for item in items:
                css_class = "active" if item.href in active_hrefs else ""
                if css_class:
                    active_id = item.id
                    active_group = key
                    break

                elif not active_hrefs:
                    if self.path == item.href or (self.path and self.path.startswith(item.href)):
                        css_class = "active"

                    if not css_class and self.active_route == item.id:
                        css_class = "active"

                if css_class:
                    active_group = key
                    active_id = item.id
                    break

        if not active_group:
            active_group = list(self.menu.keys())[0]

        return active_group, active_id

    def create_side(self) -> str:
        """Generate sidebar HTML structure based on menu definitions.

        This method constructs a responsive sidebar with collapsible groups and
        sub-items. It determines the active menu item to highlight it and expand
        its parent group. The generated HTML includes separate structures for
        desktop and mobile views using Bootstrap utility classes.

        Returns:
            str: A string containing the formatted HTML structure of the sidebar.
        """

        # Helper lambda to generate sub-items HTML string using a comprehension
        def build_sub_items(items, active_id) -> str:
            sub_items: list[Any] = []

            for item in items:
                if item.disabled:
                    continue

                css_class = "active" if item.id == active_id else ""

                link = generate_list_item(item)

                sub_items.append(f"<li id='{item.id}' class='{css_class}'>{link}</li>")

            sub_items_str = "".join(sub_items)
            return sub_items_str

        active_group, active_id = self.get_the_active_group_and_sub()

        # Template for the collapsible content (shared by desktop and mobile)
        collapse_tpl = """
            <div class="collapse {show}" id="{group_id}-collapse">
                <div class="d-none d-md-inline">
                    <!-- desktop -->
                    <ul class="btn-toggle-nav list-unstyled fw-normal pb-1 small">
                        {sub_items}
                    </ul>
                </div>
                <div class="d-inline d-md-none">
                    <!-- mobile -->
                    <ul class="navbar-nav flex-row flex-wrap btn-toggle-nav-mobile list-unstyled fw-normal pb-1 small">
                        {sub_items}
                    </ul>
                </div>
            </div>
        """

        sidebar_parts = ["<ul class='list-unstyled'>"]

        for group, items in self.menu.items():
            sub_items_str = build_sub_items(items, active_id)

            if not sub_items_str:
                continue

            group_id = group.lower().replace(" ", "_")

            match group == active_group:
                case True:
                    show, expanded = "show", "true"
                case False:
                    show, expanded = "", "false"

            icon = self.menu_icons.get(group, "")
            icon_tag = f"<i class='bi {icon} me-1'></i>" if icon else ""

            # Formatting the button and the collapse container
            button_html = f"""
                <button class="btn btn-toggle align-items-center rounded"
                        data-bs-toggle="collapse"
                        data-bs-target="#{group_id}-collapse"
                        aria-expanded="{expanded}">
                    {icon_tag}
                    <span class='hide-on-collapse-inline'>{group}</span>
                </button>
            """

            group_container = f"""
                <li class="mb-1">
                    {button_html}
                    {collapse_tpl.format(show=show, group_id=group_id, sub_items=sub_items_str)}
                </li>
                <li class="border-top my-1"></li>"""

            sidebar_parts.append(group_container.strip())

        sidebar_parts.append("</ul>")
        return "\n".join(sidebar_parts)


@functools.lru_cache(maxsize=1)
def load_menu() -> dict[str, list[SidebarItem]]:
    main_menu = {
        "Translations": [
            SidebarItem(
                id="last",
                admin=1,
                href="last",
                title="Recent",
                icon="bi-clock-history",
            ),
            SidebarItem(
                id="process",
                admin=0,
                href="process",
                title="In Process",
                icon="bi-hourglass",
            ),
            SidebarItem(
                id="process_total",
                admin=0,
                href="process_total",
                title="In Process (Total)",
                icon="bi-hourglass-split",
            ),
            SidebarItem(
                id="reports",
                admin=0,
                href="reports",
                title="Publish Reports",
                icon="bi-file-earmark-text",
            ),
        ],
        "Pages": [
            SidebarItem(
                id="tt_load",
                admin=1,
                href="tt",
                title="Translate Type",
                icon="bi-translate",
            ),
            SidebarItem(
                id="translated",
                admin=1,
                href="translated",
                title="Pages",
                icon="bi-check2-square",
            ),
            SidebarItem(
                id="translated_users",
                admin=1,
                href="translated_users",
                title="User Pages",
                icon="bi-check2-circle",
            ),
            SidebarItem(
                id="pages_users_to_main",
                admin=1,
                href="pages_users_to_main",
                title="Pages to check",
                icon="bi-check",
            ),
            SidebarItem(
                id="add",
                admin=1,
                href="add",
                title="Add translations",
                icon="bi-plus-square",
            ),
            SidebarItem(
                id="qidsload",
                admin=1,
                href="qids",
                title="Qids",
                icon="bi-list-ul",
            ),
            SidebarItem(
                id="qids_others",
                admin=1,
                href="qids_others",
                title="Qids Others",
                icon="bi-list-check",
            ),
        ],
        "Users": [
            SidebarItem(
                id="coordinators",
                admin=1,
                href="coordinators",
                title="Coordinators",
                icon="bi-person-gear",
            ),
            SidebarItem(
                id="users_emails",
                admin=1,
                href="users_emails",
                title="Users Emails",
                icon="bi-envelope",
            ),
            SidebarItem(
                id="full_tr",
                admin=1,
                href="full_translators",
                title="Full translators",
                icon="bi-person-check",
            ),
            SidebarItem(
                id="user_inp",
                admin=1,
                href="users_no_inprocess",
                title="Not in process",
                icon="bi-hourglass",
            ),
        ],
        "Others": [
            SidebarItem(
                id="projects",
                admin=1,
                href="projects",
                title="Projects",
                icon="bi-kanban",
            ),
            SidebarItem(
                id="campaigns",
                admin=1,
                href="campaigns",
                title="Campaigns",
                icon="bi-megaphone",
            ),
            SidebarItem(
                id="settings",
                admin=1,
                href="settings",
                title="Settings",
                icon="bi-gear",
            ),
            SidebarItem(
                id="categories",
                admin=0,
                href="categories",
                title="Categories",
                icon="bi-tags",
            ),
        ],
        "Tools": [
            SidebarItem(
                id="stat",
                admin=0,
                href="stat",
                title="Status",
                icon="bi-graph-up",
            ),
            SidebarItem(
                id="language_settings",
                admin=1,
                href="language_settings",
                title="Fix refs (Options)",
                icon="bi-wrench-adjustable",
            ),
            SidebarItem(
                id="fixwikirefs",
                admin=0,
                href="/fixrefs",
                title="Fixwikirefs",
                target="_blank",
                icon="bi-wrench",
            ),
        ],
    }

    return main_menu

def create_side(active_route: str, path: str | None = None) -> str:
    """Generate sidebar HTML structure based on menu definitions."""
    main_menu = load_menu()

    main_menu_icons = {
        "Translations": "bi-translate",
        "Pages": "bi-file-text",
        "Qids": "bi-database",
        "Users": "bi-people",
        "Others": "bi-three-dots",
        "Tools": "bi-tools",
    }

    model = Sidebar(main_menu, main_menu_icons, active_route, path)
    sidebar = model.create_side()

    return sidebar

__all__ = [
    "SidebarItem",
    "generate_list_item",
    "create_side",
]
