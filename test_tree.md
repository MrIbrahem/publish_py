```
tests/
├── unit/
│   ├── admin/
│   │   ├── routes/
│   │   ├── services/
│   │       ├── coordinator_service.py
│   │       ├── full_translator_service.py
│   │       ├── language_setting_service.py
│   │       ├── setting_service.py
│   │       ├── users_no_inprocess_service.py
│   ├── public/
│   │   ├── routes/
│   │   │   ├── api/
│   │   │   ├── auth/
│   │   │   ├── cxtoken/
│   │   │   │   ├── cxtoken_cors_disabled.py
│   │   │   │   ├── cxtoken_cors_on.py
│   │   │   ├── main/
│   │   │   ├── publish/
│   │   │   │   ├── publish_cors_disabled.py
│   │   │   │   ├── publish_cors_on.py
│   │   │   │   ├── publish_csrf_integration.py
│   │   │   ├── refs/
│   │   │   ├── api_integration.py
│   │   │   ├── cxtoken_cache.py
│   │   │   ├── cxtoken_cache_unit.py
│   │   ├── services/
│   │   │   ├── assessment_service.py
│   │   │   ├── enwiki_pageview_service.py
│   │   │   ├── in_process_service.py
│   │   │   ├── lang_service.py
│   │   │   ├── mdwiki_revid_service.py
│   │   │   ├── pages_users_to_main_service.py
│   │   │   ├── project_service.py
│   │   │   ├── refs_count_service.py
│   │   │   ├── translate_type_service.py
│   │   │   ├── user_service.py
│   │   │   ├── views_new_service.py
│   │   │   ├── word_service.py
│   │   ├── workers/
│   │       ├── post_worker.py
│   ├── shared/
│       ├── auth/
│       │   ├── decorators.py
│       │   ├── identity.py
│       ├── clients/
│       │   ├── mediawiki_api.py
│       │   ├── oauth_client.py
│       │   ├── revids_client.py
│       │   ├── wikidata_client.py
│       ├── core/
│       │   ├── cookies/
│       │   │   ├── cookie.py
│       │   ├── cors/
│       │   │   ├── check_cors_decorated.py
│       │   │   ├── cors_request_unit.py
│       │   │   ├── cors_wrappers.py
│       │   │   ├── cors_wrappers_and_headers.py
│       │   │   ├── is_allowed_checker_unit.py
│       │   │   ├── publish_secret_checks.py
│       │   ├── crypto.py
│       ├── services/
│       │   ├── category_service.py
│       │   ├── page_service.py
│       │   ├── qid_service.py
│       │   ├── report_service.py
│       │   ├── user_page_service.py
│       │   ├── user_token_service.py
│       ├── utils/
│           ├── decode_bytes.py
│           ├── helpers/
│           │   ├── files.py
│           │   ├── format.py
│           │   ├── text_processor.py
│           │   ├── words.py
│           │   ├── words_unit.py
```
