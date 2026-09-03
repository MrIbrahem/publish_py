"""Utility modules for the main application."""

from __future__ import annotations

from .nav_bar import NavigationBar
from .navbar_list import nav_list
from .objects import NavDropdown, NavLink

td_navbar = NavigationBar(nav_list)

__all__ = [
    "td_navbar",
    "NavigationBar",
    "NavLink",
    "NavDropdown",
]
