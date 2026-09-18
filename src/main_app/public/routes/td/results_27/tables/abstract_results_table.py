"""Port of ``results_27/Tables/AbstractResultsTable.php``.

The PHP base class also emits the surrounding ``<table>`` HTML
(``startTable``/``endTable``). In the Python port that skeleton lives in the
Jinja partials, so only the row-building contract is retained here.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class AbstractResultsTable(ABC):
    """Base class for all results tables."""

    @abstractmethod
    def build(self, items: Any) -> Any:
        """Build the table's row data from ``items``."""
