```
src/
├── __init__.py
├── app.py
├── logger_config.py
├── main_app/
│   ├── __init__.py
│   ├── admin/
│   │   ├── __init__.py
│   │   ├── decorators.py
│   │   ├── routes/
│   │   │   ├── __init__.py
│   │   │   ├── admin.py
│   │   │   ├── campaigns.py
│   │   │   ├── coordinators.py
│   │   │   ├── full_translators.py
│   │   │   ├── language_settings.py
│   │   │   ├── last.py
│   │   │   ├── projects.py
│   │   │   ├── settings.py
│   │   │   ├── users_emails.py
│   │   │   └── users_no_inprocess.py
│   │   └── sidebar.py
│   ├── config.py
│   ├── public/
│   │   ├── __init__.py
│   │   └── routes/
│   │       ├── __init__.py
│   │       ├── api/
│   │       │   ├── __init__.py
│   │       │   ├── pages_query_service.py
│   │       │   ├── routes.py
│   │       │   └── top_stats_routes.py
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
│   │       │   ├── leaderboard.py
│   │       │   ├── results_api.py
│   │       │   └── routes.py
│   │       ├── publish/
│   │       │   ├── __init__.py
│   │       │   ├── routes.py
│   │       │   └── worker.py
│   │       └── refs/
│   │           ├── __init__.py
│   │           └── routes.py
│   ├── shared/
│   │   ├── __init__.py
│   │   ├── auth/
│   │   │   ├── __init__.py
│   │   │   ├── decorators.py
│   │   │   └── identity.py
│   │   ├── clients/
│   │   │   ├── __init__.py
│   │   │   ├── mdwiki_api.py
│   │   │   ├── mediawiki_api.py
│   │   │   ├── oauth_client.py
│   │   │   ├── revids_client.py
│   │   │   ├── text_api.py
│   │   │   └── wikidata_client.py
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   ├── cookies/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── cookie.py
│   │   │   │   └── cookie_header_client.py
│   │   │   ├── cors/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── is_allowed_checker.py
│   │   │   │   └── publish_secret_checks.py
│   │   │   ├── crypto.py
│   │   │   └── extensions.py
│   │   ├── engine.py
│   │   ├── schemas/
│   │   │   └── __init__.py
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── analytics/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── assessment_service.py
│   │   │   │   ├── enwiki_pageview_service.py
│   │   │   │   ├── mdwiki_revid_service.py
│   │   │   │   ├── refs_count_service.py
│   │   │   │   ├── views_new_service.py
│   │   │   │   └── word_service.py
│   │   │   ├── config/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── language_setting_service.py
│   │   │   │   └── setting_service.py
│   │   │   ├── content/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── category_service.py
│   │   │   │   ├── lang_service.py
│   │   │   │   └── project_service.py
│   │   │   ├── pages/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── in_process_service.py
│   │   │   │   ├── page_service.py
│   │   │   │   ├── translate_type_service.py
│   │   │   │   └── user_page_service.py
│   │   │   ├── reports/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── pages_users_to_main_service.py
│   │   │   │   └── report_service.py
│   │   │   ├── users/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── coordinator_service.py
│   │   │   │   ├── full_translator_service.py
│   │   │   │   ├── user_service.py
│   │   │   │   ├── user_token_service.py
│   │   │   │   └── users_no_inprocess_service.py
│   │   │   ├── wikidata/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── allqid_service.py
│   │   │   │   └── qid_service.py
│   │   │   └── z.md
│   │   └── utils/
│   │       ├── __init__.py
│   │       ├── decode_bytes.py
│   │       ├── helpers/
│   │       │   ├── __init__.py
│   │       │   ├── files.py
│   │       │   ├── format.py
│   │       │   ├── text_processor.py
│   │       │   └── words.py
│   │       └── web_utils.py
│   └── sqlalchemy_models/
│       ├── __init__.py
│       ├── all_articles.py
│       ├── dashboard.py
│       ├── metrics.py
│       ├── pages.py
│       ├── public.py
│       ├── publish.py
│       ├── qid.py
│       ├── setting.py
│       ├── users.py
│       └── views.py
├── results_api_php_code/
│   ├── backend/
│   │   ├── api_calls/
│   │   │   └── mdwiki_sql.php
│   │   ├── helps.php
│   │   └── results/
│   │       ├── getcats.php
│   │       ├── new_way/
│   │       │   ├── get_results.php
│   │       │   └── query_results.php
│   │       └── sparql_bots/
│   │           ├── sparql_bot.php
│   │           └── SPARQLDispatcher.php
│   ├── get_results_api.php
│   ├── include_all.php
│   └── load_env.php
├── static/
│   ├── css/
│   │   ├── navbar.css
│   │   ├── sidebar-desktop.css
│   │   ├── sidebar-mobile.css
│   │   ├── style.css
│   │   └── tdstyle.css
│   ├── favicon.svg
│   ├── images/
│   ├── js/
│   │   ├── autocomplete.js
│   │   ├── card-tools.js
│   │   ├── dark-mode.js
│   │   ├── publish_reports.js
│   │   ├── sidebar.js
│   │   └── SVGLanguages.js
│   └── translate.svg
└── templates/
    ├── admins/
    ├── fixrefs/
    └── leaderboard/

```