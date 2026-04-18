import os
import sys

# Add src to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from sqlalchemy_app.shared.sqlalchemy_db.engine import BaseDb, init_db, get_session
from sqlalchemy_app.shared.sqlalchemy_db.models import _PageRecord, _UserPageRecord
from sqlalchemy_app.shared.sqlalchemy_db.services.page_service import (
    find_exists_or_update_page,
    insert_page_target,
)
from sqlalchemy_app.shared.sqlalchemy_db.services.user_page_service import (
    find_exists_or_update_user_page,
    insert_user_page_target,
)

def setup_db():
    init_db("sqlite:///:memory:", create_tables=True)

def test_page_service():
    print("Testing page_service...")
    setup_db()

    # Test insert_page_target
    success = insert_page_target(
        sourcetitle="Source 1",
        tr_type="lead",
        cat="Cat 1",
        lang="en",
        user="User 1",
        target="",
        mdwiki_revid=123,
        word=100
    )
    assert success is True

    with get_session() as session:
        page = session.query(_PageRecord).filter_by(title="Source 1").first()
        assert page is not None
        assert page.target == ""
        assert page.pupdate is not None

    # Test find_exists_or_update_page
    # Should return True because it exists, and update target
    exists = find_exists_or_update_page("Source 1", "en", "User 1", "Target 1")
    assert exists is True

    with get_session() as session:
        page = session.query(_PageRecord).filter_by(title="Source 1").first()
        assert page.target == "Target 1"

    # Test find_exists_or_update_page with non-existent
    exists = find_exists_or_update_page("Non Existent", "en", "User 1", "Target 1")
    assert exists is False

    print("page_service tests passed!")

def test_user_page_service():
    print("Testing user_page_service...")
    setup_db()

    # Test insert_user_page_target
    success = insert_user_page_target(
        sourcetitle="User Source 1",
        tr_type="full",
        cat="Cat 2",
        lang="fr",
        user="User 2",
        target=None,
        mdwiki_revid=456,
        word=200
    )
    assert success is True

    with get_session() as session:
        page = session.query(_UserPageRecord).filter_by(title="User Source 1").first()
        assert page is not None
        assert page.target is None

    # Test find_exists_or_update_user_page
    exists = find_exists_or_update_user_page("User Source 1", "fr", "User 2", "User Target 1")
    assert exists is True

    with get_session() as session:
        page = session.query(_UserPageRecord).filter_by(title="User Source 1").first()
        assert page.target == "User Target 1"

    print("user_page_service tests passed!")

if __name__ == "__main__":
    try:
        test_page_service()
        test_user_page_service()
        print("All migrations verified successfully!")
    except Exception as e:
        print(f"Verification failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
