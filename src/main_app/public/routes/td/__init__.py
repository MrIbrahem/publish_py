"""
Flask public routes
"""

from .leaderboard import LeaderBoardRoutes
from .td_route import TDRoutes

__all__ = [
    "TDRoutes",
    "LeaderBoardRoutes",
]
