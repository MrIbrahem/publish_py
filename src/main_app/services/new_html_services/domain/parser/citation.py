"""
Citation parser for WikiText reference tags
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
import re

import wikitextparser as wtp

logger = logging.getLogger(__name__)


@dataclass
class Citation:
    """Represents a citation reference"""

    def __init__(self, ref: wtp._tag.Tag) -> None:
        self.ref = ref
        self.tag = self.ref.string
        self.contents = self.ref.contents or ""
        self.options = dict(self.ref.attrs)

        self.attrs = self.ref.attrs

    @property
    def name(self) -> str:
        """Get citation name"""
        return self.ref.attrs.get("name", "").strip()

    def set_contents(self, new_content: str) -> None:
        """Set citation content"""
        self.ref.contents = new_content

    def get_attributes(self) -> str:
        """Get citation options/attributes as a string"""
        tag_str = str(self.ref.string)
        # Find the end of the opening tag: could be ">" or "/>"
        close_idx = tag_str.find(">")
        if close_idx == -1:
            return ""
        attrs_part = tag_str[len("<ref") : close_idx]
        # Strip trailing "/" for self-closing tags
        attrs_part = attrs_part.rstrip(" /")
        return attrs_part.strip()

    def to_string_self_closing(self) -> str:
        """Convert to self-closing tag string"""
        attributes = self.get_attributes()
        if attributes:
            return f"<ref {attributes} />"
        return self.ref.string

    def to_string(self) -> str:
        """Convert back to reference tag string"""
        if self.is_self_closing():
            return self.ref.string.replace("></ref>", " />")

        return self.ref.string

    def is_self_closing(self) -> bool:
        return not self.contents or not self.contents.strip()

    @staticmethod
    def fix_tag_name(ref_text: str) -> str:
        """
        Fix tag name for self-closing tags
        BUG: Citation.from_text("<ref name = PI2022/>").name == "PI2022/" this should be fixed in Citation to become "PI2022"
        """
        m = re.match(r"(<ref [^\/>]*[^ ])\/\s*>", ref_text)
        if m:
            ref_text = m.group(1) + " />"

        return ref_text

    @classmethod
    def from_text(cls, ref_text: str, fix_name_issue: bool = True) -> Citation:
        """Create a Citation from a reference tag string"""

        if not ref_text.strip().startswith("<ref"):
            raise ValueError("Not a reference tag")

        if ref_text.count("<ref") != 1:
            raise ValueError("Multiple reference tags")

        if fix_name_issue:
            ref_text = cls.fix_tag_name(ref_text)

        tag = wtp._tag.Tag(ref_text)
        return Citation(tag)


__all__ = [
    "Citation",
]
