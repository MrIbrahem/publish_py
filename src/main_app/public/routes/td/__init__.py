"""
Flask public routes
"""

from __future__ import annotations

from .leaderboard import LeaderBoardRoutes
from .td_route import TDRoutes

__all__ = [
    "TDRoutes",
    "LeaderBoardRoutes",
]
