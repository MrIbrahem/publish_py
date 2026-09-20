"""Utility modules for the main application."""

from __future__ import annotations

from .mapping import NavDropdown, NavLink
from .nav_bar import NavigationBar
from .navbar_list import nav_list

td_navbar = NavigationBar(nav_list)

__all__ = [
    "td_navbar",
    "NavigationBar",
    "NavLink",
    "NavDropdown",
]
