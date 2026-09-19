"""
Flask public routes
"""

from __future__ import annotations

from .translate import TranslateRoutes
from .leaderboard import LeaderBoardRoutes
from .td_route import TDRoutes

__all__ = [
    "TDRoutes",
    "TranslateRoutes",
    "LeaderBoardRoutes",
]
