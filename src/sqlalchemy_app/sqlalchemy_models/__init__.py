from .setting import (
    LanguageSettingRecord,
    SettingRecord,
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
from .qid import (
    QidRecord,
)

from .dashboard import (
    CategoryRecord,
    ProjectRecord,
)

from .publish import ReportRecord

from .user import (
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
