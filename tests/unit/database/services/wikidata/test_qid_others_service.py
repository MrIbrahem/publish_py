"""
Unit tests for the ``qid_others_service`` admin helpers.
"""

import pytest
from flask_sqlalchemy.extension import SQLAlchemy

from src.main_app.database.services.wikidata.qid_others_service import (
    QidOthersService,
)
from tests.unit.database.services.wikidata.qids_services_tests import (
    AddQidTest,
    DeleteQidTest,
    GetByQidTest,
    GetByTitleTest,
    GetPageQidTest,
    GetTitleToQidTest,
    InsertTest,
    ListQidsByDisTest,
    ListQidsTest,
    QidAndQidOthersServiceTest,
    UpdateQidTest,
)

pytestmark = pytest.mark.unit


class TestSetup:
    @pytest.fixture(autouse=True)
    def setup(self, sqlite_db: SQLAlchemy) -> None:
        self.service = QidOthersService()
        self.sqlite_db = sqlite_db


class TestQidAndQidOthersService(QidAndQidOthersServiceTest, TestSetup):
    """Tests for `QidService/QidOthersService` class."""


class TestGetPageQid(GetPageQidTest, TestSetup):
    """Tests for get_by_title function."""


class TestAddQid(AddQidTest, TestSetup):
    """Tests for add_or_update function."""


class TestUpdateQid(UpdateQidTest, TestSetup):
    """Tests for update_qid function."""


class TestDeleteQid(DeleteQidTest, TestSetup):
    """Tests for delete function."""


class TestListQids(ListQidsTest, TestSetup):
    """Tests for list_records function."""


class TestGetTitleToQid(GetTitleToQidTest, TestSetup):
    """Tests for get_title_to_qid function."""


class TestListQidsByDis(ListQidsByDisTest, TestSetup):
    """
    Tests for the ``dis`` filter on list_records.
    """


class TestGetByQid(GetByQidTest, TestSetup):
    """Tests for get_by_qid."""


class TestGetByTitle(GetByTitleTest, TestSetup):
    """Tests for get_by_title."""


class TestInsert(InsertTest, TestSetup):
    """Tests for the insert helper used by the admin/qids POST handler."""
