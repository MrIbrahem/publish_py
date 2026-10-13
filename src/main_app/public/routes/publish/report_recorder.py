"""
ReportRecorder    : writes the to_do file + inserts the report row
"""

from __future__ import annotations

import json
import logging
from typing import Any

from ....database.services import ReportService
from ....services.utils.helpers import ToDoLogger

logger = logging.getLogger(__name__)

# --------------------------------------------------------------------------- #
# Reporting
# --------------------------------------------------------------------------- #


class ReportRecorder:
    """Saves an operation to the to_do file and to the reports table."""

    def __init__(
        self,
        report_service: ReportService | None = None,
        todo_logger: ToDoLogger | None = None,
    ) -> None:
        self.report_service = report_service or ReportService()
        self.todo_logger = todo_logger or ToDoLogger()

    def record(
        self,
        data: dict[str, Any],
        file_name: str,
        *,
        title: str,
        user: str,
        lang: str,
        sourcetitle: str,
    ) -> None:
        self.todo_logger.log(data, file_name)

        self.report_service.add_report(
            title=title,
            user=user,
            lang=lang,
            sourcetitle=sourcetitle,
            result=file_name,
            data=json.dumps(data),
        )


__all__ = [
    "ReportRecorder",
]
