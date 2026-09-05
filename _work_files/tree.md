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
│   │   │   ├── translated/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── translated_main.py
│   │   │   │   ├── translated_shared_routes.py
│   │   │   │   └── translated_users.py
│   │   │   ├── __init__.py
│   │   │   ├── add_translate.py
│   │   │   ├── campaigns.py
│   │   │   ├── categories.py
│   │   │   ├── coordinators.py
│   │   │   ├── email_msg.py
│   │   │   ├── errors_route.py
│   │   │   ├── full_translators.py
│   │   │   ├── language_settings.py
│   │   │   ├── last.py
│   │   │   ├── pages_users_to_main.py
│   │   │   ├── projects.py
│   │   │   ├── settings.py
│   │   │   ├── stat.py
│   │   │   ├── tt.py
│   │   │   ├── users_emails.py
│   │   │   └── users_no_inprocess.py
│   │   ├── __init__.py
│   │   ├── admin_panel.py
│   │   ├── decorators.py
│   │   ├── flask_admin_panel.py
│   │   ├── flask_admin_panel_models.py
│   │   └── README.md
│   ├── config/
│   │   ├── __init__.py
│   │   ├── classes.py
│   │   ├── flask_config.py
│   │   ├── main_settings.py
│   │   └── README.md
│   ├── database/
│   │   ├── models/
│   │   │   ├── __init__.py
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
│   │   │   ├── pages/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── in_process_service.py
│   │   │   │   ├── leaderboard_service.py
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
│   │   │   │   ├── pages_users_to_main_service.py
│   │   │   │   └── report_service.py
│   │   │   ├── users/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── admin_service.py
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
│   │   ├── routes/
│   │   │   ├── api/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── form_utils.py
│   │   │   │   ├── objects.py
│   │   │   │   ├── routes.py
│   │   │   │   └── top_stats_routes.py
│   │   │   ├── cxtoken/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── cache.py
│   │   │   │   └── routes.py
│   │   │   ├── html_to_segments/
│   │   │   │   ├── config/
│   │   │   │   │   └── MWPageLoader.yaml
│   │   │   │   ├── lib/
│   │   │   │   │   ├── lineardoc/
│   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   ├── builder.py
│   │   │   │   │   │   ├── contextualizer.py
│   │   │   │   │   │   ├── doc.py
│   │   │   │   │   │   ├── doc_item.py
│   │   │   │   │   │   ├── elements.py
│   │   │   │   │   │   ├── mw_contextualizer.py
│   │   │   │   │   │   ├── normalizer.py
│   │   │   │   │   │   ├── parser.py
│   │   │   │   │   │   ├── README.md
│   │   │   │   │   │   ├── text_block.py
│   │   │   │   │   │   ├── text_chunk.py
│   │   │   │   │   │   ├── util.py
│   │   │   │   │   │   └── utils.py
│   │   │   │   │   ├── segmentation/
│   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   ├── cx_segmenter.py
│   │   │   │   │   │   └── README.md
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   └── processor.py
│   │   │   │   └── __init__.py
│   │   │   ├── main/
│   │   │   │   ├── __init__.py
│   │   │   │   └── routes.py
│   │   │   ├── new_html/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── README.md
│   │   │   │   └── routes.py
│   │   │   ├── publish/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── routes.py
│   │   │   │   ├── to_db.py
│   │   │   │   └── worker.py
│   │   │   ├── refs/
│   │   │   │   ├── __init__.py
│   │   │   │   └── routes.py
│   │   │   ├── td/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── leaderboard.py
│   │   │   │   ├── results_2026.py
│   │   │   │   ├── results_api.py
│   │   │   │   └── td_route.py
│   │   │   └── __init__.py
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
│   │   │   ├── __init__.py
│   │   │   ├── crypto.py
│   │   │   └── jinja_filters.py
│   │   ├── new_html_services/
│   │   │   ├── domain/
│   │   │   │   ├── fixes/
│   │   │   │   │   ├── media/
│   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   ├── fix_images.py
│   │   │   │   │   │   └── remove_missing_images.py
│   │   │   │   │   ├── references/
│   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   ├── delete_empty_refs.py
│   │   │   │   │   │   ├── expand_refs.py
│   │   │   │   │   │   └── ref_worker.py
│   │   │   │   │   ├── structure/
│   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   ├── fix_categories.py
│   │   │   │   │   │   └── fix_language_links.py
│   │   │   │   │   ├── templates/
│   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   ├── delete_templates.py
│   │   │   │   │   │   └── fix_templates.py
│   │   │   │   │   └── __init__.py
│   │   │   │   ├── parser/
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── citations_parser.py
│   │   │   │   │   ├── lead_section_parser.py
│   │   │   │   │   └── template_helpers.py
│   │   │   │   ├── __init__.py
│   │   │   │   ├── Domain_php_source.txt
│   │   │   │   └── README.md
│   │   │   ├── __init__.py
│   │   │   ├── clients.py
│   │   │   ├── html_utils.py
│   │   │   ├── process.py
│   │   │   ├── process_seg.py
│   │   │   ├── storage.py
│   │   │   └── utils.py
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
│   ├── templates_markups/
│   │   ├── admin_sidebar/
│   │   │   ├── __init__.py
│   │   │   ├── objects.py
│   │   │   ├── sidebar.py
│   │   │   └── sidebar_list.py
│   │   ├── navbar/
│   │   │   ├── __init__.py
│   │   │   ├── nav_bar.py
│   │   │   ├── navbar_list.py
│   │   │   └── objects.py
│   │   └── __init__.py
│   ├── __init__.py
│   ├── error_pages.py
│   ├── logger_config.py
│   └── README.md
├── results_api_php_code/
│   ├── backend/
│   │   ├── api_calls/
│   │   ├── results/
│   │   │   ├── new_way/
│   │   │   └── sparql_bots/
│   │   └── results_2026/
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
│   └── favicon.svg
├── templates/
│   ├── admin/
│   │   └── bs4_admin/
│   │       ├── file/
│   │       │   └── modals/
│   │       ├── model/
│   │       │   └── modals/
│   │       └── rediscli/
│   ├── admins/
│   │   ├── email_msg/
│   │   ├── last/
│   │   ├── qids/
│   │   ├── translated/
│   │   ├── tt/
│   │   └── users_emails/
│   ├── fixrefs/
│   ├── html_to_segments/
│   ├── new_html/
│   ├── results_2026/
│   └── td/
│       └── leaderboard/
├── __init__.py
├── app.py
└── README.md

```