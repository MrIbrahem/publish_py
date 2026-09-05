from __future__ import annotations

from ..parser.lead_section_parser import get_lead_section
from .media import RemoveMissingImagesService, remove_videos
from .references import (
    del_empty_refs,
    expand_text_refs,
    remove_bad_refs,
)
from .structure import remove_categories, remove_lang_links
from .templates import (
    add_missing_title,
    remove_lead_templates,
    remove_templates,
)


class WikitextFixerService:
    def __init__(self) -> None:
        """
        init
        """

    def fix(self, text: str, title: str, all_flag: bool = False) -> str:
        """
        Port the full fix_wikitext pipeline from the original PHP tool:
            - remove_templates
            - remove_lead_templates
            - remove_bad_refs
            - del_empty_refs
            - remove_videos
            - remove_categories
            - remove_missing_images
            - add_missing_title
        """

        if not all_flag:
            text = self.strip_text_into_lead_section(text)

        # Replace templates
        text = text.replace("{{drugbox", "{{Infobox drug")
        text = text.replace("{{Drugbox", "{{Infobox drug")

        # Clean up templates
        text = remove_templates(text)
        text = remove_lead_templates(text)

        # Clean up references
        text = remove_bad_refs(text)
        text = del_empty_refs(text)

        text = remove_lang_links(text)

        # Remove videos
        text = remove_videos(text)

        # text = remove_images(text)

        # Remove categories
        text = remove_categories(text)

        # Handle missing images and add title
        service = RemoveMissingImagesService()

        text = service.remove_missing_images(text)
        text = add_missing_title(text, title)

        return text

    def strip_text_into_lead_section(self, text: str) -> str:
        """
        Extracts the lead section from the given text and expands its references if applicable.

        If the lead section exists and is different from the original text,
        it expands the references within the lead section using the full text as context.
        Otherwise, it returns the original text unchanged.

        Args:
            text (str): The input text from which to extract and process the lead section.

        Returns:
            str: The expanded lead section if it differs from the original text,
                 otherwise the original text.
        """
        lead = get_lead_section(text)
        if lead and lead != text:
            return expand_text_refs(lead, text)

        return text


__all__ = [
    "WikitextFixerService",
]
