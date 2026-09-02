"""
Flask public routes
"""

from .api.routes import ApiRoutes
from .cxtoken.routes import CxTokenRoutes
from .html_to_segments import HtmltoSegmentsRoutes
from .main import MainRoutes
from .publish.routes import PublishRoutes
from .refs.routes import FixRefsRoutes
from .td import LeaderBoardRoutes, TDRoutes

__all__ = [
    "ApiRoutes",
    "MainRoutes",
    "TDRoutes",
    "CxTokenRoutes",
    "PublishRoutes",
    "FixRefsRoutes",
    "LeaderBoardRoutes",
    "HtmltoSegmentsRoutes",
]
