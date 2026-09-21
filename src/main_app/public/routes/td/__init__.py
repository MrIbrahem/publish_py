"""
Flask public routes
"""

from __future__ import annotations

from .leaderboard import LeaderBoardRoutes
from .td_route import TDRoutes
from .translate_med import TranslateMedView

__all__ = [
    "TDRoutes",
    "TranslateMedView",
    "LeaderBoardRoutes",
]
