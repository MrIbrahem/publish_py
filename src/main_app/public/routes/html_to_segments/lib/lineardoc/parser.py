"""
Parser to read an HTML stream into a Doc.

converted from the LinearDoc javascript library of the Wikimedia Content translation project

https://github.com/wikimedia/mediawiki-services-cxserver/blob/master/lib/lineardoc/Parser.js
"""

from __future__ import annotations

import logging
from typing import Any

from lxml import etree

from .builder import Builder
from .contextualizer import Contextualizer
from .elements import BLOCK_TAGS, VOID_ELEMENTS
from .mw_contextualizer import MwContextualizer
from .utils import Utils

logger = logging.getLogger(__name__)


class Parser:
    """Parser to read an HTML stream into a Doc."""

    def __init__(
        self,
        contextualizer: MwContextualizer | Contextualizer,
        options=None,
        sort_attrs: bool = True,
    ) -> None:
        """
        Initialize the parser.

        Args:
            contextualizer: Tag contextualizer
            options: Options dict
        """
        self.contextualizer = contextualizer
        self.options = options or {}
        self.lowercase = True
        self.sort_attrs = sort_attrs

    def init(self) -> None:
        """
        Initialize state for parsing.
        """
        self.root_builder = Builder(sort_attrs=self.sort_attrs)
        self.builder = self.root_builder
        # Stack of tags currently open
        self.all_tags = []

    def write(self, html: str) -> None:
        """
        Parse HTML into the document.

        Args:
            html: HTML string to parse
        """
        parser = etree.HTMLParser(encoding="utf-8")
        try:
            root = etree.fromstring(html.encode("utf-8"), parser)
            self._process_element(root)
        except Exception:
            # Try with wrapping
            try:
                root = etree.fromstring(f"<div>{html}</div>".encode(), parser)
                for child in root:
                    self._process_element(child)
            except Exception as e:
                raise Exception(f"Failed to parse HTML: {e}") from e

    def _process_element(self, element: etree._Element | Any) -> None:
        """
        Process an element recursively.
        """
        # Skip comments and other special nodes
        if not isinstance(element.tag, str):
            return

        tag_name = element.tag.lower() if self.lowercase else element.tag

        # Create tag dict
        tag = {"name": tag_name, "attributes": dict(element.attrib)}

        # Mark HTML void elements as self-closing
        if tag_name in VOID_ELEMENTS:
            tag["isSelfClosing"] = True

        self.on_open_tag(tag)

        # Process text content
        if element.text:
            self.on_text(element.text)

        # Process children
        for child in element:
            self._process_element(child)
            # Process tail text after child
            if child.tail:
                self.on_text(child.tail)

        self.on_close_tag(tag_name)

    def on_open_tag(self, tag: dict[str, Any]) -> None:
        """
        Handle open tag event.

        Args:
            tag: Tag dict with 'name' and 'attributes'
        """
        if self.contextualizer.get_context() == "removable" or self.contextualizer.is_removable(tag):
            self.all_tags.append(tag)
            self.contextualizer.on_open_tag(tag)
            return

        if self.options.get("isolateSegments") and Utils.is_segment(tag):
            self.builder.push_block_tag({"name": "div", "attributes": {"class": "cx-segment-block"}})

        if Utils.is_reference(tag) or Utils.is_math(tag):
            # Start a reference: create a child builder, and move into it
            self.builder = self.builder.create_child_builder(tag)

        elif Utils.is_inline_empty_tag(tag["name"]):
            self.builder.add_inline_content(tag, self.contextualizer.can_segment())

        elif self.is_inline_annotation_tag(tag["name"], Utils.is_transclusion(tag)):
            self.builder.push_inline_annotation_tag(tag)
        else:
            self.builder.push_block_tag(tag)

        self.all_tags.append(tag)
        self.contextualizer.on_open_tag(tag)

    def on_close_tag(self, tag_name) -> None:
        """
        Handle close tag event.

        Args:
            tag_name: Name of tag to close
        """
        if not self.all_tags:
            return

        tag = self.all_tags.pop()
        is_ann = self.is_inline_annotation_tag(tag_name, Utils.is_transclusion(tag))

        if self.contextualizer.is_removable(tag) or self.contextualizer.get_context() == "removable":
            self.contextualizer.on_close_tag(tag)
            return

        self.contextualizer.on_close_tag(tag)

        if Utils.is_inline_empty_tag(tag_name):
            return
        elif is_ann and len(self.builder.inline_annotation_tags) > 0:
            self.builder.pop_inline_annotation_tag(tag_name)
            if self.options.get("isolateSegments") and Utils.is_segment(tag):
                self.builder.pop_block_tag("div")
        elif is_ann and self.builder.parent is not None:
            # In a sub document: should be a span or sup that closes a reference
            if tag_name not in ("span", "sup"):
                raise Exception(f'Expected close reference - span or sup tags, got "{tag_name}"')
            self.builder.finish_text_block()
            self.builder.parent.add_inline_content(self.builder.doc, self.contextualizer.can_segment())
            # Finished with child now. Move back to the parent builder
            self.builder = self.builder.parent
        elif not is_ann:
            # Block level tag close
            if tag_name == "p" and self.contextualizer.can_segment():
                # Add an empty textchunk before the closing block tag
                self.builder.add_text_chunk("", self.contextualizer.can_segment())
            self.builder.pop_block_tag(tag_name)
        else:
            raise Exception(f"Unexpected close tag: {tag_name}")

    def on_text(self, text: str) -> None:
        """
        Handle text event.

        Args:
            text: Text content
        """
        if self.contextualizer.get_context() == "removable":
            return
        self.builder.add_text_chunk(text, self.contextualizer.can_segment())

    def on_script(self, text: str) -> None:
        """Handle script text."""
        self.builder.add_text_chunk(text, self.contextualizer.can_segment())

    def is_inline_annotation_tag(self, tag_name, is_transclusion) -> bool:
        """
        Determine whether a tag is an inline annotation or not.

        Args:
            tag_name: Tag name in lowercase
            is_transclusion: If the tag is transclusion

        Returns:
            Whether the tag is an inline annotation
        """
        context = self.contextualizer.get_context()

        # <span> inside a media context acts like a block tag
        if tag_name == "span" and context == "media":
            return False

        # Audio or Video are block tags. But in a media-inline context they are inline
        if tag_name in ("audio", "video") and context == "media-inline":
            return True

        # Styles are usually block tags, but sometimes style tags are used as transclusions
        if tag_name == "style" and is_transclusion:
            return True

        # All tags that are not block tags are inline annotation tags
        return tag_name not in BLOCK_TAGS


__all__ = [
    "Parser",
]
