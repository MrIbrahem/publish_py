# for each table in

## src/app_main/admin/domain/db/schema.py

-   coordinator
-   full_translators
-   language_settings
-   settings
-   users_no_inprocess

## src/app_main/public/domain/db/schema.py

-   langs
-   assessments
-   enwiki_pageviews
-   in_process
-   mdwiki_revids
-   pages_users_to_main
-   projects
-   refs_counts
-   translate_type
-   users
-   views_new
-   words

# create models

## src/app_main/admin/domain/models

-   coordinator.py
-   ...

## src/app_main/public/domain/models

-   lang.py
-   ...

# models tests

## tests/unit/admin/domain/models

-   test_coordinator_model.py
-   ...

## tests/unit/public/domain/models

-   test_lang_model.py
-   ...
