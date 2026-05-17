 src/main_app/shared/services/
  ├── __init__.py                    # Re-exports from all sub-packages
  │
  ├── pages/                         # Core translation workflow
  │   ├── __init__.py
  │   ├── page_service.py
  │   ├── user_page_service.py
  │   ├── in_process_service.py
  │   ├── translate_type_service.py
  │   └── pages_users_to_main_service.py
  │
  ├── users/                         # User management & access control
  │   ├── __init__.py
  │   ├── user_service.py
  │   ├── user_token_service.py
  │   ├── coordinator_service.py
  │   ├── full_translator_service.py
  │   └── users_no_inprocess_service.py
  │
  ├── wikidata/                      # Wikidata QID mappings
  │   ├── __init__.py
  │   ├── qid_service.py
  │   └── allqid_service.py
  │
  ├── content/                       # Taxonomy & content metadata
  │   ├── __init__.py
  │   ├── category_service.py
  │   ├── lang_service.py
  │   ├── language_setting_service.py
  │   ├── project_service.py
  │   └── word_service.py
  │
  ├── analytics/                     # Page views, refs, assessments
  │   ├── __init__.py
  │   ├── enwiki_pageview_service.py
  │   ├── views_new_service.py
  │   ├── refs_count_service.py
  │   └── assessment_service.py
  │
  ├── reports/                       # Publishing reports & revision tracking
  │   ├── __init__.py
  │   ├── report_service.py
  │   └── mdwiki_revid_service.py
  │
  └── config/                        # App settings
      ├── __init__.py
      └── setting_service.py
