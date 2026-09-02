class WikitextFixerService:
    def __init__(self, text: str, title: str) -> None:
        self.text = text
        self.title = title

    def fix(self) -> str:
        """
        Temporary placeholder.

        TODO: Port the full fix_wikitext pipeline from the original PHP tool:
            - {{drugbox / {{Drugbox → {{Infobox drug
            - remove_templates
            - remove_lead_templates
            - remove_bad_refs
            - del_empty_refs
            - remove_videos
            - remove_categories
            - removeMissingImages
            - add_missing_title
        """
        return self.text


__all__ = [
    "WikitextFixerService",
]
