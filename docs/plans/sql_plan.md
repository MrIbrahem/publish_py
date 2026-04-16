# create following files for each table in

1. src/app_main/admin/domain/db/schema.py

    - coordinator
    - full_translators
    - language_settings
    - settings
    - users_no_inprocess

2. src/app_main/public/domain/db/schema.py

    - langs
    - assessments
    - enwiki_pageviews
    - in_process
    - mdwiki_revids
    - pages_users_to_main
    - projects
    - refs_counts
    - translate_type
    - users
    - views_new
    - words

---

```
publish_py/
├── src/
│   └── app_main/
│       ├── admin/
│       │   └── domain/
│       │       ├── db/
│       │       │   ├── schema.py
│       │       │   ├── db_coordinators.py
│       │       │   └── ...
│       │       ├── models/
│       │       │   ├── coordinator.py
│       │       │   ├── ...
│       │       └── services/
│       │           ├── coordinators_service.py
│       │           ├── ...
│       ├── public/
│       │   └── domain/
│       │       ├── db/
│       │       │   ├── schema.py
│       │       │   ├── db_langs.py
│       │       │   └── ...
│       │       ├── models/
│       │       │   ├── assessment.py
│       │       │   ├── ...
│       │       └── services/
│       │           ├── langs_service.py
│       │           ├── ...
├── tests/
│   └── unit/
│       ├── admin/
│       │   └── domain/
│       │       ├── db/
│       │       │   ├── test_db_coordinators.py
│       │       │   ├── ...
│       │       ├── models/
│       │       │   ├── test_coordinator_model.py
│       │       │   ├── ...
│       │       └── services/
│       │           ├── test_coordinators_service.py
│       │           ├── ...
│       ├── public/
│       │   └── domain/
│       │       ├── db/
│       │       │   ├── test_db_langs.py
│       │       │   ├── ...
│       │       ├── models/
│       │       │   ├── test_assessment_model.py
│       │       │   ├── ...
│       │       └── services/
│       │           ├── test_langs_service.py
│       │           ├── ...
```

# Note:

-   models and models tests already created start creating db files then services
