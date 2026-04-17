import pytest
from unittest.mock import MagicMock, patch
from src.app_main.shared.sqlalchemy_db.engine import init_db, build_engine, BaseDb
from src.app_main.public.domain.sqlalchemy_services.assessment_service import (
    list_assessments,
    get_assessment,
    get_assessment_by_title,
    add_assessment,
    add_or_update_assessment,
    update_assessment,
    delete_assessment
)
from src.app_main.public.domain.models.assessment import AssessmentRecord, _AssessmentRecord

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
    # Test add
    a = add_assessment("test_page", "High")
    assert a.title == "test_page"
    assert a.importance == "High"

    # Test get
    a2 = get_assessment(a.id)
    assert a2.title == "test_page"

    # Test get by title
    a3 = get_assessment_by_title("test_page")
    assert a3.id == a.id

    # Test list
    all_a = list_assessments()
    assert any(x.title == "test_page" for x in all_a)

    # Test update
    updated = update_assessment(a.id, importance="Low")
    assert updated.importance == "Low"

    # Test add_or_update
    a4 = add_or_update_assessment("test_page", "Mid")
    assert a4.importance == "Mid"

    # Test delete
    delete_assessment(a.id)
    assert get_assessment(a.id) is None
