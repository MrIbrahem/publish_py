```
tests/
│
├── integration/
│   │
│   ├── admin/
│   │   ├── test_coordinators_routes_integration.py
│   │   └── test_settings_routes_integration.py
│   │
│   ├── app_services/
│   │
│   ├── coordinators/
│   │   │
│   │   └── routes/
│   │       │
│   │       ├── qids/
│   │       │
│   │       ├── translated/
│   │       │
│   │       ├── test_admin_routes_integration.py
│   │       ├── test_full_translators_routes_integration.py
│   │       ├── test_language_settings_routes_integration.py
│   │       └── test_users_no_inprocess_routes_integration.py
│   │
│   ├── database/
│   │   │
│   │   └── services/
│   │       └── test_pages_service_integration.py
│   │
│   ├── public/
│   │   │
│   │   ├── auth/
│   │   │
│   │   └── routes/
│   │       │
│   │       ├── api/
│   │       │   └── test_api_routes.py
│   │       │
│   │       ├── auth/
│   │       │   └── test_auth_routes.py
│   │       │
│   │       ├── cxtoken/
│   │       │   ├── test_cxtoken_cors_disabled.py
│   │       │   ├── test_cxtoken_cors_on.py
│   │       │   └── test_cxtoken_routes.py
│   │       │
│   │       ├── html_to_segments/
│   │       │   │
│   │       │   └── lib/
│   │       │       │
│   │       │       ├── lineardoc/
│   │       │       │
│   │       │       └── segmentation/
│   │       │
│   │       ├── main/
│   │       │   └── test_main_routes.py
│   │       │
│   │       ├── publish/
│   │       │   ├── test_publish_cors_disabled.py
│   │       │   ├── test_publish_cors_on.py
│   │       │   ├── test_publish_csrf_integration.py
│   │       │   └── test_publish_routes.py
│   │       │
│   │       ├── refs/
│   │       │   └── test_refs_routes.py
│   │       │
│   │       └── td/
│   │           ├── test_td_routes_integration.py
│   │           └── test_translate_med_integration.py
│   │
│   └── services/
│       │
│       └── core/
│           │
│           └── cors/
│               ├── test_is_allowed_checker.py
│               └── test_main_routes_with_cors.py
│
├── unit/
│   │
│   ├── admin/
│   │   └── test_settings_routes.py
│   │
│   ├── app_routes/
│   │   │
│   │   └── auth/
│   │       ├── test_auth_utils.py
│   │       └── test_identity.py
│   │
│   ├── app_services/
│   │   │
│   │   ├── new_html_services/
│   │   │   │
│   │   │   ├── clients/
│   │   │   │
│   │   │   ├── parser/
│   │   │   │   │
│   │   │   │   ├── data/
│   │   │   │   │   └── source-1.wiki
│   │   │   │   │
│   │   │   │   ├── test_citation.py
│   │   │   │   ├── test_citations_parser.py
│   │   │   │   ├── test_lead_section_parser.py
│   │   │   │   └── test_template_helpers.py
│   │   │   │
│   │   │   ├── process/
│   │   │   │   ├── test_process_seg.py
│   │   │   │   └── test_processer.py
│   │   │   │
│   │   │   ├── utils/
│   │   │   │   ├── test_html_utils.py
│   │   │   │   └── test_services_utils.py
│   │   │   │
│   │   │   ├── wikitext_fixes/
│   │   │   │   │
│   │   │   │   ├── fixtures/
│   │   │   │   │   │
│   │   │   │   │   ├── result/
│   │   │   │   │   │   ├── abdominal_pain.wiki
│   │   │   │   │   │   ├── obstructive_sleep_apnea.wiki
│   │   │   │   │   │   ├── test-1.wiki
│   │   │   │   │   │   ├── test-2.wiki
│   │   │   │   │   │   ├── Uterine_atony.wiki
│   │   │   │   │   │   └── Wernicke–Korsakoff_syndrome.wiki
│   │   │   │   │   │
│   │   │   │   │   └── source/
│   │   │   │   │       ├── abdominal_pain.wiki
│   │   │   │   │       ├── obstructive_sleep_apnea.wiki
│   │   │   │   │       ├── test-1.wiki
│   │   │   │   │       ├── test-2.wiki
│   │   │   │   │       ├── Uterine_atony.wiki
│   │   │   │   │       └── Wernicke–Korsakoff_syndrome.wiki
│   │   │   │   │
│   │   │   │   ├── media/
│   │   │   │   │   ├── test_fix_images.py
│   │   │   │   │   └── test_remove_missing_images.py
│   │   │   │   │
│   │   │   │   ├── references/
│   │   │   │   │   ├── test_delete_empty_refs.py
│   │   │   │   │   ├── test_expand_refs.py
│   │   │   │   │   └── test_ref_worker.py
│   │   │   │   │
│   │   │   │   ├── structure/
│   │   │   │   │   ├── test_fix_categories.py
│   │   │   │   │   └── test_fix_language_links.py
│   │   │   │   │
│   │   │   │   ├── templates/
│   │   │   │   │   ├── test_delete_templates.py
│   │   │   │   │   └── test_fix_templates.py
│   │   │   │   │
│   │   │   │   └── test_wikitext_fixer.py
│   │   │   │
│   │   │   ├── __init__.py
│   │   │   ├── expend_infobox.py
│   │   │   └── test_storage.py
│   │   │
│   │   ├── results_2026/
│   │   │   │
│   │   │   ├── data/
│   │   │   │
│   │   │   ├── helpers/
│   │   │   │
│   │   │   ├── mapping/
│   │   │   │
│   │   │   ├── tables/
│   │   │   │
│   │   │   ├── __init__.py
│   │   │   └── test_row_items.py
│   │   │
│   │   └── __init__.py
│   │
│   ├── config/
│   │
│   ├── coordinators/
│   │   │
│   │   └── routes/
│   │       │
│   │       ├── msg/
│   │       │
│   │       ├── qids/
│   │       │
│   │       ├── translated/
│   │       │
│   │       ├── test_admin_routes.py
│   │       ├── test_full_translators_routes.py
│   │       ├── test_language_settings_routes.py
│   │       └── test_users_no_inprocess_routes.py
│   │
│   ├── database/
│   │   │
│   │   ├── models/
│   │   │   │
│   │   │   ├── analytics/
│   │   │   │   ├── test_assessment_model.py
│   │   │   │   ├── test_enwiki_pageview_model.py
│   │   │   │   ├── test_mdwiki_revid_model.py
│   │   │   │   ├── test_refs_count_model.py
│   │   │   │   ├── test_views_new_model.py
│   │   │   │   └── test_word_model.py
│   │   │   │
│   │   │   ├── config/
│   │   │   │   ├── test_language_setting_model.py
│   │   │   │   └── test_setting_model.py
│   │   │   │
│   │   │   ├── content/
│   │   │   │   ├── test_category_model.py
│   │   │   │   ├── test_lang_model.py
│   │   │   │   └── test_project_model.py
│   │   │   │
│   │   │   ├── pages/
│   │   │   │   ├── test_in_process_model.py
│   │   │   │   ├── test_page_model.py
│   │   │   │   └── test_translate_type_model.py
│   │   │   │
│   │   │   ├── reports/
│   │   │   │   ├── test_pages_users_to_main_model.py
│   │   │   │   └── test_report_model.py
│   │   │   │
│   │   │   ├── users/
│   │   │   │   ├── test_coordinator_model.py
│   │   │   │   ├── test_full_translator_model.py
│   │   │   │   ├── test_user_model.py
│   │   │   │   ├── test_user_token_model.py
│   │   │   │   └── test_users_no_inprocess_model.py
│   │   │   │
│   │   │   └── wikidata/
│   │   │       └── test_qid_model.py
│   │   │
│   │   ├── services/
│   │   │   │
│   │   │   ├── analytics/
│   │   │   │   ├── test_assessment_service.py
│   │   │   │   ├── test_enwiki_pageview_service.py
│   │   │   │   ├── test_mdwiki_revid_service.py
│   │   │   │   ├── test_refs_count_service.py
│   │   │   │   ├── test_views_new_service.py
│   │   │   │   └── test_word_service.py
│   │   │   │
│   │   │   ├── config/
│   │   │   │   ├── test_language_setting_service.py
│   │   │   │   └── test_settings_service.py
│   │   │   │
│   │   │   ├── content/
│   │   │   │   ├── test_category_service.py
│   │   │   │   ├── test_lang_service.py
│   │   │   │   └── test_project_service.py
│   │   │   │
│   │   │   ├── others/
│   │   │   │
│   │   │   ├── pages/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── test_chart_data.py
│   │   │   │   ├── test_in_process_service.py
│   │   │   │   ├── test_pages_users_to_main_service_admin.py
│   │   │   │   └── test_translate_type_service.py
│   │   │   │
│   │   │   ├── pages_tables/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── pages_shared_service_tests.py
│   │   │   │   ├── test_page_service.py
│   │   │   │   └── test_user_page_service.py
│   │   │   │
│   │   │   ├── reports/
│   │   │   │   └── test_report_service.py
│   │   │   │
│   │   │   ├── users/
│   │   │   │   ├── test_admin_service.py
│   │   │   │   ├── test_full_translator_service.py
│   │   │   │   ├── test_user_token_service.py
│   │   │   │   ├── test_users_no_inprocess_service.py
│   │   │   │   └── test_users_service.py
│   │   │   │
│   │   │   ├── utils/
│   │   │   │
│   │   │   ├── wikidata/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── qids_services_tests.py
│   │   │   │   ├── test_allqid_service.py
│   │   │   │   ├── test_qid_others_service.py
│   │   │   │   └── test_qid_service.py
│   │   │   │
│   │   │   └── __init__.py
│   │   │
│   │   └── __init__.py
│   │
│   ├── extensions/
│   │
│   ├── public/
│   │   │
│   │   ├── auth/
│   │   │   └── test_routes.py
│   │   │
│   │   ├── mapping/
│   │   │
│   │   ├── routes/
│   │   │   │
│   │   │   ├── api/
│   │   │   │   └── test_api_routes_unit.py
│   │   │   │
│   │   │   ├── auth/
│   │   │   │   └── test_rate_limit.py
│   │   │   │
│   │   │   ├── cxtoken/
│   │   │   │   └── test_cxtoken_cache.py
│   │   │   │
│   │   │   ├── main/
│   │   │   │
│   │   │   ├── publish/
│   │   │   │   └── test_error_resolver.py
│   │   │   │
│   │   │   ├── refs/
│   │   │   │
│   │   │   ├── td/
│   │   │   │
│   │   │   ├── test_html2segments.py
│   │   │   ├── test_legacy_url_redirects.py
│   │   │   └── test_new_html_routes.py
│   │   │
│   │   └── utils/
│   │
│   ├── services/
│   │   │
│   │   ├── auth/
│   │   │   ├── test_auth_service.py
│   │   │   └── test_token_manager.py
│   │   │
│   │   ├── clients/
│   │   │   ├── test_http_client.py
│   │   │   ├── test_mediawiki_api.py
│   │   │   ├── test_oauth_client.py
│   │   │   ├── test_text_api.py
│   │   │   └── test_wikidata_client.py
│   │   │
│   │   ├── core/
│   │   │   │
│   │   │   ├── cookies/
│   │   │   │   └── test_cookie.py
│   │   │   │
│   │   │   ├── cors/
│   │   │   │   ├── test_check_cors_decorated.py
│   │   │   │   ├── test_cors_request_unit.py
│   │   │   │   ├── test_cors_wrappers.py
│   │   │   │   ├── test_cors_wrappers_and_headers.py
│   │   │   │   ├── test_is_allowed_checker_unit.py
│   │   │   │   └── test_publish_secret_checks.py
│   │   │   │
│   │   │   ├── test_crypto.py
│   │   │   └── test_extensions.py
│   │   │
│   │   ├── schemas/
│   │   │
│   │   ├── segments_wraper/
│   │   │
│   │   └── utils/
│   │       │
│   │       ├── helpers/
│   │       │   ├── test_files.py
│   │       │   ├── test_format.py
│   │       │   └── test_text_processor.py
│   │       │
│   │       ├── test_decode_bytes.py
│   │       └── test_web_utils.py
│   │
│   ├── templates_markups/
│   │   │
│   │   ├── coordinator_sidebar/
│   │   │
│   │   ├── navbar/
│   │   │
│   │   └── test_coordinator_sidebar.py
│   │
│   └── __init__.py
│
├── __init__.py
├── conftest.py
└── README.md

```