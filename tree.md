```
src/
├── __init__.py
├── app.py
├── db_models/
│   ├── __init__.py
│   ├── admin_models.py
│   ├── public_models.py
│   └── shared_models.py
├── env_config.py
├── logger_config.py
├── sqlalchemy_app/
│   ├── __init__.py
│   ├── admin/
│   │   ├── __init__.py
│   │   ├── decorators.py
│   │   ├── models.py
│   │   ├── routes/
│   │   │   ├── __init__.py
│   │   │   ├── admin.py
│   │   │   ├── coordinators.py
│   │   │   ├── full_translators.py
│   │   │   ├── language_settings.py
│   │   │   ├── settings.py
│   │   │   └── users_no_inprocess.py
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── coordinator_service.py
│   │   │   ├── full_translator_service.py
│   │   │   ├── language_setting_service.py
│   │   │   ├── setting_service.py
│   │   │   └── users_no_inprocess_service.py
│   │   └── sidebar.py
│   ├── config.py
│   ├── db_models/
│   ├── public/
│   │   ├── __init__.py
│   │   ├── models.py
│   │   ├── routes/
│   │   │   ├── __init__.py
│   │   │   ├── api/
│   │   │   │   ├── __init__.py
│   │   │   │   └── routes.py
│   │   │   ├── auth/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── oauth.py
│   │   │   │   ├── rate_limit.py
│   │   │   │   └── routes.py
│   │   │   ├── cxtoken/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── cache.py
│   │   │   │   └── routes.py
│   │   │   ├── main/
│   │   │   │   ├── __init__.py
│   │   │   │   └── routes.py
│   │   │   ├── publish/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── routes.py
│   │   │   │   └── worker.py
│   │   │   └── refs/
│   │   │       ├── __init__.py
│   │   │       └── routes.py
│   │   └── services/
│   │       ├── __init__.py
│   │       ├── assessment_service.py
│   │       ├── enwiki_pageview_service.py
│   │       ├── in_process_service.py
│   │       ├── lang_service.py
│   │       ├── mdwiki_revid_service.py
│   │       ├── pages_users_to_main_service.py
│   │       ├── project_service.py
│   │       ├── refs_count_service.py
│   │       ├── translate_type_service.py
│   │       ├── user_service.py
│   │       ├── views_new_service.py
│   │       └── word_service.py
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
│       │   └── extensions.py
│       ├── engine.py
│       ├── models.py
│       ├── services/
│       │   ├── __init__.py
│       │   ├── category_service.py
│       │   ├── page_service.py
│       │   ├── qid_service.py
│       │   ├── report_service.py
│       │   ├── user_page_service.py
│       │   └── user_token_service.py
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
├── static/
│   ├── css/
│   │   ├── navbar.css
│   │   ├── sidebar-desktop.css
│   │   ├── sidebar-mobile.css
│   │   └── style.css
│   ├── images/
│   ├── js/
│   │   ├── autocomplete.js
│   │   ├── card-tools.js
│   │   ├── dark-mode.js
│   │   ├── sidebar.js
│   │   └── SVGLanguages.js
│   └── translate.svg
└── templates/
    └── admins/

```