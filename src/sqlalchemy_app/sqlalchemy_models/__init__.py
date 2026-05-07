from .dashboard import (
    CategoryRecord,
    ProjectRecord,
)
from .metrics import (
    AssessmentRecord,
    RefsCountRecord,
    WordRecord,
)
from .pages import (
    InProcessRecord,
    PageRecord,
    PagesUsersToMainRecord,
    UserPageRecord,
)
from .public import (
    LangRecord,
    MdwikiRevidRecord,
    TranslateTypeRecord,
)
from .publish import ReportRecord
from .all_articles import AllArticlesRecord
from .qid import (
    AllQidsExistRecord,
    AllQidsRecord,
    QidRecord,
)
from .setting import (
    LanguageSettingRecord,
    SettingRecord,
)
from .users import (
    CoordinatorRecord,
    FullTranslatorRecord,
    UserRecord,
    UsersNoInprocessRecord,
    UserTokenRecord,
)
from .views import (
    EnwikiPageviewRecord,
    ViewsNewAllRecord,
    ViewsNewRecord,
)

__all__ = [
    "AllArticlesRecord",
    "AllQidsExistRecord",
    "AllQidsRecord",
    "AssessmentRecord",
    "CategoryRecord",
    "CoordinatorRecord",
    "EnwikiPageviewRecord",
    "FullTranslatorRecord",
    "InProcessRecord",
    "LangRecord",
    "LanguageSettingRecord",
    "MdwikiRevidRecord",
    "PageRecord",
    "PagesUsersToMainRecord",
    "ProjectRecord",
    "QidRecord",
    "RefsCountRecord",
    "ReportRecord",
    "SettingRecord",
    "TranslateTypeRecord",
    "UserPageRecord",
    "UserRecord",
    "UsersNoInprocessRecord",
    "UserTokenRecord",
    "ViewsNewAllRecord",
    "ViewsNewRecord",
    "WordRecord",
]
