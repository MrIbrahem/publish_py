
import pytest
from flask.testing import FlaskClient

def test_security_headers_on_main_page(client: FlaskClient):
    """Test that security headers are present on the main page."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.headers.get("X-Frame-Options") == "SAMEORIGIN"
    assert response.headers.get("X-Content-Type-Options") == "nosniff"
    assert response.headers.get("Referrer-Policy") == "strict-origin-when-cross-origin"

def test_security_headers_on_api_endpoint(client: FlaskClient, mock_is_allowed_medwiki):
    """Test that security headers are present on an API endpoint."""
    # We use mock_is_allowed_medwiki to bypass CORS check for the API
    response = client.get("/api/publish_reports")
    # It might return 200 or something else depending on DB state,
    # but the headers should be there anyway.
    assert response.headers.get("X-Frame-Options") == "SAMEORIGIN"
    assert response.headers.get("X-Content-Type-Options") == "nosniff"
    assert response.headers.get("Referrer-Policy") == "strict-origin-when-cross-origin"

def test_security_headers_on_admin_page(client: FlaskClient, mock_admin_required):
    """Test that security headers are present on an admin page."""
    # Use mock_admin_required to bypass admin checks
    response = client.get("/admin/")
    # /admin/ redirects to /admin/last
    assert response.status_code == 302
    assert response.headers.get("X-Frame-Options") == "SAMEORIGIN"
    assert response.headers.get("X-Content-Type-Options") == "nosniff"
    assert response.headers.get("Referrer-Policy") == "strict-origin-when-cross-origin"

    # Check the redirected page
    response = client.get("/admin/last")
    assert response.headers.get("X-Frame-Options") == "SAMEORIGIN"
    assert response.headers.get("X-Content-Type-Options") == "nosniff"
    assert response.headers.get("Referrer-Policy") == "strict-origin-when-cross-origin"
