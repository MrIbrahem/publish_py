```
src/
├── __init__.py
├── app.py
├── app_main/
│   ├── __init__.py
│   ├── admin/
│   │   ├── __init__.py
│   │   ├── domain/
│   │   │   ├── db/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── db_coordinators.py
│   │   │   │   ├── db_full_translators.py
│   │   │   │   ├── db_language_settings.py
│   │   │   │   ├── db_settings.py
│   │   │   │   ├── db_users_no_inprocess.py
│   │   │   │   └── schema.py
│   │   │   ├── db_ensure_tables.py
│   │   │   ├── models/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── coordinator.py
│   │   │   │   ├── full_translator.py
│   │   │   │   ├── language_setting.py
│   │   │   │   ├── setting.py
│   │   │   │   └── users_no_inprocess.py
│   │   │   └── services/
│   │   │       ├── __init__.py
│   │   │       ├── coordinators_service.py
│   │   │       ├── full_translators_service.py
│   │   │       ├── language_settings_service.py
│   │   │       ├── settings_service.py
│   │   │       └── users_no_inprocess_service.py
│   │   └── routes/
│   │       └── __init__.py
│   ├── config.py
│   ├── public/
│   │   ├── __init__.py
│   │   ├── domain/
│   │   │   ├── db/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── db_assessments.py
│   │   │   │   ├── db_enwiki_pageviews.py
│   │   │   │   ├── db_in_process.py
│   │   │   │   ├── db_langs.py
│   │   │   │   ├── db_mdwiki_revids.py
│   │   │   │   ├── db_pages_users_to_main.py
│   │   │   │   ├── db_projects.py
│   │   │   │   ├── db_refs_counts.py
│   │   │   │   ├── db_translate_type.py
│   │   │   │   ├── db_users.py
│   │   │   │   ├── db_views_new.py
│   │   │   │   ├── db_words.py
│   │   │   │   └── schema.py
│   │   │   ├── db_ensure_tables.py
│   │   │   ├── models/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── assessment.py
│   │   │   │   ├── enwiki_pageview.py
│   │   │   │   ├── in_process.py
│   │   │   │   ├── lang.py
│   │   │   │   ├── mdwiki_revid.py
│   │   │   │   ├── pages_users_to_main.py
│   │   │   │   ├── project.py
│   │   │   │   ├── refs_count.py
│   │   │   │   ├── translate_type.py
│   │   │   │   ├── user.py
│   │   │   │   ├── views_new.py
│   │   │   │   └── word.py
│   │   │   └── services/
│   │   │       ├── __init__.py
│   │   │       ├── assessments_service.py
│   │   │       ├── enwiki_pageviews_service.py
│   │   │       ├── in_process_service.py
│   │   │       ├── langs_service.py
│   │   │       ├── mdwiki_revids_service.py
│   │   │       ├── pages_users_to_main_service.py
│   │   │       ├── projects_service.py
│   │   │       ├── refs_counts_service.py
│   │   │       ├── translate_type_service.py
│   │   │       ├── users_service.py
│   │   │       ├── views_new_service.py
│   │   │       └── words_service.py
│   │   └── routes/
│   │       ├── __init__.py
│   │       ├── api/
│   │       │   ├── __init__.py
│   │       │   └── routes.py
│   │       ├── auth/
│   │       │   ├── __init__.py
│   │       │   ├── oauth.py
│   │       │   ├── rate_limit.py
│   │       │   └── routes.py
│   │       ├── cxtoken/
│   │       │   ├── __init__.py
│   │       │   ├── cache.py
│   │       │   └── routes.py
│   │       ├── main/
│   │       │   ├── __init__.py
│   │       │   └── routes.py
│   │       ├── publish/
│   │       │   ├── __init__.py
│   │       │   ├── routes.py
│   │       │   └── worker.py
│   │       └── refs/
│   │           ├── __init__.py
│   │           └── routes.py
│   └── shared/
│       ├── __init__.py
│       ├── auth/
│       │   ├── __init__.py
│       │   ├── decorators.py
│       │   └── identity.py
│       ├── clients/
│       │   ├── __init__.py
│       │   ├── mediawiki_api.py
│       │   ├── oauth_client.py
│       │   ├── revids_client.py
│       │   └── wikidata_client.py
│       ├── core/
│       │   ├── __init__.py
│       │   ├── cookies/
│       │   │   ├── __init__.py
│       │   │   ├── cookie.py
│       │   │   └── cookie_header_client.py
│       │   ├── cors/
│       │   │   ├── __init__.py
│       │   │   ├── is_allowed_checker.py
│       │   │   └── publish_secret_checks.py
│       │   ├── crypto.py
│       │   ├── db_driver.py
│       │   └── extensions.py
│       ├── domain/
│       │   ├── __init__.py
│       │   ├── db/
│       │   │   ├── __init__.py
│       │   │   ├── db_categories.py
│       │   │   ├── db_pages.py
│       │   │   ├── db_publish_reports.py
│       │   │   ├── db_qids.py
│       │   │   ├── db_user_tokens.py
│       │   │   └── schema.py
│       │   ├── db_ensure_tables.py
│       │   ├── models/
│       │   │   ├── __init__.py
│       │   │   ├── category.py
│       │   │   ├── page.py
│       │   │   ├── qid.py
│       │   │   ├── report.py
│       │   │   └── user_token.py
│       │   └── services/
│       │       ├── __init__.py
│       │       ├── categories_service.py
│       │       ├── db_service.py
│       │       ├── pages_service.py
│       │       ├── qids_service.py
│       │       └── users_services.py
│       ├── domain.zip
│       └── utils/
│           ├── __init__.py
│           ├── decode_bytes.py
│           ├── helpers/
│           │   ├── __init__.py
│           │   ├── files.py
│           │   ├── format.py
│           │   ├── text_processor.py
│           │   └── words.py
│           └── web_utils.py
├── env_config.py
├── logger_config.py
├── static/
└── templates/

```