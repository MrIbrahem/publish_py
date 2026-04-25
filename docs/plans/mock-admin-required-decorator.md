# Plan: Mock admin_required Decorator in Integration Tests

## Problem Statement

All 6 test files in `tests/integration/admin/routes/` contain a TODO comment: "should mock admin_required decorator". Currently, these tests:

-   Use `client` (unauthenticated) → get 302 redirects to login
-   Use `auth_client` with patched `active_coordinators` → still get 302 because `current_user()` returns `None` (user doesn't exist in test DB)

This results in weak tests that only assert `response.status_code == 302` instead of actually testing route functionality.

## Root Cause

The `auth_client` fixture sets `session["uid"] = 12345`, but `get_user_token(12345)` returns `None` because no corresponding user exists in the test database. The `admin_required` decorator (in `src/sqlalchemy_app/admin/decorators.py`) calls `current_user()` which fails, causing a 302 redirect.

## Solution: Mock the `admin_required` Decorator

Create a fixture that mocks `admin_required` to bypass authentication, allowing tests to focus on route logic.

### Implementation Plan

#### Step 1: Create `tests/integration/admin/routes/conftest.py`

Create a new conftest.py with a fixture that mocks the decorator:

```python
"""Fixtures for admin routes integration tests."""

from unittest.mock import patch

import pytest


@pytest.fixture(autouse=True)
def mock_admin_required():
    """Mock admin_required decorator to bypass authentication checks.

    This fixture automatically applies to all tests in this directory,
    allowing tests to focus on route functionality rather than auth.
    """
    # Mock the decorator to simply return the original function unchanged
    with patch("src.sqlalchemy_app.admin.decorators.admin_required", lambda f: f):
        yield
```

**Key decisions:**

-   `autouse=True`: Automatically applies to all tests in the directory
-   `lambda f: f`: Makes `@admin_required` a no-op

#### Step 2: Update Test Files

For each of the 6 test files, update the tests to:

1. Remove individual `patch("src.sqlalchemy_app.admin.decorators.active_coordinators")` calls
2. Change assertions from `response.status_code == 302` to meaningful assertions

**Files to update:**

-   `test_admin_routes_integration.py`
-   `test_settings_routes_integration.py`
-   `test_coordinators_routes_integration.py`
-   `test_full_translators_routes_integration.py`
-   `test_users_no_inprocess_routes_integration.py`
-   `test_language_settings_routes_integration.py`

**Example transformation:**

Before:

```python
def test_settings_dashboard_lists_settings(self, auth_client: FlaskClient):
    with patch("src.sqlalchemy_app.admin.decorators.active_coordinators") as mock_coords:
        mock_coords.return_value = ["TestUser"]
        with patch("src.sqlalchemy_app.shared.services.setting_service.list_settings") as mock_list:
            mock_setting = MagicMock()
            mock_list.return_value = [mock_setting]
            response = auth_client.get("/admin/settings")
            assert response.status_code == 302
```

After:

```python
def test_settings_dashboard_lists_settings(self, auth_client: FlaskClient):
    with patch("src.sqlalchemy_app.shared.services.setting_service.list_settings") as mock_list:
        mock_setting = MagicMock()
        mock_list.return_value = [mock_setting]
        response = auth_client.get("/admin/settings")
        assert response.status_code == 200
```

#### Step 3: Handle Tests That Verify Auth Requirements

Tests like `test_xxx_requires_admin` should be:

-   Deleted (auth is tested in the decorator itself)
-   Or moved to a separate file that doesn't use the mock

#### Step 4: Verify and Run Tests

```bash
pytest tests/integration/admin/routes/ -v
ruff check tests/integration/admin/routes/
```

## Benefits

1. **Cleaner tests**: No repetitive patching of `active_coordinators`
2. **Better assertions**: Tests can assert 200 and verify response content
3. **Focus on route logic**: Tests focus on what the route does, not authentication

## Files Modified

-   **Created**: `tests/integration/admin/routes/conftest.py`
-   **Modified**: All 6 test files in `tests/integration/admin/routes/`

## Estimated Effort

~1 hour total
