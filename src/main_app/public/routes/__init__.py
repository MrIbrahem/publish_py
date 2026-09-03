"""
Flask public routes
"""

from __future__ import annotations

from .api.routes import ApiRoutes
from .cxtoken.routes import CxTokenRoutes
from .html_to_segments import HtmltoSegmentsRoutes
from .main import MainRoutes
from .new_html import NewHtmlRoutes
from .publish.routes import PublishRoutes
from .refs.routes import FixRefsRoutes
from .td import LeaderBoardRoutes, TDRoutes

__all__ = [
    "NewHtmlRoutes",
    "ApiRoutes",
    "MainRoutes",
    "TDRoutes",
    "CxTokenRoutes",
    "PublishRoutes",
    "FixRefsRoutes",
    "LeaderBoardRoutes",
    "HtmltoSegmentsRoutes",
]
