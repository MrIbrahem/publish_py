# ruff: noqa: F401
"""
Unit tests for src/main_app/public/routes/html_to_segments/__init__.py module.

Classes to test: ProcessingError, HtmltoSegmentsRoutes
Functions to test: validate_request, create_error_response, create_success_response, process_text

TODO: write tests
"""


from src.main_app.public.routes.html_to_segments import (
    HtmltoSegmentsRoutes,
    ProcessingError,
    create_error_response,
    create_success_response,
    process_text,
    validate_request,
)
