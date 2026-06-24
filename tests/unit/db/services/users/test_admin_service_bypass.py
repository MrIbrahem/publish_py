import pytest
from src.main_app.config import DevelopmentConfig, ProductionConfig
from src.main_app.db.services.users.admin_service import active_coordinators, is_active_coordinator
from src.main_app.db.services.users.bypass_service import should_bypass_coordinator_check
from src.main_app.shared.auth.identity import current_user


def test_bypass_never_active_under_production(app):
    """Ensure bypass is NEVER active under ProductionConfig."""
    # We can't easily change the app's config class after it's created,
    # but we can simulate the ProductionConfig environment.
    app.config["IS_DEVELOPMENT_CONFIG"] = False
    app.config["UI_TEST_BYPASS_COORDINATOR_CHECK"] = True  # simulated leaked env var

    with app.test_request_context():
        assert should_bypass_coordinator_check("nonexistent-user") is False
        assert is_active_coordinator("nonexistent-user") is False
        assert current_user() is None


def test_bypass_active_under_development_when_enabled(app):
    """Ensure bypass is active under DevelopmentConfig when enabled."""
    app.config["IS_DEVELOPMENT_CONFIG"] = True
    app.config["UI_TEST_BYPASS_COORDINATOR_CHECK"] = True

    with app.test_request_context():
        assert should_bypass_coordinator_check("nonexistent-user") is True
        assert is_active_coordinator("any-user") is True
        assert "BYPASS_ADMIN" in active_coordinators()
        user = current_user()
        assert user is not None
        assert user.username == "BYPASS_ADMIN"


def test_bypass_disabled_by_default_under_development(app):
    """Ensure bypass is disabled by default even under DevelopmentConfig."""
    app.config["IS_DEVELOPMENT_CONFIG"] = True
    app.config["UI_TEST_BYPASS_COORDINATOR_CHECK"] = False

    with app.test_request_context():
        assert should_bypass_coordinator_check("nonexistent-user") is False
        assert is_active_coordinator("nonexistent-user") is False
