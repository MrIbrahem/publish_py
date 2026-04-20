```
src/
├── unit/
│   ├── admin/
│   │   ├── decorators.py
│   │   ├── models.py
│   │   ├── routes/
│   │   │   ├── admin.py
│   │   │   ├── coordinators.py
│   │   │   ├── full_translators.py
│   │   │   ├── language_settings.py
│   │   │   ├── settings.py
│   │   │   └── users_no_inprocess.py
│   │   ├── services/
│   │   │   ├── coordinator_service.py
│   │   │   ├── full_translator_service.py
│   │   │   ├── language_setting_service.py
│   │   │   ├── setting_service.py
│   │   │   └── users_no_inprocess_service.py
│   │   └── sidebar.py
│   ├── config.py
│   ├── public/
│   │   ├── models.py
│   │   ├── routes/
│   │   │   ├── api/
│   │   │   │   └── routes.py
│   │   │   ├── auth/
│   │   │   │   ├── oauth.py
│   │   │   │   ├── rate_limit.py
│   │   │   │   └── routes.py
│   │   │   ├── cxtoken/
│   │   │   │   ├── cache.py
│   │   │   │   └── routes.py
│   │   │   ├── main/
│   │   │   │   └── routes.py
│   │   │   ├── publish/
│   │   │   │   ├── routes.py
│   │   │   │   └── worker.py
│   │   │   └── refs/
│   │   │       └── routes.py
│   │   └── services/
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
│       ├── auth/
│       │   ├── decorators.py
│       │   └── identity.py
│       ├── clients/
│       │   ├── mediawiki_api.py
│       │   ├── oauth_client.py
│       │   ├── revids_client.py
│       │   └── wikidata_client.py
│       ├── core/
│       │   ├── cookies/
│       │   │   ├── cookie.py
│       │   │   └── cookie_header_client.py
│       │   ├── cors/
│       │   │   ├── is_allowed_checker.py
│       │   │   └── publish_secret_checks.py
│       │   ├── crypto.py
│       │   └── extensions.py
│       ├── db_models/
│       ├── engine.py
│       ├── models.py
│       ├── services/
│       │   ├── category_service.py
│       │   ├── page_service.py
│       │   ├── qid_service.py
│       │   ├── report_service.py
│       │   ├── user_page_service.py
│       │   └── user_token_service.py
│       └── utils/
│           ├── decode_bytes.py
│           ├── helpers/
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
