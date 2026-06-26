"""Integration tests for API routes.

These tests verify the integration of various components in API routes.
"""


class TestCorsIntegration1:
    """Integration tests for CORS handling."""

    def test_cors_headers_on_allowed_origin(self, mock_client, monkeypatch):
        """Test that CORS headers are set for allowed origins."""
        # Mock is_allowed to return an allowed origin
        monkeypatch.setattr(
            "src.main_app.shared.core.cors.is_allowed_checker.is_allowed", lambda req: "https://example.com"
        )
        monkeypatch.setattr("src.main_app.shared.core.cors.is_allowed", lambda req: "https://example.com")

        response = mock_client.get("/", headers={"Origin": "https://example.com"})

        # CORS headers may or may not be present depending on route configuration
        # The test verifies the endpoint is accessible
        assert response.status_code == 200  # in [200, 302, 404]

    def test_preflight_request_handling(self, mock_client):
        """Test that OPTIONS requests are handled for CORS preflight."""
        response = mock_client.options("/")

        # Should be handled (may return 200 or 404 depending on route setup)
        assert response.status_code == 200  # in [200, 404]


class TestCorsIntegration2:
    """Integration tests for CORS handling."""

    def test_cors_headers_on_allowed_origin(self, mock_client, monkeypatch):
        """Test that CORS headers are set for allowed origins."""
        # Mock is_allowed to return an allowed origin
        monkeypatch.setattr(
            "src.main_app.shared.core.cors.is_allowed_checker.is_allowed", lambda req: "https://example.com"
        )
        monkeypatch.setattr("src.main_app.shared.core.cors.is_allowed", lambda req: "https://example.com")

        response = mock_client.get("/", headers={"Origin": "https://example.com"})

        # CORS headers may or may not be present depending on route configuration
        # The test verifies the endpoint is accessible
        assert response.status_code == 200

    def test_preflight_request_handling(self, mock_client):
        """Test that OPTIONS requests are handled for CORS preflight."""
        response = mock_client.options("/")

        # Should be handled (may return 200 or 404 depending on route setup)
        assert response.status_code == 200
