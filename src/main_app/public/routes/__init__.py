"""
Flask public routes
"""

from .api.routes import ApiRoutes
from .cxtoken.routes import CxTokenRoutes
from .main import MainRoutes
from .publish.routes import PublishRoutes
from .refs.routes import FixRefsRoutes
from .td import LeaderBoardRoutes, TDRoutes
from .html_to_segments import HtmltoSegmentsRoutes

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
