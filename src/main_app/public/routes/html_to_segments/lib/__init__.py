"""
Library package for CX server.
"""

from __future__ import annotations

from .processor import normalize, process_html

from .lineardoc import Normalizer, Parser
__all__ = ["process_html", "normalize", "Normalizer", "Parser",]
