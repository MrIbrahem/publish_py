```
src/
├── main_app/
│   ├── admin/
│   │   ├── __init__.py
│   │   ├── coordinators.py
│   │   ├── decorators.py
│   │   ├── errors_route.py
│   │   ├── flask_admin_panel.py
│   │   ├── flask_admin_panel_models.py
│   │   └── settings.py
│   ├── app_services/
│   │   ├── new_html_services/
│   │   │   ├── clients/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── local_rest_json_repository.py
│   │   │   │   ├── mdwiki_api.py
│   │   │   │   ├── mdwiki_rest_fallback_service.py
│   │   │   │   └── transform_service.py
│   │   │   ├── parser/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── citation.py
│   │   │   │   ├── citations_parser.py
│   │   │   │   ├── lead_section_parser.py
│   │   │   │   └── template_helpers.py
│   │   │   ├── process/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── html_service.py
│   │   │   │   ├── mapping.py
│   │   │   │   ├── process_seg.py
│   │   │   │   └── processer.py
│   │   │   ├── utils/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── files_utils.py
│   │   │   │   └── html_utils.py
│   │   │   ├── wikitext_fixes/
│   │   │   │   ├── media/
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── fix_images.py
│   │   │   │   │   └── remove_missing_images.py
│   │   │   │   ├── references/
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── delete_empty_refs.py
│   │   │   │   │   ├── expand_refs.py
│   │   │   │   │   └── ref_worker.py
│   │   │   │   ├── structure/
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── fix_categories.py
│   │   │   │   │   └── fix_language_links.py
│   │   │   │   ├── templates/
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── delete_templates.py
│   │   │   │   │   └── fix_templates.py
│   │   │   │   ├── __init__.py
│   │   │   │   └── wikitext_fixer.py
│   │   │   ├── __init__.py
│   │   │   ├── README.md
│   │   │   └── storage.py
│   │   ├── results_2026/
│   │   │   ├── data/
│   │   │   │   ├── __init__.py
│   │   │   │   └── results_fetcher.py
│   │   │   ├── helpers/
│   │   │   │   ├── __init__.py
│   │   │   │   └── translate_type_loader.py
│   │   │   ├── mapping/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── exists_mapping.py
│   │   │   │   ├── inprocess_mapping.py
│   │   │   │   ├── missing_mapping.py
│   │   │   │   └── shared_mapping.py
│   │   │   ├── tables/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── exists_table.py
│   │   │   │   ├── in_process_table.py
│   │   │   │   └── missing_table.py
│   │   │   ├── __init__.py
│   │   │   ├── bundle.py
│   │   │   └── results_loader.py
│   │   └── __init__.py
│   ├── config/
│   │   ├── __init__.py
│   │   ├── classes.py
│   │   ├── flask_config.py
│   │   ├── main_settings.py
│   │   └── README.md
│   ├── coordinators/
│   │   ├── routes/
│   │   │   ├── msg/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── email_msg.py
│   │   │   │   └── view.py
│   │   │   ├── qids/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── qids.py
│   │   │   │   ├── qids_model.py
│   │   │   │   └── qids_others.py
│   │   │   ├── translated/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── translated_main.py
│   │   │   │   ├── translated_shared_routes.py
│   │   │   │   └── translated_users.py
│   │   │   ├── __init__.py
│   │   │   ├── add_translate.py
│   │   │   ├── campaigns.py
│   │   │   ├── categories.py
│   │   │   ├── full_translators.py
│   │   │   ├── language_settings.py
│   │   │   ├── last.py
│   │   │   ├── pages_users_to_main.py
│   │   │   ├── projects.py
│   │   │   ├── stat.py
│   │   │   ├── tt.py
│   │   │   ├── users_emails.py
│   │   │   └── users_no_inprocess.py
│   │   ├── __init__.py
│   │   ├── coordinator_panel.py
│   │   └── decorators.py
│   ├── database/
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── admin_users.py
│   │   │   ├── base.py
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
│   │   │   │   └── settings_service.py
│   │   │   ├── content/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── category_member_service.py
│   │   │   │   ├── category_service.py
│   │   │   │   ├── lang_service.py
│   │   │   │   └── project_service.py
│   │   │   ├── others/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── api_service.py
│   │   │   │   ├── leaderboard_service.py
│   │   │   │   └── top_stats_service.py
│   │   │   ├── pages/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── in_process_service.py
│   │   │   │   ├── missing_stats_service.py
│   │   │   │   ├── pages_query_service.py
│   │   │   │   ├── pages_users_to_main_service.py
│   │   │   │   ├── results_2026_service.py
│   │   │   │   └── translate_type_service.py
│   │   │   ├── pages_tables/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── page_service.py
│   │   │   │   ├── pages_shared_service.py
│   │   │   │   └── user_page_service.py
│   │   │   ├── reports/
│   │   │   │   ├── __init__.py
│   │   │   │   └── report_service.py
│   │   │   ├── users/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── admin_service.py
│   │   │   │   ├── coordinator_service.py
│   │   │   │   ├── full_translator_service.py
│   │   │   │   ├── user_token_service.py
│   │   │   │   ├── users_no_inprocess_service.py
│   │   │   │   └── users_service.py
│   │   │   ├── utils/
│   │   │   │   ├── __init__.py
│   │   │   │   └── retry_on_disconnect.py
│   │   │   ├── wikidata/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── allqid_service.py
│   │   │   │   ├── qid_others_service.py
│   │   │   │   ├── qid_service.py
│   │   │   │   └── qid_shared_service.py
│   │   │   ├── __init__.py
│   │   │   └── crud_service.py
│   │   ├── __init__.py
│   │   ├── create_helper.py
│   │   ├── exceptions.py
│   │   └── README.md
│   ├── extensions/
│   │   ├── __init__.py
│   │   ├── _csrf.py
│   │   ├── data_base.py
│   │   └── db_types.py
│   ├── public/
│   │   ├── auth/
│   │   │   ├── __init__.py
│   │   │   ├── decorators.py
│   │   │   ├── rate_limit.py
│   │   │   └── routes.py
│   │   ├── mapping/
│   │   │   ├── __init__.py
│   │   │   └── forms_mapping.py
│   │   ├── routes/
│   │   │   ├── api/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── mapping.py
│   │   │   │   ├── routes.py
│   │   │   │   └── top_stats_routes.py
│   │   │   ├── cxtoken/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── cache.py
│   │   │   │   └── routes.py
│   │   │   ├── main/
│   │   │   │   ├── __init__.py
│   │   │   │   └── routes.py
│   │   │   ├── publish/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── error_resolver.py
│   │   │   │   ├── report_recorder.py
│   │   │   │   ├── routes.py
│   │   │   │   ├── to_db.py
│   │   │   │   ├── wikidata_linker.py
│   │   │   │   └── worker.py
│   │   │   ├── refs/
│   │   │   │   ├── __init__.py
│   │   │   │   └── routes.py
│   │   │   ├── td/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── leaderboard.py
│   │   │   │   ├── leaderboard_mapping.py
│   │   │   │   ├── results_api.py
│   │   │   │   ├── td_route.py
│   │   │   │   └── translate_med.py
│   │   │   ├── __init__.py
│   │   │   ├── html2segments.py
│   │   │   ├── legacy_compat.py
│   │   │   └── new_html.py
│   │   ├── utils/
│   │   │   ├── __init__.py
│   │   │   └── routes_utils.py
│   │   ├── __init__.py
│   │   └── README.md
│   ├── services/
│   │   ├── auth/
│   │   │   ├── __init__.py
│   │   │   ├── auth_exceptions.py
│   │   │   ├── auth_service.py
│   │   │   ├── current_user.py
│   │   │   ├── flow.py
│   │   │   ├── token_manager.py
│   │   │   └── utils.py
│   │   ├── clients/
│   │   │   ├── __init__.py
│   │   │   ├── http_client.py
│   │   │   ├── mediawiki_api.py
│   │   │   ├── oauth_client.py
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
│   │   │   ├── __init__.py
│   │   │   ├── crypto.py
│   │   │   └── jinja_filters.py
│   │   ├── schemas/
│   │   │   └── __init__.py
│   │   ├── segments_wraper/
│   │   │   └── __init__.py
│   │   ├── utils/
│   │   │   ├── helpers/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── files.py
│   │   │   │   ├── format.py
│   │   │   │   └── text_processor.py
│   │   │   ├── __init__.py
│   │   │   ├── decode_bytes.py
│   │   │   ├── views_links.py
│   │   │   ├── web_utils.py
│   │   │   └── wiki_links.py
│   │   ├── __init__.py
│   │   └── README.md
│   ├── templates_markups/
│   │   ├── coordinator_sidebar/
│   │   │   ├── __init__.py
│   │   │   ├── mapping.py
│   │   │   ├── sidebar.py
│   │   │   └── sidebar_list.py
│   │   ├── navbar/
│   │   │   ├── __init__.py
│   │   │   ├── mapping.py
│   │   │   ├── nav_bar.py
│   │   │   └── td_navbar_list.py
│   │   └── __init__.py
│   ├── __init__.py
│   ├── error_pages.py
│   ├── logger_config.py
│   └── README.md
├── static/
│   ├── css/
│   │   ├── Chart.min.css
│   │   ├── dashboard_new1.css
│   │   ├── mobile_format.css
│   │   ├── navbar.css
│   │   ├── sidebar-desktop.css
│   │   ├── sidebar-mobile.css
│   │   ├── style.css
│   │   ├── styles.css
│   │   ├── tdstyle.css
│   │   └── theme.css
│   ├── images/
│   ├── js/
│   │   ├── add_by_url.js
│   │   ├── card-tools.js
│   │   ├── Chart.min.js
│   │   ├── dark-mode.js
│   │   ├── graph.js
│   │   ├── html_to_segments.js
│   │   ├── publish_reports.js
│   │   ├── sidebar.js
│   │   ├── td_autocomplete.js
│   │   └── views_api.js
│   ├── favicon.ico
│   ├── favicon.svg
│   └── xtools.svg
├── templates/
│   ├── admin/
│   │   ├── base.html
│   │   └── index_with_sidebar.html
│   ├── coordinators/
│   │   ├── email_msg/
│   │   │   ├── index.html
│   │   │   └── msg_template.html
│   │   ├── last/
│   │   │   └── index.html
│   │   ├── qids/
│   │   │   ├── edit.html
│   │   │   └── index.html
│   │   ├── translated/
│   │   │   ├── edit.html
│   │   │   └── index.html
│   │   ├── tt/
│   │   │   ├── edit.html
│   │   │   └── index.html
│   │   ├── users_emails/
│   │   │   ├── edit.html
│   │   │   └── index.html
│   │   ├── _sidebar.html
│   │   ├── add_translate.html
│   │   ├── base1.html
│   │   ├── base1_no_navbar.html
│   │   ├── campaigns.html
│   │   ├── categories.html
│   │   ├── close_btn.html
│   │   ├── coordinators.html
│   │   ├── errors.html
│   │   ├── full_translators.html
│   │   ├── in_process.html
│   │   ├── in_process_total.html
│   │   ├── index.html
│   │   ├── language_settings.html
│   │   ├── pages_users_to_main.html
│   │   ├── pages_users_to_main_fix_it.html
│   │   ├── projects.html
│   │   ├── reports.html
│   │   ├── settings.html
│   │   ├── stat.html
│   │   └── users_no_inprocess.html
│   ├── fixrefs/
│   │   └── index.html
│   ├── html_to_segments/
│   │   ├── index.html
│   │   └── list.html
│   ├── new_html/
│   │   ├── fix.html
│   │   └── revisions.html
│   ├── td/
│   │   ├── leaderboard/
│   │   │   ├── index-js.html
│   │   │   ├── index.html
│   │   │   ├── langs.html
│   │   │   └── users.html
│   │   ├── results_2026/
│   │   │   ├── exists_table.html
│   │   │   ├── inprocess_table.html
│   │   │   ├── missing_table.html
│   │   │   └── results_card.html
│   │   ├── form.html
│   │   ├── index.html
│   │   ├── missing.html
│   │   ├── td_base.html
│   │   ├── td_navbar.html
│   │   └── translate_med.html
│   ├── _macros.html
│   ├── _navbar.html
│   ├── base.html
│   ├── error.html
│   ├── index.html
│   ├── index_db_error.html
│   └── reports.html
├── __init__.py
├── app.py
├── bootstrap.py
└── README.md

```