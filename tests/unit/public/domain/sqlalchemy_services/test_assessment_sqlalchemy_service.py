from unittest.mock import MagicMock, patch

import pytest
from src.app_main.public.domain.models.assessment import AssessmentRecord, _AssessmentRecord
from src.app_main.public.domain.sqlalchemy_services.assessment_service import (
    add_assessment,
    add_or_update_assessment,
    delete_assessment,
    get_assessment,
    get_assessment_by_title,
    list_assessments,
    update_assessment,
)
from src.app_main.shared.sqlalchemy_db.engine import BaseDb, build_engine, init_db


@pytest.fixture(autouse=True)
def setup_db():
    init_db("sqlite:///:memory:")
    engine = build_engine("sqlite:///:memory:")
    BaseDb.metadata.create_all(engine)
    with patch("src.app_main.shared.sqlalchemy_db.engine._SessionFactory") as mock_session_factory:
        from sqlalchemy.orm import sessionmaker

        Session = sessionmaker(bind=engine)
        mock_session_factory.return_value = Session()
        yield


def test_assessment_workflow():
    a = add_assessment("test_page", "High")
    assert a.title == "test_page"
    assert get_assessment(a.id).title == "test_page"
    assert get_assessment_by_title("test_page").id == a.id
    assert any(x.title == "test_page" for x in list_assessments())
    updated = update_assessment(a.id, importance="Low")
    assert updated.importance == "Low"
    a4 = add_or_update_assessment("test_page", "Mid")
    assert a4.importance == "Mid"
    delete_assessment(a.id)
    assert get_assessment(a.id) is None
