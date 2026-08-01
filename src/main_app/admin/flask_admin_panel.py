"""Admin blueprint package."""

from dataclasses import dataclass, field
from typing import Any

from flask import Flask
from flask_admin import Admin, AdminIndexView  # , BaseView, expose
from flask_admin.contrib.sqla import ModelView
from flask_admin.theme import Bootstrap4Theme
from flask_babel import Babel

from ..db.models.dashboard import (
    CategoryRecord,
    ProjectRecord,
)
from ..db.models.metrics import (
    AssessmentRecord,
    RefsCountRecord,
    WordRecord,
)
from ..db.models.pages import (
    InProcessRecord,
    PageRecord,
    PagesUsersToMainRecord,
    UserPageRecord,
)
from ..db.models.public import (
    LangRecord,
    MdwikiRevidRecord,
    TranslateTypeRecord,
)
from ..db.models.publish import ReportRecord
from ..db.models.qid import (
    AllQidsExistRecord,
    QidOthersRecord,
    QidRecord,
)
from ..db.models.setting import (
    LanguageSettingRecord,
    SettingRecord,
)
from ..db.models.users import (
    AdminUserRecord,
    FullTranslatorRecord,
    UserRecord,
    UsersNoInprocessRecord,
)
from ..db.models.views import (
    EnwikiPageviewRecord,
    ViewsNewAllRecord,
    ViewsNewRecord,
)


@dataclass
class AdminCategory:
    name: str
    icon_value: str
    records: list[Any] = field(default_factory=list)
    icon_type: str = "fa"
    class_name: Any = None


categories: list[AdminCategory] = [
    AdminCategory(
        name="Dashboard",
        icon_value="fa-tachometer-alt",
        records=[
            CategoryRecord,
            ProjectRecord,
        ],
    ),
    AdminCategory(
        name="Metrics",
        icon_value="fa-chart-bar",
        records=[
            AssessmentRecord,
            RefsCountRecord,
            WordRecord,
        ],
    ),
    AdminCategory(
        name="Pages",
        icon_value="fa-file-alt",
        records=[
            InProcessRecord,
            PageRecord,
            PagesUsersToMainRecord,
            UserPageRecord,
        ],
    ),
    AdminCategory(
        name="QIDs",
        icon_value="fa-database",
        records=[
            AllQidsExistRecord,
            QidOthersRecord,
            QidRecord,
        ],
    ),
    AdminCategory(
        name="Users",
        icon_value="fa-users",
        records=[
            AdminUserRecord,
            FullTranslatorRecord,
            UserRecord,
            UsersNoInprocessRecord,
        ],
    ),
    AdminCategory(
        name="Views",
        icon_value="fa-eye",
        records=[
            EnwikiPageviewRecord,
            ViewsNewAllRecord,
            ViewsNewRecord,
        ],
    ),
    AdminCategory(
        name="Public",
        icon_value="fa-globe",
        records=[
            LangRecord,
            MdwikiRevidRecord,
            TranslateTypeRecord,
        ],
    ),
    AdminCategory(
        name="Settings",
        icon_value="fa-cog",
        records=[
            LanguageSettingRecord,
            SettingRecord,
        ],
    ),
]


class WrapModelView(ModelView):
    ignore_hidden = True
    form_excluded_columns = ("created_at", "updated_at", "token")
    column_display_actions: bool = True
    action_disallowed_list = ["delete"]
    page_size: int = 50
    # edit_modal: bool = True
    # create_modal: bool = True
    can_edit: bool = True
    can_delete: bool = False
    can_view_details: bool = True


def add_admin_dashboard(app: Flask, _db) -> None:
    babel = Babel(app)  # pyright: ignore
    # Initialize Admin and add views
    theme = Bootstrap4Theme(
        base_template="admin/index_with_sidebar.html",
        swatch="default",
        fluid=True,
    )

    admin = Admin(
        app,
        name="DB admin",
        theme=theme,
        endpoint=None,
        index_view=AdminIndexView(
            name="DB admin", template="admin/index_with_sidebar.html", url="/adminpanel/db_admin"
        ),
    )

    admin.add_view(WrapModelView(ReportRecord, _db))

    # register all models
    for cat in categories:
        admin.add_category(
            name=cat.name,
            class_name=cat.class_name,
            icon_type=cat.icon_type,
            icon_value=cat.icon_value,
        )
        views = [WrapModelView(model, _db, category=cat.name) for model in cat.records]
        admin.add_views(*views)


__all__ = [
    "add_admin_dashboard",
]
