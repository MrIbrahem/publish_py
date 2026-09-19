"""
Flask public routes
"""

from __future__ import annotations

from .leaderboard import LeaderBoardRoutes
from .td_route import TDRoutes
from .translate_med import TranslateRoutes

__all__ = [
    "TDRoutes",
    "TranslateRoutes",
    "LeaderBoardRoutes",
]
