"""
Contextualizer for HTML - tracks the segmentation context of the currently open node.
"""


class Contextualizer:
    """Contextualizer for HTML."""

    def __init__(self, config=None):
        """
        Initialize the contextualizer.

        Args:
            config: Configuration dict
        """
        self.contexts = []
        self.config = config or {}

    def get_child_context(self, open_tag):
        """
        Get the context for a new tag being opened.

        Args:
            open_tag: Tag dict with 'name' and 'attributes'

        Returns:
            The new context
        """
        # Change to 'media' context inside figure
        if open_tag["name"] == "figure":
            return "media"

        # Exception: return to undefined context inside figure//figcaption
        if open_tag["name"] == "figcaption":
            return None

        # No change: same as parent context
        return self.get_context()

    def get_context(self):
        """
        Get the current context.

        Returns:
            The current context
        """
        return self.contexts[-1] if self.contexts else None

    def on_open_tag(self, open_tag):
        """
        Call when a tag opens.

        Args:
            open_tag: Tag dict with 'name' and 'attributes'
        """
        self.contexts.append(self.get_child_context(open_tag))

    def on_close_tag(self, tag=None):
        """Call when a tag closes (or just after an empty tag opens)."""
        if self.contexts:
            self.contexts.pop()

    def can_segment(self):
        """
        Determine whether sentences can be segmented into spans in this context.

        Returns:
            Whether sentences can be segmented into spans in this context
        """
        return self.get_context() is None
