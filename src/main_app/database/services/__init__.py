"""
Shared db services, used in both admin and public blueprints
"""

from __future__ import annotations

from .analytics import (
    AssessmentService,
    EnwikiPageviewService,
    MdwikiRevidService,
    RefsCountService,
    ViewsNewService,
    WordService,
)
from .config import (
    LanguageSettingService,
    SettingsService,
)
from .content import (
    CategoryService,
    LangService,
    ProjectService,
)
from .pages import (
    InProcessService,
    LeaderboardService,
    MissingStatsService,
    PagesQueryService,
    PagesUsersToMainPagesService,
    Results2026Service,
    TranslateTypeService,
)
from .pages_tables import (
    PagesService,
    UserPagesService,
)
from .reports import (
    PagesUsersToMainService,
    ReportService,
)
from .users import (
    AdminService,
    FullTranslatorService,
    UsersNoInprocessService,
    UsersService,
    UserTokenService,
)
from .wikidata import (
    AllQidsService,
    QidOthersService,
    QidService,
)

__all__ = [
    "Results2026Service",
    "AllQidsService",
    "PagesQueryService",
    "LeaderboardService",
    "MdwikiRevidService",
    "EnwikiPageviewService",
    "AssessmentService",
    "RefsCountService",
    "ViewsNewService",
    "WordService",
    "FullTranslatorService",
    "UsersNoInprocessService",
    "PagesService",
    "ReportService",
    "PagesUsersToMainPagesService",
    "TranslateTypeService",
    "UserPagesService",
    "InProcessService",
    "LangService",
    "ProjectService",
    "PagesUsersToMainService",
    "QidService",
    "QidOthersService",
    "MissingStatsService",
    "CategoryService",
    "AdminService",
    "UsersService",
    "UserTokenService",
    "SettingsService",
    "LanguageSettingService",
]
