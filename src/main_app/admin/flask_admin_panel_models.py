"""Admin blueprint package."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from ..database.models.dashboard import (
    CategoryRecord,
    ProjectRecord,
)
from ..database.models.metrics import (
    AssessmentRecord,
    RefsCountRecord,
    WordRecord,
)
from ..database.models.pages import (
    InProcessRecord,
    PageRecord,
    PagesUsersToMainRecord,
    UserPageRecord,
)
from ..database.models.public import (
    LangRecord,
    MdwikiRevidRecord,
    TranslateTypeRecord,
)
from ..database.models.publish import ReportRecord
from ..database.models.qid import (
    AllQidsExistRecord,
    QidOthersRecord,
    QidRecord,
)
from ..database.models.setting import (
    LanguageSettingRecord,
    SettingRecord,
)
from ..database.models.users import (
    AdminUserRecord,
    FullTranslatorRecord,
    UserRecord,
    UsersNoInprocessRecord,
)
from ..database.models.views import (
    EnwikiPageviewRecord,
    ViewsNewAllRecord,
    ViewsNewRecord,
)


# 1. Dataclass to represent individual models with optional parameters like custom names
@dataclass
class ModelItem:
    model: Any
    name: str | None = None


# 2. Dataclass to represent an Admin Category
@dataclass
class AdminCategory:
    name: str | None  # None for uncategorized/standalone models
    icon_value: str = "fa-folder"
    models: list[Any] = field(default_factory=list)  # Accepts a raw model or a ModelItem instance
    icon_type: str = "fa"
    class_name: Any = None


# 3. Primary categories configuration
categories: list[AdminCategory] = [
    AdminCategory(
        name="Dashboard",
        icon_value="fa-tachometer-alt",
        models=[
            CategoryRecord,
            ProjectRecord,
        ],
    ),
    AdminCategory(
        name="Metrics",
        icon_value="fa-chart-bar",
        models=[
            AssessmentRecord,
            RefsCountRecord,
            WordRecord,
        ],
    ),
    AdminCategory(
        name="Pages",
        icon_value="fa-file-alt",
        models=[
            InProcessRecord,
            PageRecord,
            PagesUsersToMainRecord,
            UserPageRecord,
        ],
    ),
    AdminCategory(
        name="QIDs",
        icon_value="fa-database",
        models=[
            AllQidsExistRecord,
            QidOthersRecord,
            QidRecord,
        ],
    ),
    AdminCategory(
        name="Users",
        icon_value="fa-users",
        models=[
            AdminUserRecord,
            FullTranslatorRecord,
            UserRecord,
            UsersNoInprocessRecord,
        ],
    ),
    AdminCategory(
        name="Views",
        icon_value="fa-eye",
        models=[
            EnwikiPageviewRecord,
            ViewsNewAllRecord,
            ViewsNewRecord,
        ],
    ),
    AdminCategory(
        name="Public",
        icon_value="fa-globe",
        models=[
            LangRecord,
            MdwikiRevidRecord,
            TranslateTypeRecord,
        ],
    ),
    AdminCategory(
        name="Settings",
        icon_value="fa-cog",
        models=[
            LanguageSettingRecord,
            SettingRecord,
        ],
    ),
    # Standalone category for models without a specific category group
    AdminCategory(
        name=None,
        models=[
            ReportRecord,
        ],
    ),
]

__all__ = [
    "categories",
    "ModelItem",
]
