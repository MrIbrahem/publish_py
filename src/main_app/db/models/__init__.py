from .all_articles import AllArticlesRecord
from .category_members import CategoryMemberRecord
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
from .qid import (
    AllQidsExistRecord,
    QidOthersRecord,
    QidRecord,
)
from .setting import (
    LanguageSettingRecord,
    SettingRecord,
)
from .users import (
    AdminUserRecord,
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
    "AssessmentRecord",
    "CategoryMemberRecord",
    "CategoryRecord",
    "AdminUserRecord",
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
    "QidOthersRecord",
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
