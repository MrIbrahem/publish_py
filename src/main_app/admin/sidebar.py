from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

from flask import has_request_context, url_for

logger = logging.getLogger(__name__)


def _safe_url_for(endpoint: str, fallback: str, **values) -> str:
    if has_request_context():
        return url_for(endpoint, **values)
    return fallback


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


def create_side(active_route: str, path: str | None = None) -> str:
    """Generate sidebar HTML structure based on menu definitions."""
    main_menu_icons = {
        "Translations": "bi-translate",
        "Pages": "bi-file-text",
        "Qids": "bi-database",
        "Users": "bi-people",
        "Others": "bi-three-dots",
        "Tools": "bi-tools",
    }

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

    sidebar = ["<ul class='list-unstyled'>"]

    # logger.debug(f"Generating sidebar for active_route='{active_route}'")

    for key, items in main_menu.items():
        lis: list[Any] = []
        group_is_active = False
        key_id = key.lower().replace(" ", "_")
        css_class_full = [item.href for item in items if path == item.href]

        for item in items:
            if item.disabled:
                continue

            css_class = "active" if item.href in css_class_full else ""

            if not css_class_full:
                if path == item.href or (path and path.startswith(item.href)):
                    css_class = "active"

                if not css_class and active_route == item.id:
                    css_class = "active"

            link = generate_list_item(item)

            lis.append(f"<li id='{item.id}' class='{css_class}'>{link}</li>")
            if css_class:
                group_is_active = True

        if lis:
            show = "show" if group_is_active else ""
            expanded = "true" if group_is_active else "false"
            icon = main_menu_icons.get(key, "")
            icon_tag = f"<i class='bi {icon} me-1'></i>" if icon else ""

            group_html = f"""
                <li class="mb-1">
                    <button class="btn btn-toggle align-items-center rounded"
                            data-bs-toggle="collapse"
                            data-bs-target="#{key_id}-collapse"
                            aria-expanded="{expanded}">
                        {icon_tag}
                        <span class='hide-on-collapse-inline'>{key}</span>
                    </button>
                    <div class="collapse {show}" id="{key_id}-collapse">
                        <div class="d-none d-md-inline">
                            <!-- desktop -->
                            <ul class="btn-toggle-nav list-unstyled fw-normal pb-1 small">
                                {"".join(lis)}
                            </ul>
                        </div>
                        <div class="d-inline d-md-none">
                            <!-- mobile -->
                            <ul class="navbar-nav flex-row flex-wrap btn-toggle-nav-mobile list-unstyled fw-normal pb-1 small">
                                {"".join(lis)}
                            </ul>
                        </div>
                    </div>
                </li>
                <li class="border-top my-1"></li>
            """
            sidebar.append(group_html.strip())

    sidebar.append("</ul>")
    return "\n".join(sidebar)


__all__ = [
    "SidebarItem",
    "generate_list_item",
    "create_side",
]
