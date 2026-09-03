

from .templates import (
    remove_templates,
    remove_lead_templates,
    add_missing_title,
)
from .references import (
    remove_bad_refs,
    del_empty_refs,
)

from .structure import remove_categories
# from .media import remove_images
from .media import remove_videos
from .media import RemoveMissingImagesService


class WikitextFixerService:
    def __init__(self, text: str, title: str) -> None:
        self.text = text
        self.title = title

    def fix(self) -> str:
        """
        Temporary placeholder.

        TODO: Port the full fix_wikitext pipeline from the original PHP tool:
            - remove_templates
            - remove_lead_templates
            - remove_bad_refs
            - del_empty_refs
            - remove_videos
            - remove_categories
            - remove_missing_images
            - add_missing_title
        """
        text = self.text
        title = self.title

        # Replace templates
        text = text.replace("{{drugbox", "{{Infobox drug")
        text = text.replace("{{Drugbox", "{{Infobox drug")

        # Clean up templates
        text = remove_templates(text)
        text = remove_lead_templates(text)

        # Clean up references
        text = remove_bad_refs(text)
        text = del_empty_refs(text)

        # text = remove_lang_links(text)

        # Remove videos
        text = remove_videos(text)

        # text = remove_images(text)

        # Remove categories
        text = remove_categories(text)

        # Handle missing images and add title
        service = RemoveMissingImagesService()

        text = service.remove_missing_images(text)
        text = add_missing_title(text, title)

        return self.text


__all__ = [
    "WikitextFixerService",
]
