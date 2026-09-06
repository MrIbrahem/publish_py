```
tests/
├── integration/
│   ├── admin/
│   │   └── routes/
│   │       ├── qids/
│   │       ├── translated/
│   │       ├── test_admin_routes_integration.py
│   │       ├── test_coordinators_routes_integration.py
│   │       ├── test_full_translators_routes_integration.py
│   │       ├── test_language_settings_routes_integration.py
│   │       ├── test_settings_routes_integration.py
│   │       └── test_users_no_inprocess_routes_integration.py
│   ├── main_app/
│   │   ├── admin/
│   │   │   └── routes/
│   │   │       └── qids/
│   │   └── public/
│   │       ├── auth/
│   │       └── routes/
│   │           ├── api/
│   │           ├── cxtoken/
│   │           ├── main/
│   │           ├── publish/
│   │           ├── refs/
│   │           └── td/
│   ├── public/
│   │   ├── auth/
│   │   └── routes/
│   │       ├── api/
│   │       │   └── test_api_routes.py
│   │       ├── auth/
│   │       │   └── test_auth_routes.py
│   │       ├── cxtoken/
│   │       │   ├── test_cxtoken_cors_disabled.py
│   │       │   ├── test_cxtoken_cors_on.py
│   │       │   └── test_cxtoken_routes.py
│   │       ├── html_to_segments/
│   │       │   └── lib/
│   │       │       ├── lineardoc/
│   │       │       └── segmentation/
│   │       ├── main/
│   │       │   └── test_main_routes.py
│   │       ├── publish/
│   │       │   ├── test_publish_cors_disabled.py
│   │       │   ├── test_publish_cors_on.py
│   │       │   ├── test_publish_csrf_integration.py
│   │       │   └── test_publish_routes.py
│   │       ├── refs/
│   │       │   └── test_refs_routes.py
│   │       └── td/
│   └── services/
│       ├── core/
│       │   └── cors/
│       │       ├── test_is_allowed_checker.py
│       │       └── test_main_routes_with_cors.py
│       └── services/
│           └── test_pages_service_integration.py
├── unit/
│   ├── admin/
│   │   └── routes/
│   │       ├── qids/
│   │       ├── translated/
│   │       ├── test_admin_routes.py
│   │       ├── test_coordinators_routes.py
│   │       ├── test_full_translators_routes.py
│   │       ├── test_language_settings_routes.py
│   │       ├── test_settings_routes.py
│   │       └── test_users_no_inprocess_routes.py
│   ├── app_routes/
│   │   └── auth/
│   │       ├── test_auth_utils.py
│   │       └── test_identity.py
│   ├── config/
│   ├── database/
│   │   ├── models/
│   │   │   ├── analytics/
│   │   │   │   ├── test_assessment_model.py
│   │   │   │   ├── test_enwiki_pageview_model.py
│   │   │   │   ├── test_mdwiki_revid_model.py
│   │   │   │   ├── test_refs_count_model.py
│   │   │   │   ├── test_views_new_model.py
│   │   │   │   └── test_word_model.py
│   │   │   ├── config/
│   │   │   │   ├── test_language_setting_model.py
│   │   │   │   └── test_setting_model.py
│   │   │   ├── content/
│   │   │   │   ├── test_category_model.py
│   │   │   │   ├── test_lang_model.py
│   │   │   │   └── test_project_model.py
│   │   │   ├── pages/
│   │   │   │   ├── test_in_process_model.py
│   │   │   │   ├── test_page_model.py
│   │   │   │   └── test_translate_type_model.py
│   │   │   ├── reports/
│   │   │   │   ├── test_pages_users_to_main_model.py
│   │   │   │   └── test_report_model.py
│   │   │   ├── users/
│   │   │   │   ├── test_coordinator_model.py
│   │   │   │   ├── test_full_translator_model.py
│   │   │   │   ├── test_user_model.py
│   │   │   │   ├── test_user_token_model.py
│   │   │   │   └── test_users_no_inprocess_model.py
│   │   │   └── wikidata/
│   │   │       └── test_qid_model.py
│   │   └── services/
│   │       ├── analytics/
│   │       │   ├── test_assessment_service.py
│   │       │   ├── test_enwiki_pageview_service.py
│   │       │   ├── test_mdwiki_revid_service.py
│   │       │   ├── test_refs_count_service.py
│   │       │   ├── test_views_new_service.py
│   │       │   └── test_word_service.py
│   │       ├── config/
│   │       │   ├── test_language_setting_service.py
│   │       │   └── test_settings_service.py
│   │       ├── content/
│   │       │   ├── test_category_service.py
│   │       │   ├── test_lang_service.py
│   │       │   └── test_project_service.py
│   │       ├── pages/
│   │       │   ├── test_chart_data.py
│   │       │   ├── test_in_process_service.py
│   │       │   ├── test_page_service.py
│   │       │   ├── test_pages_users_to_main_service_admin.py
│   │       │   ├── test_translate_type_service.py
│   │       │   └── test_user_page_service.py
│   │       ├── pages_tables/
│   │       ├── reports/
│   │       │   ├── test_pages_users_to_main_service.py
│   │       │   └── test_report_service.py
│   │       ├── users/
│   │       │   ├── test_admin_service.py
│   │       │   ├── test_full_translator_service.py
│   │       │   ├── test_user_token_service.py
│   │       │   ├── test_users_no_inprocess_service.py
│   │       │   └── test_users_service.py
│   │       ├── utils/
│   │       └── wikidata/
│   │           ├── test_allqid_service.py
│   │           ├── test_qid_others_service.py
│   │           └── test_qid_service.py
│   ├── extensions/
│   ├── main_app/
│   │   ├── admin/
│   │   ├── config/
│   │   ├── db/
│   │   │   ├── models/
│   │   │   └── services/
│   │   │       ├── analytics/
│   │   │       ├── config/
│   │   │       ├── content/
│   │   │       ├── pages/
│   │   │       ├── reports/
│   │   │       ├── users/
│   │   │       ├── utils/
│   │   │       └── wikidata/
│   │   ├── extensions/
│   │   ├── public/
│   │   │   ├── auth/
│   │   │   └── utils/
│   │   └── shared/
│   │       ├── auth/
│   │       ├── clients/
│   │       ├── core/
│   │       │   ├── cookies/
│   │       │   └── cors/
│   │       ├── schemas/
│   │       └── utils/
│   │           └── helpers/
│   ├── public/
│   │   ├── auth/
│   │   │   └── test_routes.py
│   │   ├── routes/
│   │   │   ├── api/
│   │   │   │   └── test_api_routes_unit.py
│   │   │   ├── auth/
│   │   │   │   └── test_rate_limit.py
│   │   │   ├── cxtoken/
│   │   │   │   └── test_cxtoken_cache.py
│   │   │   ├── html_to_segments/
│   │   │   │   ├── lib/
│   │   │   │   │   ├── lineardoc/
│   │   │   │   │   │   ├── data/
│   │   │   │   │   │   ├── test_builder.py
│   │   │   │   │   │   ├── test_contextualizer.py
│   │   │   │   │   │   ├── test_doc.py
│   │   │   │   │   │   ├── test_doc_item.py
│   │   │   │   │   │   ├── test_elements.py
│   │   │   │   │   │   ├── test_lineardoc_utils.py
│   │   │   │   │   │   ├── test_mw_contextualizer.py
│   │   │   │   │   │   ├── test_normalizer.py
│   │   │   │   │   │   ├── test_parser.py
│   │   │   │   │   │   ├── test_text_block.py
│   │   │   │   │   │   ├── test_text_chunk.py
│   │   │   │   │   │   └── test_util.py
│   │   │   │   │   ├── segmentation/
│   │   │   │   │   │   └── test_cx_segmenter.py
│   │   │   │   │   └── test_processor.py
│   │   │   │   └── test_html_to_segments_init.py
│   │   │   ├── main/
│   │   │   ├── new_html/
│   │   │   │   └── test_new_html_routes.py
│   │   │   ├── publish/
│   │   │   │   └── test_publish_worker.py
│   │   │   ├── refs/
│   │   │   └── td/
│   │   └── utils/
│   ├── services/
│   │   ├── auth/
│   │   │   ├── test_auth_service.py
│   │   │   └── test_token_manager.py
│   │   ├── clients/
│   │   │   ├── test_mdwiki_api.py
│   │   │   ├── test_mediawiki_api.py
│   │   │   ├── test_oauth_client.py
│   │   │   ├── test_revids_client.py
│   │   │   ├── test_text_api.py
│   │   │   └── test_wikidata_client.py
│   │   ├── core/
│   │   │   ├── cookies/
│   │   │   │   └── test_cookie.py
│   │   │   ├── cors/
│   │   │   │   ├── test_check_cors_decorated.py
│   │   │   │   ├── test_cors_request_unit.py
│   │   │   │   ├── test_cors_wrappers.py
│   │   │   │   ├── test_cors_wrappers_and_headers.py
│   │   │   │   ├── test_is_allowed_checker_unit.py
│   │   │   │   └── test_publish_secret_checks.py
│   │   │   ├── test_crypto.py
│   │   │   └── test_extensions.py
│   │   ├── new_html_services/
│   │   │   ├── domain/
│   │   │   │   ├── fixes/
│   │   │   │   │   ├── data/
│   │   │   │   │   │   ├── output-2.wiki
│   │   │   │   │   │   ├── result-1.wiki
│   │   │   │   │   │   ├── result-2.wiki
│   │   │   │   │   │   ├── source-1.wiki
│   │   │   │   │   │   └── source-2.wiki
│   │   │   │   │   ├── media/
│   │   │   │   │   │   ├── test_fix_images.py
│   │   │   │   │   │   └── test_remove_missing_images.py
│   │   │   │   │   ├── references/
│   │   │   │   │   │   ├── test_delete_empty_refs.py
│   │   │   │   │   │   ├── test_expand_refs.py
│   │   │   │   │   │   └── test_ref_worker.py
│   │   │   │   │   ├── structure/
│   │   │   │   │   │   ├── test_fix_categories.py
│   │   │   │   │   │   └── test_fix_language_links.py
│   │   │   │   │   ├── templates/
│   │   │   │   │   │   ├── test_delete_templates.py
│   │   │   │   │   │   └── test_fix_templates.py
│   │   │   │   │   ├── test_fixtures/
│   │   │   │   │   │   ├── local.wiki.txt
│   │   │   │   │   │   └── mwikicx.wiki.txt
│   │   │   │   │   └── test_fixes_init.py
│   │   │   │   └── parser/
│   │   │   │       ├── test_citations_parser.py
│   │   │   │       ├── test_lead_section_parser.py
│   │   │   │       └── test_template_helpers.py
│   │   │   ├── test_clients.py
│   │   │   ├── test_html_utils.py
│   │   │   ├── test_process.py
│   │   │   ├── test_process_seg.py
│   │   │   ├── test_services_utils.py
│   │   │   └── test_storage.py
│   │   ├── schemas/
│   │   └── utils/
│   │       ├── helpers/
│   │       │   ├── test_files.py
│   │       │   ├── test_format.py
│   │       │   ├── test_text_processor.py
│   │       │   ├── test_words.py
│   │       │   └── test_words_unit.py
│   │       ├── test_decode_bytes.py
│   │       └── test_web_utils.py
│   └── templates_markups/
│       ├── admin_sidebar/
│       ├── navbar/
│       └── test_admin_sidebar.py
├── __init__.py
├── conftest.py
└── README.md

```