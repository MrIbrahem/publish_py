"""
text_chunk - A chunk of uniformly-annotated inline text

The annotations consist of a list of inline tags (<a>, <i> etc), and an
optional "inline element" (br/img tag, or a sub-document e.g. for a
reference span). The tags and/or reference apply to the whole text;
therefore text with varying markup must be split into multiple chunks.

converted from the LinearDoc javascript library of the Wikimedia Content translation project

https://github.com/wikimedia/mediawiki-services-cxserver/blob/master/lib/lineardoc/TextChunk.js
"""

from __future__ import annotations

from typing import Any


class TextChunk:
    """A chunk of uniformly-annotated inline text."""

    def __init__(
        self,
        text: str,
        tags: list[dict[str, Any]],
        *,
        inline_content: dict[str, Any] | None = None,
    ) -> None:
        """
        Initialize a text_chunk.

        Args:
            text: Plaintext in the chunk (can be '')
            tags: Array of SAX open tag objects, for the applicable tags
            inline_content: Tag or sub-doc (optional)
        """
        self.text = text
        self.tags = tags
        self.inline_content = inline_content

    def __str__(self) -> str:
        return self.text

    def __repr__(self) -> str:
        return self.text

    def generate_xml_chunk(self, utils, pad: str = "") -> list[str]:
        chunk_dump = []
        tags_dump = utils.dump_tags(self.tags)
        tags_attr = f' tags="{tags_dump}"' if tags_dump else ""

        if self.text:
            formatted_text_chunk = utils.esc(self.text).replace("\n", "&#10;")
            chunk_dump.append(f"{pad}<cxtextchunk{tags_attr}>" + formatted_text_chunk + "</cxtextchunk>")

        if self.inline_content:
            chunk_dump.append(f"{pad}<cxinlineelement{tags_attr}>")
            if hasattr(self.inline_content, "dump_xml_array"):
                # sub-doc: concatenate
                chunk_dump.extend(self.inline_content.dump_xml_array(pad + "  "))
            else:
                chunk_dump.append(f'{pad}  <{self.inline_content["name"]}/>')

            chunk_dump.append(f"{pad}</cxinlineelement>")

        return chunk_dump


__all__ = [
    "TextChunk",
]
