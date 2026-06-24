"""
Flask public routes
"""

from flask import Blueprint

from .leaderboard import bp_leaderboard
from .td_route import bp_td


def register_td_blueprints(bp_td: Blueprint) -> None:
    bp_td.register_blueprint(bp_leaderboard)


register_td_blueprints(bp_td)


__all__ = [
    "bp_td",
]
