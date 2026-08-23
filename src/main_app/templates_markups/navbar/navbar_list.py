""" """

from __future__ import annotations

from .objects import NavLink

nav_list = [
    NavLink(
        text="Leaderboard",
        icon="bi-bar-chart-line",
        url_endpoint="leaderboard.index",
        title="Leaderboard",
        path="/Translation_Dashboard/leaderboard",
    ),
    NavLink(
        text="Prior",
        icon="bi-bar-chart me-1",
        url_endpoint="",
        title="Prior",
        static_url="/prior",
        path="/prior",
        link_target="_blank",
    ),
    NavLink(
        text="Missing",
        icon="bi-card-list",
        url_endpoint="td.missing",
        title="Missing",
        path="/Translation_Dashboard/missing",
    ),
    NavLink(
        text="Fix Refs",
        icon="bi-list-task",
        url_endpoint="fixrefs.index",
        title="Fix Refs",
        path="/fixrefs",
    ),
    NavLink(
        text="Publish Reports",
        icon="bi-list-task",
        url_endpoint="main.reports",
        title="Publish Reports",
        path="/reports",
    ),
    NavLink(
        text="Admins",
        icon="bi-people-fill",
        url_endpoint="adminpanel.index",
        path="/adminpanel",
        for_admin=True,
    ),
    NavLink(
        text="GitHub",
        icon="bi-github",
        static_url="https://github.com/MrIbrahem/mdwiki.toolforge.org",
        link_target="_blank",
        path="",
    ),
]

__all__ = [
    "nav_list",
]
