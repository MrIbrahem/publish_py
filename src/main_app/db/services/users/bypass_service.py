"""
Bypass logic for coordinator authorization checks.
"""

from __future__ import annotations

import logging

from flask import current_app

logger = logging.getLogger(__name__)


def is_bypass_enabled() -> bool:
    """Check if the UI test bypass is enabled in the current configuration.

    The bypass is enabled ONLY if the active config is DevelopmentConfig (safety check)
    AND the UI_TEST_BYPASS_COORDINATOR_CHECK setting is True.
    """
    try:
        return current_app.config.get("IS_DEVELOPMENT_CONFIG", False) and current_app.config.get(
            "UI_TEST_BYPASS_COORDINATOR_CHECK", False
        )
    except Exception:
        return False


def should_bypass_coordinator_check(username: str) -> bool:
    """Determine if the coordinator check should be bypassed for the given user.

    Development-only bypass: when running under DevelopmentConfig with
    UI_TEST_BYPASS_COORDINATOR_CHECK enabled, this check returns True so
    local UI/E2E/Playwright/Selenium tests don't require a real row in
    the coordinators (admin_user) table.

    The bypass is gated on IS_DEVELOPMENT_CONFIG, a concrete class
    attribute set only on DevelopmentConfig — never on ProductionConfig —
    so it cannot be activated in production regardless of environment
    variables. Do NOT rely on this bypass when testing authorization or
    permission logic itself; keep it disabled for those tests.
    """
    if is_bypass_enabled():
        current_app.logger.warning(
            "UI_TEST_BYPASS_COORDINATOR_CHECK is active — coordinator "
            "authorization check bypassed for username=%s.",
            username,
        )
        return True

    return False
