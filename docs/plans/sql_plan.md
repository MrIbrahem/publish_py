# create following files for each table in

1. src/app_main/admin/domain/db/schema.py

    -   coordinator
    -   full_translators
    -   language_settings
    -   settings
    -   users_no_inprocess

2. src/app_main/public/domain/db/schema.py

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

---
```
src/
├── app_main/
│   ├── public/
│   │   └── domain/
│           └── models/
|               ├── lang.py
|               └── ...
│           └── db/
|               ├── db_langs.py
|               └── ...
│           └── services/
|               ├── langs_service.py
|               └── ...
│   └── admin/
│       └── domain/
│           └── models/
|               ├── coordinator.py
|               └── ...
│           └── db/
|               ├── db_coordinators.py
|               └── ...
│           └── services/
|               ├── coordinators_service.py
|               └── ...
├── tests/
│   ├── unit/
│   │   ├── public/
│   │   │   └── domain/
│   │   │       └── models/
│                   ├── test_lang_model.py
│                   └── ...
│   │   │       └── db/
│                   ├── test_db_langs.py
│                   └── ...
│   │   │       └── services/
│                   ├── test_langs_service.py
│                   └── ...
│   │   └── admin/
│   │       └── domain/
│   │           └── models/
│                   ├── test_coordinator_model.py
│                   └── ...
│   │           └── db/
│                   ├── test_db_coordinators.py
│                   └── ...
│   │           └── services/
│                   ├── test_coordinators_service.py
│                   └── ...
```
