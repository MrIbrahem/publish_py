""" """

from __future__ import annotations

import functools

from .objects import (
    SidebarGroup,
    SidebarItem,
)

# ---------------------------------------------------------------------------
# Menu item builders — small factories to avoid repeating the same
# endpoint/fallback wiring for every dashboard or job-list link.
# ---------------------------------------------------------------------------


def dashboard_item(id_: str, title: str, icon: str, endpoint: str, fallback_href: str) -> SidebarItem:
    """Build a SidebarItem pointing at a regular admin-panel dashboard endpoint."""
    return SidebarItem(id=id_, title=title, icon=icon, endpoint=endpoint, fallback_href=fallback_href)


def job_item(job_type: str, title: str, icon: str, *, disabled: bool = False) -> SidebarItem:
    """Build a SidebarItem pointing at the job-list page for the given job type."""
    return SidebarItem(
        id=job_type,
        title=title,
        icon=icon,
        endpoint="adminpanel.jobs.jobs_list",
        endpoint_kwargs={"job_type": job_type},
        fallback_href=f"/adminpanel/jobs/{job_type}",
        disabled=disabled,
    )


@functools.lru_cache(maxsize=1)
def load_groups_menu() -> list[SidebarGroup]:
    """Build the static sidebar menu structure.

    No Flask request/app context is touched here — URLs are resolved lazily
    by `SidebarItem.resolve_href()` at render time — so this result is safe
    to cache for the lifetime of the process.
    """
    translations = SidebarGroup(
        id="translations",
        title="Translations",
        icon="bi-translate",
        items=[
            SidebarItem(
                id="last",
                requires_admin=True,
                fallback_href="/adminpanel/last",
                title="Recent",
                icon="bi-clock-history",
            ),
            SidebarItem(
                id="process",
                requires_admin=False,
                fallback_href="/adminpanel/process",
                title="In Process",
                icon="bi-hourglass",
            ),
            SidebarItem(
                id="process_total",
                requires_admin=False,
                fallback_href="/adminpanel/process_total",
                title="In Process (Total)",
                icon="bi-hourglass-split",
            ),
            SidebarItem(
                id="reports",
                requires_admin=False,
                fallback_href="/adminpanel/reports",
                title="Publish Reports",
                icon="bi-file-earmark-text",
            ),
        ],
    )

    pages = SidebarGroup(
        id="pages",
        title="Pages",
        icon="bi-file-text",
        items=[
            SidebarItem(
                id="tt_load",
                requires_admin=True,
                fallback_href="/adminpanel/tt",
                title="Translate Type",
                icon="bi-translate",
            ),
            SidebarItem(
                id="translated",
                requires_admin=True,
                fallback_href="/adminpanel/translated",
                title="Pages",
                icon="bi-check2-square",
            ),
            SidebarItem(
                id="translated_users",
                requires_admin=True,
                fallback_href="/adminpanel/translated_users",
                title="User Pages",
                icon="bi-check2-circle",
            ),
            SidebarItem(
                id="pages_users_to_main",
                requires_admin=True,
                fallback_href="/adminpanel/pages_users_to_main",
                title="Pages to check",
                icon="bi-check",
            ),
            SidebarItem(
                id="add",
                requires_admin=True,
                fallback_href="/adminpanel/add",
                title="Add translations",
                icon="bi-plus-square",
            ),
            SidebarItem(
                id="qidsload",
                requires_admin=True,
                fallback_href="/adminpanel/qids",
                title="Qids",
                icon="bi-list-ul",
            ),
            SidebarItem(
                id="qids_others",
                requires_admin=True,
                fallback_href="/adminpanel/qids_others",
                title="Qids Others",
                icon="bi-list-check",
            ),
        ],
    )

    users = SidebarGroup(
        id="users",
        title="Users",
        icon="bi-people",
        items=[
            SidebarItem(
                id="coordinators",
                requires_admin=True,
                fallback_href="/adminpanel/coordinators",
                title="Coordinators",
                icon="bi-person-gear",
            ),
            SidebarItem(
                id="users_emails",
                requires_admin=True,
                fallback_href="/adminpanel/users_emails",
                title="Users Emails",
                icon="bi-envelope",
            ),
            SidebarItem(
                id="full_tr",
                requires_admin=True,
                fallback_href="/adminpanel/full_translators",
                title="Full translators",
                icon="bi-person-check",
            ),
            SidebarItem(
                id="user_inp",
                requires_admin=True,
                fallback_href="/adminpanel/users_no_inprocess",
                title="Not in process",
                icon="bi-hourglass",
            ),
        ],
    )

    others = SidebarGroup(
        id="others",
        title="Others",
        icon="bi-three-dots",
        items=[
            SidebarItem(
                id="projects",
                requires_admin=True,
                fallback_href="/adminpanel/projects",
                title="Projects",
                icon="bi-kanban",
            ),
            SidebarItem(
                id="campaigns",
                requires_admin=True,
                fallback_href="/adminpanel/campaigns",
                title="Campaigns",
                icon="bi-megaphone",
            ),
            SidebarItem(
                id="settings",
                requires_admin=True,
                fallback_href="/adminpanel/settings",
                title="Settings",
                icon="bi-gear",
            ),
            SidebarItem(
                id="categories",
                requires_admin=False,
                fallback_href="/adminpanel/categories",
                title="Categories",
                icon="bi-tags",
            ),
            SidebarItem(
                id="errors",
                requires_admin=True,
                fallback_href="/adminpanel/errors",
                title="App Errors",
                icon="bi-exclamation-triangle",
            ),
        ],
    )

    tools = SidebarGroup(
        id="tools",
        title="Tools",
        icon="bi-tools",
        items=[
            SidebarItem(
                id="stat",
                requires_admin=False,
                fallback_href="/adminpanel/stat",
                title="Status",
                icon="bi-graph-up",
            ),
            SidebarItem(
                id="language_settings",
                requires_admin=True,
                fallback_href="/adminpanel/language_settings",
                title="Fix refs (Options)",
                icon="bi-wrench-adjustable",
            ),
            SidebarItem(
                id="fixwikirefs",
                requires_admin=False,
                fallback_href="/adminpanel//fixrefs",
                title="Fixwikirefs",
                link_target="_blank",
                icon="bi-wrench",
            ),
            SidebarItem(
                id="db_admin",
                requires_admin=True,
                fallback_href="/adminpanel/db_admin",
                title="DB admin",
                icon="bi-database",
            ),
        ],
    )

    return [
        translations,
        pages,
        users,
        others,
        tools,
    ]


__all__ = [
    "load_groups_menu",
]
