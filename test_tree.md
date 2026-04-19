```
tests/
├── __init__.py
├── conftest.py
├── integration/
│   ├── sqlalchemy_app/
│   │   └── shared/
│   │       ├── core/
│   │       │   └── cors/
│   │       │       └── test_is_allowed_checker.py
│   │       └── domain/
│   │           └── services/
│   │               ├── test_pages_service.py
│   │               └── test_users_services.py
│   └── sqlalchemy_app.zip
└── unit/
    ├── admin/
    │   ├── domain/
    │   │   └── services/
    │   │       ├── test_coordinator_sqlalchemy_service.py
    │   │       ├── test_full_translator_sqlalchemy_service.py
    │   │       ├── test_language_setting_sqlalchemy_service.py
    │   │       ├── test_setting_sqlalchemy_service.py
    │   │       └── test_users_no_inprocess_sqlalchemy_service.py
    │   └── routes/
    ├── db_models/
    │   ├── admin_models/
    │   │   ├── test_coordinator_model.py
    │   │   ├── test_full_translator_model.py
    │   │   ├── test_language_setting_model.py
    │   │   ├── test_setting_model.py
    │   │   └── test_users_no_inprocess_model.py
    │   ├── public_models/
    │   │   ├── test_assessment_model.py
    │   │   ├── test_enwiki_pageview_model.py
    │   │   ├── test_in_process_model.py
    │   │   ├── test_lang_model.py
    │   │   ├── test_mdwiki_revid_model.py
    │   │   ├── test_pages_users_to_main_model.py
    │   │   ├── test_project_model.py
    │   │   ├── test_refs_count_model.py
    │   │   ├── test_translate_type_model.py
    │   │   ├── test_user_model.py
    │   │   ├── test_views_new_model.py
    │   │   └── test_word_model.py
    │   └── shared_models/
    │       ├── test_category_model.py
    │       ├── test_page_model.py
    │       ├── test_qid_model.py
    │       ├── test_report_model.py
    │       └── test_user_token_model.py
    ├── public/
    │   ├── domain/
    │   │   └── services/
    │   │       ├── test_assessment_sqlalchemy_service.py
    │   │       ├── test_enwiki_pageview_sqlalchemy_service.py
    │   │       ├── test_in_process_sqlalchemy_service.py
    │   │       ├── test_lang_sqlalchemy_service.py
    │   │       ├── test_mdwiki_revid_sqlalchemy_service.py
    │   │       ├── test_pages_users_to_main_sqlalchemy_service.py
    │   │       ├── test_project_sqlalchemy_service.py
    │   │       ├── test_refs_count_sqlalchemy_service.py
    │   │       ├── test_translate_type_sqlalchemy_service.py
    │   │       ├── test_user_service_sqlalchemy_service.py
    │   │       ├── test_views_new_sqlalchemy_service.py
    │   │       └── test_word_sqlalchemy_service.py
    │   ├── routes/
    │   │   ├── api/
    │   │   ├── auth/
    │   │   ├── cxtoken/
    │   │   │   ├── test_cxtoken_cors_disabled.py
    │   │   │   └── test_cxtoken_cors_on.py
    │   │   ├── main/
    │   │   ├── publish/
    │   │   │   ├── test_publish_cors_disabled.py
    │   │   │   ├── test_publish_cors_on.py
    │   │   │   └── test_publish_csrf_integration.py
    │   │   ├── refs/
    │   │   ├── test_api_integration.py
    │   │   ├── test_cxtoken_cache.py
    │   │   └── test_cxtoken_cache_unit.py
    │   └── test_workers/
    │       └── test_post_worker.py
    └── shared/
        ├── auth/
        │   ├── test_decorators.py
        │   └── test_identity.py
        ├── clients/
        │   ├── test_mediawiki_api.py
        │   ├── test_oauth_client.py
        │   ├── test_revids_client.py
        │   └── test_wikidata_client.py
        ├── core/
        │   ├── cookies/
        │   │   └── test_cookie.py
        │   ├── cors/
        │   │   ├── test_check_cors_decorated.py
        │   │   ├── test_cors_request_unit.py
        │   │   ├── test_cors_wrappers.py
        │   │   ├── test_cors_wrappers_and_headers.py
        │   │   ├── test_is_allowed_checker_unit.py
        │   │   └── test_publish_secret_checks.py
        │   └── test_crypto.py
        ├── domain/
        │   └── services/
        │       ├── test_category_sqlalchemy_service.py
        │       ├── test_page_sqlalchemy_service.py
        │       ├── test_qid_sqlalchemy_service.py
        │       ├── test_report_sqlalchemy_service.py
        │       └── test_user_token_sqlalchemy_service.py
        └── utils/
            ├── helpers/
            │   ├── test_files.py
            │   ├── test_format.py
            │   ├── test_text_processor.py
            │   ├── test_words.py
            │   └── test_words_unit.py
            └── test_decode_bytes.py

```