# Domain (PHP → Python port)

Python port of `src/Domain/**` (fixes + parser), using
[5j9/wikitextparser](https://github.com/5j9/wikitextparser) instead of the
original hand-rolled regex-based template/ref/category parser.

## Layout

```
domain/
├── fixes/
│   ├── media/
│   │   ├── fix_images.py              # FixImagesFixture.php
│   │   └── remove_missing_images.py   # RemoveMissingImagesService.php
│   ├── references/
│   │   ├── delete_empty_refs.py       # DeleteEmptyRefsFixture.php
│   │   ├── expand_refs.py             # ExpandRefsFixture.php
│   │   └── ref_worker.py              # RefWorkerFixture.php
│   ├── structure/
│   │   ├── fix_categories.py          # FixCategoriesFixture.php
│   │   └── fix_language_links.py      # FixLanguageLinksFixture.php
│   └── templates/
│       ├── delete_templates.py        # DeleteTemplatesFixture.php
│       └── fix_templates.py           # FixTemplatesFixture.php
└── parser/
    ├── category_parser.py             # CategoryParser.php
    ├── citations_parser.py            # CitationsParser.php
    ├── lead_section_parser.py         # LeadSectionParser.php
    └── template_helpers.py            # ParserTemplate.php + ParserTemplates.php + Template.php
```

## Install

```bash
pip install -r requirements.txt
```

## What changed vs. the PHP version

-   **Template parsing** (`ParserTemplate`, `ParserTemplates`, `Template`) is
    fully replaced by `wikitextparser.Template`. `template_helpers.py` is a
    thin compatibility layer (`strip_name`, `get_parameter`, `set_parameter`,
    `delete_parameter`, `render_pretty`, ...) so the `fixes` modules read
    almost like the PHP originals.
-   **`<ref>` tag parsing** (`CitationsParser.php`) uses
    `wikitextparser.parse(text).get_tags("ref")` instead of two separate
    regexes for "full" vs "short" refs; self-closing detection is done via
    `tag.string.endswith("/>")`.
-   **Categories / language links / inline images** use
    `wikitextparser`'s wikilink parsing instead of manual `[[...]]` regexes —
    this also fixes the PHP version's fragile handling of nested wikilinks
    inside captions (e.g. `[[File:x.png|caption with a [[link]] inside]]`).
    `remove_missing_images.py`'s `removeMissingInlineImages` in particular
    drops the PHP version's manual bracket-depth counter entirely.
-   **Lead section extraction** uses `wikitextparser`'s `.sections[0]` instead
    of a `preg_split` on `==` markers.
-   **Mutation pattern**: instead of PHP's `str_replace($old, $new, $text)`
    (which can misfire if the same snippet appears twice), the Python code
    parses once with `wtp.parse(text)`, mutates `Template`/`WikiLink` objects
    in place, then calls `str(parsed)` to get the final text. Because
    wikitextparser's objects are "live" views into the parsed text, removing
    an outer template/link before touching anything nested inside it is
    required — each `fixes` module collects targets first, then mutates
    ("two-pass"), to avoid touching now-stale nested objects.
-   `RemoveMissingImagesService` keeps the same
    `ImageExistenceChecker`/`image_exists()` dependency-injection shape as
    the PHP `CommonsImageServiceInterface` — you still need to supply a real
    Commons-checking implementation (e.g. calling the Wikimedia Commons API);
    none was included in the PHP source provided for conversion.
-   `ExpandRefsFixture.php`'s call into `Infrastructure\Debug\test_print` is
    replaced with standard `logging` (that infra module wasn't part of the
    provided source).
-   Function/file names were snake_cased per file per the requested layout
    (e.g. `del_empty_refs` → `delete_empty_refs`, `refs_expend_work` →
    `expand_refs`).

## Not ported (out of scope / not provided)

-   `Services\Api\CommonsImageService` and
    `Services\Interfaces\CommonsImageServiceInterface` (only referenced, not
    included in the PHP dump).
-   `Infrastructure\Debug\test_print`.
