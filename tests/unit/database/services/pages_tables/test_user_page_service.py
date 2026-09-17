import pytest

# from src.main_app.database.models import UserPageRecord
from src.main_app.database.services import (
    UserPagesService,
)
from tests.unit.database.services.pages_tables.pages_shared_service_tests import (
    AddPageTests,
    CountTranslatedTests,
    DeletePageTests,
    GetByIdTests,
    InsertPageTargetTests,
    ListTranslatedTests,
    PagesAndUserPagesServiceTests,
    UpdatePageTests,
)

pytestmark = pytest.mark.unit


class TestSetup:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.service = UserPagesService()


class TestPagesAndUserPagesService(PagesAndUserPagesServiceTests, TestSetup):
    """Tests for PagesService/UserPagesService class."""


class TestAddPage(AddPageTests, TestSetup):
    """Tests for add_page function."""


class TestUpdatePage(UpdatePageTests, TestSetup):
    """Tests for update_page function."""


class TestDeletePage(DeletePageTests, TestSetup):
    """Tests for delete_page function."""


class TestInsertPageTarget(InsertPageTargetTests, TestSetup):
    """Tests for insert_page_target function."""


# ---------------------------------------------------------------------------
# Tests for new service functions added with the admin/translated work:
#   - self.service.list_translated(lang, limit, offset)
#   - self.service.count_translated(lang)
#   - self.service.get_by_id(page_id)
# ---------------------------------------------------------------------------


class TestListTranslated(ListTranslatedTests, TestSetup):
    """Tests for list_translated."""


class TestCountTranslated(CountTranslatedTests, TestSetup):
    """Tests for count_translated."""


class TestGetById(GetByIdTests, TestSetup):
    """Tests for get_by_id."""
