# ruff: noqa: F401
"""
Unit tests for src/main_app/public/routes/html_to_segments/lib/lineardoc/utils.py module.

Functions to test: find_all, esc, esc_attr, get_open_tag_html, get_close_tag_html, clone_open_tag, dump_tags, is_reference, is_math, is_gallery, is_reference_list, is_external_link, is_segment, is_transclusion, is_transclusion_fragment, is_non_translatable, is_inline_empty_tag, get_chunk_boundary_groups, add_common_tag, set_link_ids_in_place, is_ignorable_block, is_closing_template_match


"""


from src.main_app.public.routes.html_to_segments.lib.lineardoc.utils import (
    add_common_tag,
    clone_open_tag,
    dump_tags,
    esc,
    esc_attr,
    find_all,
    get_chunk_boundary_groups,
    get_close_tag_html,
    get_open_tag_html,
    is_closing_template_match,
    is_external_link,
    is_gallery,
    is_ignorable_block,
    is_inline_empty_tag,
    is_math,
    is_non_translatable,
    is_reference,
    is_reference_list,
    is_segment,
    is_transclusion,
    is_transclusion_fragment,
    set_link_ids_in_place,
)
