"""Utility modules for the main application."""

from __future__ import annotations

from .mapping import NavDropdown, NavLink
from .nav_bar import NavigationBar
from .td_navbar_list import td_nav_list

td_navbar = NavigationBar(td_nav_list)

__all__ = [
    "td_navbar",
    "NavigationBar",
    "NavLink",
    "NavDropdown",
]
