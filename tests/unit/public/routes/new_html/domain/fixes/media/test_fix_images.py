"""
Unit tests for src/main_app/public/routes/new_html/domain/fixes/media/fix_images.py module.

Functions to test: remove_images, remove_videos

Ported from the PHP suite ``FixImagesTest`` (FixRefs\\Tests\\WikiTextFixes).
"""

from __future__ import annotations

from src.main_app.public.routes.new_html.domain.fixes.media.fix_images import (
    remove_images,
    remove_videos,
)

# ---------------------------------------------------------------------------
# Tests for remove_images
# ---------------------------------------------------------------------------


class TestRemoveImages:
    """Tests for the `remove_images` function of the `fix_images` module."""

    def test_remove_images_with_simple_image(self):
        """A single [[File:...]] link is wrapped in a #ifexist check."""
        text = "Text [[File:Example.png|thumb|Description]] more text"
        result = remove_images(text)

        assert "{{subst:#ifexist:File:Example.png|" in result
        assert "[[File:Example.png|thumb|Description]]}}" in result

    def test_remove_images_with_multiple_images(self):
        """Every [[File:...]] link in the text gets wrapped."""
        text = "[[File:Image1.jpg|thumb]] text [[File:Image2.png|Description]]"
        result = remove_images(text)

        assert "{{subst:#ifexist:File:Image1.jpg|" in result
        assert "{{subst:#ifexist:File:Image2.png|" in result

    def test_remove_images_with_complex_parameters(self):
        """A file link with many parameters and a nested link is wrapped intact."""
        text = "[[File:Test.jpg|thumb|upright=1.3|alt=Alt text|Caption with [[link]]]]"
        result = remove_images(text)

        assert "{{subst:#ifexist:File:Test.jpg|" in result
        assert "[[link]]" in result

    def test_remove_images_with_no_images(self):
        """Text without any file links is returned unchanged."""
        text = "Plain text without images"
        result = remove_images(text)

        assert result == text

    def test_remove_images_with_empty_text(self):
        """Empty input returns empty output."""
        result = remove_images("")

        assert result == ""

    def test_remove_images_preserves_non_file_links(self):
        """Non-File wikilinks (article links, categories) are left untouched."""
        text = "[[Article link]] and [[File:Image.jpg|thumb]] and [[Category:Test]]"
        result = remove_images(text)

        assert "[[Article link]]" in result
        assert "[[Category:Test]]" in result
        assert "{{subst:#ifexist:" in result

    def test_remove_images_with_nested_links(self):
        """A nested wikilink inside the image caption survives the wrap."""
        text = "[[File:Test.jpg|Caption with [[nested link|display]]]]"
        result = remove_images(text)

        assert "{{subst:#ifexist:File:Test.jpg|" in result
        assert "[[nested link|display]]" in result

    def test_remove_images_with_upright(self):
        """The `upright=` parameter is preserved inside the wrapped link."""
        text = "[[File:Logo.png|thumb|upright=1.3|Logo description]]"
        result = remove_images(text)

        assert "{{subst:#ifexist:File:Logo.png|" in result
        assert "upright=1.3" in result

    def test_remove_images_multiple_occurrences_same_file(self):
        """Two separate links to the same filename are both wrapped independently."""
        text = "[[File:Same.jpg|thumb]] text [[File:Same.jpg|Different caption]]"
        result = remove_images(text)

        count = result.count("{{subst:#ifexist:File:Same.jpg|")
        assert count == 2

    def test_remove_images_with_special_characters_in_filename(self):
        """Filenames with spaces, hyphens, underscores, and parentheses are handled."""
        text = "[[File:Test-image_2020 (1).png|Description]]"
        result = remove_images(text)

        assert "{{subst:#ifexist:File:Test-image_2020 (1).png|" in result


# ---------------------------------------------------------------------------
# Tests for remove_videos
# ---------------------------------------------------------------------------


class TestRemoveVideos:
    """Tests for the `remove_videos` function of the `fix_images` module."""

    def test_remove_videos_with_webm_file(self):
        """A .webm file link is removed while surrounding text remains."""
        text = "Text [[File:Video.webm|frameless|Description]] more"
        result = remove_videos(text)

        assert "[[File:Video.webm" not in result
        assert "Text" in result
        assert "more" in result

    def test_remove_videos_with_ogv_file(self):
        """A .ogv file link is removed."""
        text = "[[File:Video.ogv|thumb|Video description]]"
        result = remove_videos(text)

        assert "[[File:Video.ogv" not in result

    def test_remove_videos_with_ogg_file(self):
        """A .ogg file link is removed."""
        text = "[[File:Audio.ogg|Description]]"
        result = remove_videos(text)

        assert "[[File:Audio.ogg" not in result

    def test_remove_videos_with_mp4_file(self):
        """A .mp4 file link is removed."""
        text = "[[File:Video.mp4|thumb|upright=1.36|Description]]"
        result = remove_videos(text)

        assert "[[File:Video.mp4" not in result

    def test_remove_videos_preserves_images(self):
        """Non-video file links are preserved while video links are removed."""
        text = "[[File:Image.jpg|thumb]] and [[File:Video.webm|Video]]"
        result = remove_videos(text)

        assert "[[File:Image.jpg|thumb]]" in result
        assert "[[File:Video.webm" not in result

    def test_remove_videos_with_multiple_videos(self):
        """All video links are removed when several are present."""
        text = "[[File:V1.webm|Video 1]] [[File:V2.ogv|Video 2]] [[File:V3.mp4|Video 3]]"
        result = remove_videos(text)

        assert "[[File:V1.webm" not in result
        assert "[[File:V2.ogv" not in result
        assert "[[File:V3.mp4" not in result

    def test_remove_videos_with_case_variations(self):
        """Video extensions are matched case-insensitively."""
        text = "[[File:Video.WEBM|Uppercase]] [[File:Video.Ogv|Mixed]]"
        result = remove_videos(text)

        assert "[[File:Video.WEBM" not in result
        assert "[[File:Video.Ogv" not in result

    def test_remove_videos_with_no_videos(self):
        """Non-video images remain untouched when no video links are present."""
        text = "[[File:Image.jpg|thumb]] [[File:Photo.png|Description]]"
        result = remove_videos(text)

        assert "[[File:Image.jpg|thumb]]" in result
        assert "[[File:Photo.png|Description]]" in result

    def test_remove_videos_with_empty_text(self):
        """Empty input returns empty output."""
        result = remove_videos("")

        assert result == ""

    def test_remove_videos_with_complex_parameters(self):
        """A video link with several parameters is fully removed."""
        text = "[[File:Video.webm|frameless|upright=1.36|thumbtime=2:25|Video explanation]]"
        result = remove_videos(text)

        assert "[[File:Video.webm" not in result

    def test_remove_videos_with_nested_template(self):
        """A video link whose caption contains a template is fully removed."""
        text = "[[File:Video.webm|Description with {{template}}]]"
        result = remove_videos(text)

        assert "[[File:Video.webm" not in result

    def test_remove_videos_preserves_text_around(self):
        """Text before and after the removed video link is preserved."""
        text = "Before video [[File:Test.webm|Video]] after video"
        result = remove_videos(text)

        assert "Before video" in result
        assert "after video" in result
        assert "[[File:Test.webm" not in result

    def test_remove_videos_does_not_affect_non_video_extensions(self):
        """Non-video file extensions (pdf, mp3) are left in place."""
        text = "[[File:Document.pdf|Document]] [[File:Audio.mp3|Audio]]"
        result = remove_videos(text)

        assert "[[File:Document.pdf" in result
        assert "[[File:Audio.mp3" in result
