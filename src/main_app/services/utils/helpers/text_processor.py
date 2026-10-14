"""
Text processing utilities.

Mirrors: php_src/text_change.php

"""

from __future__ import annotations

from dataclasses import asdict, dataclass
import logging
from typing import Any

PageFixer = None

try:
    from fix_refs import PageFixer
except ImportError:
    PageFixer = None

logger = logging.getLogger(__name__)


@dataclass
class LangSetting:
    """Per-language fixing options."""
    lang: str
    move_dots: bool = True
    expend_infobox: bool = True
    add_en_lang: bool = False
    add_category: bool = False

    def to_json(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_any(cls, setting: LangSetting | dict[str, Any]) -> LangSetting:
        """Create LangSetting from any input."""
        if isinstance(setting, LangSetting):
            return setting

        return cls(**setting)

class TextProcessor:

    @staticmethod
    def load_lang(
        lang: str,
        move_dots: bool = True,
        expend_infobox: bool = True,
        add_en_lang: bool = False,
        add_category: bool = False,
    ) -> LangSetting:
        return LangSetting(
            lang=lang,
            move_dots=move_dots,
            expend_infobox=expend_infobox,
            add_en_lang=add_en_lang,
            add_category=add_category,
        )

    @staticmethod
    def fix(
        text: str | Any,
        title: str,
        lang_setting: LangSetting,
        source_title: str = "",
        mdwiki_revid: int | str = 0,
    ) -> str:
        if PageFixer is None:
            logger.error("fix_refs library is not installed")
            return text

        if not isinstance(text, str):
            return text

        if not text.strip():
            return text

        fixer = PageFixer(
            text=text,
            title=title,
            source_title=source_title,
            mdwiki_revid=mdwiki_revid,
            lang_setting=lang_setting.to_json(),
        )

        return fixer.run()

__all__ = [
    "TextProcessor",
]
