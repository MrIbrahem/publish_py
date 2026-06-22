```
src/
├── main_app/
│   ├── admin/
│   │   ├── routes/
│   │   │   ├── qids/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── qids.py
│   │   │   │   ├── qids_model.py
│   │   │   │   └── qids_others.py
│   │   │   ├── __init__.py
│   │   │   ├── add_translate.py
│   │   │   ├── admin.py
│   │   │   ├── campaigns.py
│   │   │   ├── categories.py
│   │   │   ├── coordinators.py
│   │   │   ├── full_translators.py
│   │   │   ├── language_settings.py
│   │   │   ├── last.py
│   │   │   ├── pages_users_to_main.py
│   │   │   ├── projects.py
│   │   │   ├── settings.py
│   │   │   ├── stat.py
│   │   │   ├── translated.py
│   │   │   ├── translated_users.py
│   │   │   ├── tt.py
│   │   │   ├── users_emails.py
│   │   │   └── users_no_inprocess.py
│   │   ├── __init__.py
│   │   ├── decorators.py
│   │   ├── README.md
│   │   └── sidebar.py
│   ├── config/
│   │   ├── __init__.py
│   │   ├── classes.py
│   │   ├── flask_config.py
│   │   ├── main_settings.py
│   │   └── README.md
│   ├── db/
│   │   ├── models/
│   │   │   ├── analytics/
│   │   │   ├── config/
│   │   │   ├── content/
│   │   │   ├── pages/
│   │   │   ├── reports/
│   │   │   ├── users/
│   │   │   ├── wikidata/
│   │   │   ├── __init__.py
│   │   │   ├── all_articles.py
│   │   │   ├── category_members.py
│   │   │   ├── dashboard.py
│   │   │   ├── metrics.py
│   │   │   ├── pages.py
│   │   │   ├── public.py
│   │   │   ├── publish.py
│   │   │   ├── qid.py
│   │   │   ├── setting.py
│   │   │   ├── users.py
│   │   │   └── views.py
│   │   ├── services/
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
│   │   │   │   ├── leaderboard_service.py
│   │   │   │   ├── missing_stats_service.py
│   │   │   │   ├── page_service.py
│   │   │   │   ├── pages_users_to_main_service.py
│   │   │   │   ├── results_2026_service.py
│   │   │   │   ├── translate_type_service.py
│   │   │   │   └── user_page_service.py
│   │   │   ├── reports/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── pages_users_to_main_service.py
│   │   │   │   └── report_service.py
│   │   │   ├── users/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── admin_service.py
│   │   │   │   ├── full_translator_service.py
│   │   │   │   ├── user_service.py
│   │   │   │   ├── user_token_service.py
│   │   │   │   └── users_no_inprocess_service.py
│   │   │   ├── utils/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── db_guard_model.py
│   │   │   │   └── retry_on_disconnect.py
│   │   │   ├── wikidata/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── allqid_service.py
│   │   │   │   ├── qid_others_service.py
│   │   │   │   └── qid_service.py
│   │   │   ├── __init__.py
│   │   │   ├── _main_service.py
│   │   │   └── delete_service.py
│   │   ├── __init__.py
│   │   ├── exceptions.py
│   │   └── README.md
│   ├── public/
│   │   ├── routes/
│   │   │   ├── api/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── form_utils.py
│   │   │   │   ├── leaderboard.py
│   │   │   │   ├── pages_query_service.py
│   │   │   │   ├── routes.py
│   │   │   │   └── top_stats_routes.py
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
│   │   │   │   ├── leaderboard.py
│   │   │   │   ├── results_2026.py
│   │   │   │   ├── results_api.py
│   │   │   │   └── routes.py
│   │   │   ├── publish/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── routes.py
│   │   │   │   └── worker.py
│   │   │   ├── refs/
│   │   │   │   ├── __init__.py
│   │   │   │   └── routes.py
│   │   │   └── __init__.py
│   │   ├── __init__.py
│   │   └── README.md
│   ├── shared/
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
│   │   │   ├── cookies/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── cookie.py
│   │   │   │   └── cookie_header_client.py
│   │   │   ├── cors/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── is_allowed_checker.py
│   │   │   │   └── publish_secret_checks.py
│   │   │   ├── extensions/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── _csrf.py
│   │   │   │   └── data_base.py
│   │   │   ├── __init__.py
│   │   │   └── crypto.py
│   │   ├── schemas/
│   │   │   └── __init__.py
│   │   ├── utils/
│   │   │   ├── helpers/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── files.py
│   │   │   │   ├── format.py
│   │   │   │   ├── text_processor.py
│   │   │   │   └── words.py
│   │   │   ├── __init__.py
│   │   │   ├── decode_bytes.py
│   │   │   ├── web_utils.py
│   │   │   └── wiki_links.py
│   │   ├── __init__.py
│   │   └── README.md
│   ├── __init__.py
│   └── README.md
├── results_api_php_code/
│   ├── backend/
│   │   ├── api_calls/
│   │   │   └── mdwiki_sql.php
│   │   ├── results/
│   │   │   ├── new_way/
│   │   │   │   ├── get_results.php
│   │   │   │   └── query_results.php
│   │   │   ├── sparql_bots/
│   │   │   │   ├── sparql_bot.php
│   │   │   │   └── SPARQLDispatcher.php
│   │   │   └── getcats.php
│   │   ├── results_2026/
│   │   │   ├── get_results_2026.php
│   │   │   ├── include.php
│   │   │   ├── index.php
│   │   │   ├── results_table.php
│   │   │   ├── results_table_exists.php
│   │   │   └── results_table_inprocess.php
│   │   └── helps.php
│   ├── get_results_api.php
│   ├── include_all.php
│   ├── load_env.php
│   └── README.md
├── static/
│   ├── css/
│   │   ├── Chart.min.css
│   │   ├── dashboard_new1.css
│   │   ├── mobile_format.css
│   │   ├── navbar.css
│   │   ├── Responsive_Table.css
│   │   ├── sidebar-desktop.css
│   │   ├── sidebar-mobile.css
│   │   ├── style.css
│   │   ├── styles.css
│   │   ├── tdstyle.css
│   │   └── theme.css
│   ├── images/
│   ├── js/
│   │   ├── add_by_url.js
│   │   ├── autocomplate.js
│   │   ├── autocomplete.js
│   │   ├── c.js
│   │   ├── card-tools.js
│   │   ├── Chart.min.js
│   │   ├── codes.js
│   │   ├── color-modes.js
│   │   ├── dark-mode.js
│   │   ├── g.js
│   │   ├── graph_api.js
│   │   ├── leadtable.js
│   │   ├── main.js
│   │   ├── publish_reports.js
│   │   ├── sidebar.js
│   │   ├── sorttable.js
│   │   ├── SVGLanguages.js
│   │   ├── theme.js
│   │   └── to.js
│   ├── favicon.svg
│   └── translate.svg
├── templates/
│   ├── admins/
│   │   ├── last/
│   │   ├── qids/
│   │   ├── translated/
│   │   ├── tt/
│   │   └── users_emails/
│   ├── fixrefs/
│   ├── leaderboard/
│   └── results_2026/
├── __init__.py
├── app.py
├── logger_config.py
└── README.md

```