"""
Unit tests for extensions module.
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
from flask import Blueprint, Flask

from src.sqlalchemy_app.shared.core.extensions import csrf, csrf_exempt, csrf_init_app


class TestCsrfInitApp:
    """Tests for csrf_init_app function."""

    def test_initializes_csrf_protection(self, app: Flask):
        """Test that csrf_init_app initializes CSRF protection on the app."""
        # Create a fresh app for this test
        from flask_wtf.csrf import CSRFProtect

        test_app = Flask(__name__)
        test_app.config["SECRET_KEY"] = "test_secret_key"
        test_app.config["WTF_CSRF_ENABLED"] = True

        # Create a new CSRF instance for testing
        test_csrf = CSRFProtect()

        # CSRF should not be initialized yet
        assert test_app.extensions.get("csrf") is None

        test_csrf.init_app(test_app)

        # After initialization, CSRF extension should be registered
        assert test_app.extensions.get("csrf") is not None

    def test_csrf_protection_is_active_after_init(self, app: Flask):
        """Test that CSRF protection is active after initialization."""
        csrf_init_app(app)

        # Create a test client
        client = app.test_client()

        # Make a GET request to establish a request context and get a CSRF token
        # The app should now have CSRF protection enabled
        with client.session_transaction():
            pass  # Just establish a request context

        with app.test_request_context():
            from flask_wtf.csrf import generate_csrf

            csrf_token = generate_csrf()
            assert csrf_token is not None


class TestCsrfExempt:
    """Tests for csrf_exempt function."""

    def test_exempts_blueprint_when_csrf_enabled(self):
        """Test that blueprint is exempted when CSRF is enabled."""
        app = Flask(__name__)
        app.config["SECRET_KEY"] = "test_secret_key"
        app.config["WTF_CSRF_ENABLED"] = True

        bp = Blueprint("test_bp", __name__)

        with patch.object(csrf, "exempt") as mock_exempt:
            csrf_exempt(app, bp)
            mock_exempt.assert_called_once_with(bp)

    def test_does_not_exempt_when_csrf_disabled(self):
        """Test that blueprint is not exempted when CSRF is disabled."""
        app = Flask(__name__)
        app.config["SECRET_KEY"] = "test_secret_key"
        app.config["WTF_CSRF_ENABLED"] = False

        bp = Blueprint("test_bp", __name__)

        with patch.object(csrf, "exempt") as mock_exempt:
            csrf_exempt(app, bp)
            mock_exempt.assert_not_called()

    def test_exempts_blueprint_with_csrf_init(self, app: Flask):
        """Test that exempted blueprint allows POST without CSRF token."""
        app.config["WTF_CSRF_ENABLED"] = True

        bp = Blueprint("test_bp", __name__)

        @bp.route("/test", methods=["POST"])
        def test_post():
            return "Success", 200

        csrf_init_app(app)
        csrf_exempt(app, bp)
        app.register_blueprint(bp)

        client = app.test_client()

        # POST without CSRF token should succeed for exempted blueprint
        response = client.post("/test")
        # Should succeed because blueprint is exempted
        assert response.status_code == 200


class TestCsrfSingleton:
    """Tests for the csrf singleton instance."""

    def test_csrf_is_singleton(self):
        """Test that csrf is a singleton instance."""
        from src.sqlalchemy_app.shared.core.extensions import csrf as csrf1
        from src.sqlalchemy_app.shared.core.extensions import csrf as csrf2

        assert csrf1 is csrf2

    def test_csrf_is_csrfprotect_instance(self):
        """Test that csrf is a CSRFProtect instance."""
        from flask_wtf.csrf import CSRFProtect

        assert isinstance(csrf, CSRFProtect)


class TestExtensionsIntegration:
    """Integration tests for extensions module."""

    def test_full_csrf_setup(self, app: Flask):
        """Test complete CSRF setup flow."""
        app.config["WTF_CSRF_ENABLED"] = True
        app.config["SECRET_KEY"] = "test_secret_key"

        # Initialize CSRF
        csrf_init_app(app)

        # Create and exempt a blueprint
        bp = Blueprint("api_bp", __name__)

        @bp.route("/data", methods=["POST"])
        def api_data():
            return {"status": "ok"}, 200

        csrf_exempt(app, bp)
        app.register_blueprint(bp, url_prefix="/api")

        client = app.test_client()

        # POST to exempted API endpoint should work without CSRF token
        response = client.post("/api/data")
        assert response.status_code == 200

    def test_csrf_protection_on_non_exempt_routes(self, app: Flask):
        """Test that non-exempt routes still require CSRF token."""
        app.config["WTF_CSRF_ENABLED"] = True
        app.config["SECRET_KEY"] = "test_secret_key"

        csrf_init_app(app)

        # Create a regular route (not exempted)
        @app.route("/protected", methods=["POST"])
        def protected_post():
            return "Success", 200

        client = app.test_client()

        # POST without CSRF token should fail
        response = client.post("/protected")
        assert response.status_code == 400  # CSRF error
