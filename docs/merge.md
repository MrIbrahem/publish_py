# Overview

# Code Sources

| Endpoint                            | status | Method    | Description                  | Source                                                                                                                                  |
| ----------------------------------- | ------ | --------- | ---------------------------- | --------------------------------------------------------------------------------------------------------------------------------------- |
| `/`                                 |        | GET       | Main entry                   | [Mdwiki-TD/mdwiki.toolforge.org](https://github.com/Mdwiki-TD/mdwiki.toolforge.org)                                                     |
| `/Translation_Dashboard`            |        | GET       | -                            | [Mdwiki-TD/Translation-Dashboard](https://github.com/Mdwiki-TD/Translation-Dashboard)                                                   |
| `/publish`, `/cxtoken` , `/reports` | ✔️     | POST      | Publish endpoint and Reports | [Mdwiki-TD/publish](https://github.com/Mdwiki-TD/publish)                                                                               |
| `/login`, `/logout`, `/callback`    | ✔️     | GET       | OAuth                        | [Mdwiki-TD/auth-repo](https://github.com/Mdwiki-TD/auth-repo)                                                                           |
| `/fixrefs`                          | ✔️     | GET, POST | Fix refs                     | [MrIbrahem/fix_refs_new_py](https://github.com/MrIbrahem/fix_refs_new_py) & [Mdwiki-TD/fix_refs](https://github.com/Mdwiki-TD/fix_refs) |
| `/api`                              |        | GET       | API                          | [Mdwiki-TD/TD_API](https://github.com/Mdwiki-TD/TD_API)                                                                                 |
| `/new_html`                         |        | GET       | -                            | [mdwikicx/new_html](https://github.com/mdwikicx/new_html)                                                                               |
| `/admin`                            |        | GET       | -                            | [Mdwiki-TD/tdc](https://github.com/Mdwiki-TD/tdc/)                                                                                      |

# End points

## Main entry

### Source Endpoints

| Endpoint        | Method | Description             |
| --------------- | ------ | ----------------------- |
| `/`             | GET    | Main entry              |
| `/fixwikirefs/` | GET    | Fix References tool     |
| `/views/`       | GET    | Pageviews Dashboard     |
| `/prior/`       | GET    | Prior List Dashboard    |
| `/WHO/`         | GET    | WHO Essential Medicines |
| `/gmail1/`      | POST   | Gmail Sender            |
| `/404.php`      | GET    | Custom 404 handler      |

### Flask Endpoints

| Route    | Method | Description                                        | Status | Source                                                                                  |
| -------- | ------ | -------------------------------------------------- | ------ | --------------------------------------------------------------------------------------- |
| `/`      | GET    | Homepage                                           | ✔️     |                                                                                         |
| `/views` | GET    | PageViews                                          |        |                                                                                         |
| `/prior` | GET    | Prior List                                         |        | [Source](https://github.com/Mdwiki-TD/mdwiki.toolforge.org/tree/main/public_html/prior) |
| `/WHO`   | GET    | World Health Organization essential medicines list |        | [Source](https://github.com/Mdwiki-TD/mdwiki.toolforge.org/tree/main/public_html/WHO)   |

---

## Translation Dashboard

### Source Endpoints

| Endpoint                                     | Method | Description                                                               |
| -------------------------------------------- | ------ | ------------------------------------------------------------------------- |
| `/`                                          | GET    | Main dashboard — search for missing translations by campaign and language |
| `/leaderboard.php`                           | GET    | Leaderboard — translation stats per user, language, and campaign          |
| `/leaderboard.php?get=users&user={user}`     | GET    | User-specific translation statistics                                      |
| `/leaderboard.php?get=langs&langcode={code}` | GET    | Language-specific translation statistics                                  |
| `/leaderboard.php?camps=1`                   | GET    | Campaign and article statistics tables                                    |
| `/leaderboard.php?graph=1`                   | GET    | Translation timeline graph (server-rendered)                              |
| `/leaderboard.php?graph_api=1`               | GET    | Translation timeline graph (API-driven JS)                                |
| `/missing.php`                               | GET    | Missing articles — top languages by missing article count                 |
| `/sitelinks.php`                             | GET    | Wikidata sitelinks report                                                 |
| `/translate.php`                             | GET    | Redirect to Content Translation tool                                      |
| `/x.php`                                     | GET    | AJAX-based leaderboard using DataTables                                   |
| `/auth.php`                                  | GET    | Redirect to authentication                                                |
| `/coordinator.php`                           | GET    | Redirect to coordinator tools                                             |
| `/404.php`                                   | GET    | 404 error page                                                            |

### Flask Endpoints

| Endpoint                                               | Method | Description             |
| ------------------------------------------------------ | ------ | ----------------------- |
| `/Translation_Dashboard/`                              | GET    | Dashboard index         |
| `/Translation_Dashboard/results_api`                   | GET    | Translation results API |
| `/Translation_Dashboard/table`                         | GET    | Translation table       |
| `/Translation_Dashboard/missing`                       | GET    | Missing translations    |
| `/Translation_Dashboard/leaderboard/`                  | GET    | Leaderboard index       |
| `/Translation_Dashboard/leaderboard/langs/<lang_code>` | GET    | Leaderboard by language |
| `/Translation_Dashboard/leaderboard/users/<username>`  | GET    | Leaderboard by user     |

---

## Publish

Manages the final steps in the process of publishing Wikipedia articles that have been translated using the [ContentTranslation tool](https://github.com/mdwikicx/cx-1) in [medwiki.toolforge.org](http://medwiki.toolforge.org/). It takes the translated text in wikitext format, refines it further, and then publishes it to Wikipedia.

### Source Endpoints

| source Endpoint     | Method | Description                                                             |
| ------------------- | ------ | ----------------------------------------------------------------------- |
| `/index.php`        | POST   | Publish a translated page to Wikipedia (requires `X-Secret-Key` header) |
| `/token.php`        | GET    | Get CSRF (cxtoken) for ContentTranslation on a target wiki              |
| `/publish_reports/` | GET    | Publish reports dashboard, grouped by year/month                        |

### Flask Endpoints

| Endpoint    | Method  | Description        |
| ----------- | ------- | ------------------ |
| `/cxtoken/` | GET     | CX Token page      |
| `/cxtoken/` | OPTIONS | CX Token preflight |
| `/publish/` | POST    | Publish article    |
| `/publish/` | OPTIONS | Publish preflight  |
| `/reports`  | GET     | Reports page       |

---

## OAuth

### Source Endpoints

| Endpoint                               | Method | Description                                                                     |
| -------------------------------------- | ------ | ------------------------------------------------------------------------------- |
| `/auth/` or `/auth/index.php`          | GET    | Auth status page — shows login link or authenticated username with logout       |
| `/auth/login.php` or `/?a=login`       | GET    | Initiate OAuth login — redirects to MediaWiki authorization page                |
| `/auth/callback.php` or `/?a=callback` | GET    | OAuth callback handler — completes auth, stores tokens, sets cookies, redirects |
| `/auth/logout.php` or `/?a=logout`     | GET    | Destroy session and clear cookies, then redirect                                |
| `/auth/get_user.php` or `/?a=get_user` | GET    | JSON API — returns `{"username": "..."}`                                        |

### Flask Endpoints

| Endpoint         | Method | Description           |
| ---------------- | ------ | --------------------- |
| `/auth/login`    | GET    | MediaWiki OAuth login |
| `/auth/callback` | GET    | OAuth callback        |
| `/auth/logout`   | GET    | Logout                |

---

## Fix refs

### Source Endpoints

| Endpoint         | Method | Description                                     |
| ---------------- | ------ | ----------------------------------------------- |
| `/`              | GET    | Main entry - web form for fixing references     |
| `/`              | POST   | Process a Wikipedia article by title & language |
| `/text_post.php` | POST   | Process raw wikitext (API-style)                |
| `/test.php`      | GET    | Test form with pre-filled sample data           |

### Flask Endpoints

| Endpoint           | Method | Description      |
| ------------------ | ------ | ---------------- |
| `/fixrefs/`        | GET    | Tool index       |
| `/fixrefs/`        | POST   | Process wikitext |
| `/fixrefs/test`    | GET    | Test page        |
| `/fixrefs/process` | GET    | Process page     |

---

## API

### Source Endpoints

| Endpoint                                    | Method | Description                                                                                  |
| ------------------------------------------- | ------ | -------------------------------------------------------------------------------------------- |
| `/`                                         | GET    | Main entry                                                                                   |
| `/api.php?get=assessments`                  | GET    | Article assessments with importance                                                          |
| `/api.php?get=categories`                   | GET    | Available categories with campaign mappings                                                  |
| `/api.php?get=category_members`             | GET    | Article IDs from a category membership table                                                 |
| `/api.php?get=coordinators`                 | GET    | List of coordinators with active status                                                      |
| `/api.php?get=count_pages`                  | GET    | Count of targets per user, ordered descending                                                |
| `/api.php?get=enwiki_pageviews`             | GET    | English Wikipedia page views                                                                 |
| `/api.php?get=exists_by_lang_and_category`  | GET    | Articles that exist in a specific language + category                                        |
| `/api.php?get=exists_statics_by_category`   | GET    | Statistics of articles that exist per language for a category                                |
| `/api.php?get=full_translators`             | GET    | Full translators with active status                                                          |
| `/api.php?get=graph_data`                   | GET    | Monthly page publication counts                                                              |
| `/api.php?get=in_process`                   | GET    | In-process translations with campaign and language info                                      |
| `/api.php?get=lang_views2`                  | GET    | Page views filtered by language (alias)                                                      |
| `/api.php?get=lang_views`                   | GET    | Page views filtered by language                                                              |
| `/api.php?get=langs`                        | GET    | All languages with code, autonym, name, redirects                                            |
| `/api.php?get=language_settings`            | GET    | Language settings with distinct values                                                       |
| `/api.php?get=leaderboard_table_formated`   | GET    | Formatted leaderboard (by_lang, by_user, by_month)                                           |
| `/api.php?get=leaderboard_table`            | GET    | Raw leaderboard data (pages, users, words, views)                                            |
| `/api.php?get=missing_by_lang_and_category` | GET    | Articles missing translation in a specific language + category                               |
| `/api.php?get=missing`                      | GET    | Articles missing translation in all languages for a category                                 |
| `/api.php?get=pages_by_user_or_lang`        | GET    | Pages filtered by user or language with views                                                |
| `/api.php?get=pages_langs`                  | GET    | Languages used in the pages table                                                            |
| `/api.php?get=pages_users_langs`            | GET    | Languages used in the pages_users table                                                      |
| `/api.php?get=pages_users_to_main`          | GET    | Join of pages_users_to_main with pages_users                                                 |
| `/api.php?get=pages_users`                  | GET    | Pages from pages_users table                                                                 |
| `/api.php?get=pages_with_views`             | GET    | Pages with views (redirects to pages)                                                        |
| `/api.php?get=pages`                        | GET    | Pages with full details (title, word, translate_type, cat, lang, user, target, dates, views) |
| `/api.php?get=projects`                     | GET    | Project groups                                                                               |
| `/api.php?get=publish_reports_stats`        | GET    | Publication reports stats by year/month/lang/user/result                                     |
| `/api.php?get=publish_reports`              | GET    | Publication reports with selectable fields                                                   |
| `/api.php?get=qids_others`                  | GET    | Additional Wikidata QIDs                                                                     |
| `/api.php?get=qids`                         | GET    | Wikidata QIDs (supports `dis` param)                                                         |
| `/api.php?get=refs_counts`                  | GET    | Reference counts (lead and all) per title                                                    |
| `/api.php?get=revids`                       | GET    | MDWiki revision IDs for titles                                                               |
| `/api.php?get=settings`                     | GET    | System configuration settings                                                                |
| `/api.php?get=statics_by_category`          | GET    | Count of existing articles grouped by language for a category                                |
| `/api.php?get=status`                       | GET    | Page publication counts by month (optional filters)                                          |
| `/api.php?get=titles`                       | GET    | Page titles with assessments, refs, views, QIDs, words                                       |
| `/api.php?get=top_lang_of_users`            | GET    | Top language per user (by page count)                                                        |
| `/api.php?get=top_langs`                    | GET    | Top languages by targets, words, views                                                       |
| `/api.php?get=top_users`                    | GET    | Top users by targets, words, views                                                           |
| `/api.php?get=translate_type`               | GET    | Translation types (lead/full)                                                                |
| `/api.php?get=user_access`                  | GET    | Access keys with usernames                                                                   |
| `/api.php?get=user_lang_status`             | GET    | User status by language (redirects to user_status)                                           |
| `/api.php?get=user_status`                  | GET    | User status by language with year/select options                                             |
| `/api.php?get=user_views2`                  | GET    | Page views filtered by a specific user (alias)                                               |
| `/api.php?get=user_views`                   | GET    | Page views filtered by a specific user                                                       |
| `/api.php?get=users_by_last_pupdate`        | GET    | Users with their latest page update                                                          |
| `/api.php?get=users_no_inprocess`           | GET    | Users without in-process articles                                                            |
| `/api.php?get=users`                        | GET    | List of usernames (supports `userlike` filter)                                               |
| `/api.php?get=views_new`                    | GET    | Page views from views_new_all table                                                          |
| `/api.php?get=views`                        | GET    | Page view stats joined with pages                                                            |
| `/api.php?get=words`                        | GET    | Word counts for page titles (lead and all words)                                             |

### Flask Endpoints

| Endpoint                           | Method | Description                |
| ---------------------------------- | ------ | -------------------------- |
| `/api/publish_reports`             | GET    | Publish reports data       |
| `/api/publish_reports/stats`       | GET    | Publish reports stats      |
| `/api/in_process`                  | GET    | In-process pages           |
| `/api/in_process_total`            | GET    | In-process total count     |
| `/api/pages_users`                 | GET    | Pages per user             |
| `/api/pages_with_views`            | GET    | Pages with view counts     |
| `/api/categories`                  | GET    | Categories                 |
| `/api/distinct_langs`              | GET    | Distinct languages         |
| `/api/users_by_translations_count` | GET    | Users by translation count |
| `/api/langs`                       | GET    | Languages list             |
| `/api/users`                       | GET    | Users list                 |
| `/api/status`                      | GET    | Leaderboard status         |
| `/api/top_langs`                   | GET    | Top languages              |
| `/api/top_users`                   | GET    | Top users                  |

---

## Admin

### Source Endpoints

| Endpoint             | Method   | Description                                             |
| -------------------- | -------- | ------------------------------------------------------- |
| `/`                  | GET      | Main entry — recent translations dashboard              |
| `?ty=reports`        | GET      | View publish reports with filters                       |
| `?ty=stat`           | GET      | Per-category article statistics                         |
| `?ty=sidebar`        | GET      | Sidebar HTML (for AJAX reload)                          |
| `?ty=categories`     | GET      | Translation languages with Wikidata category status     |
| `?ty=Campaigns`      | GET/POST | List and edit translation campaigns                     |
| `?ty=Campaigns/post` | POST     | Save/update/delete campaign categories                  |
| `?ty=projects`       | GET/POST | Manage project groups                                   |
| `?ty=projects/post`  | POST     | Save project changes                                    |
| `?ty=settings`       | GET/POST | Manage application settings                             |
| `?ty=settings/post`  | POST     | Save settings changes                                   |
| `sugust.php`         | GET      | JSON endpoint for article suggestions (`?title=&lang=`) |

#### Recent translations

| Endpoint                         | Method   | Description                              |
| -------------------------------- | -------- | ---------------------------------------- |
| `?ty=last`                       | GET      | Recent translations table                |
| `?ty=last1`                      | GET      | Recent translations (SQL-based)          |
| `?ty=process`                    | GET      | Translations currently in progress       |
| `?ty=process_total`              | GET      | Per-user translation count summary       |
| `?ty=last_coord`                 | GET      | Coordinator view of recent translations  |
| `?ty=recent_helps`               | GET      | Helper utilities for recent translations |
| `?ty=pages_users_to_main`        | GET      | Pages needing move to main namespace     |
| `?ty=pages_users_to_main/fix_it` | GET/POST | Edit page transfer details               |

#### Pages

| Endpoint                     | Method   | Description                            |
| ---------------------------- | -------- | -------------------------------------- |
| `?ty=translated`             | GET      | Paginated list of all translated pages |
| `?ty=translated/edit_page`   | GET/POST | Edit or delete a translated page       |
| `?ty=tt`                     | GET      | List articles by translate type        |
| `?ty=tt/edit_translate_type` | GET/POST | Edit or add translate type             |
| `?ty=tt/post`                | POST     | Save translate type changes            |
| `?ty=add`                    | GET/POST | Add new translation entries            |
| `?ty=add/post`               | POST     | Save new translation rows              |

#### Qids

| Endpoint            | Method   | Description             |
| ------------------- | -------- | ----------------------- |
| `?ty=qids`          | GET      | List Wikidata QIDs      |
| `?ty=qids/edit_qid` | GET/POST | Edit or add a QID entry |
| `?ty=qids/post`     | POST     | Save QID changes        |

#### Users

| Endpoint                      | Method   | Description                                |
| ----------------------------- | -------- | ------------------------------------------ |
| `?ty=Emails`                  | GET/POST | List users with emails and project filters |
| `?ty=Emails/post`             | POST     | Save user email/wiki/project edits         |
| `?ty=Emails/msg`              | GET/POST | Compose and send email to translator       |
| `?ty=Emails/edit_user`        | GET      | Edit or add a single user                  |
| `?ty=users_no_inprocess`      | GET/POST | Manage users excluded from "in process"    |
| `?ty=users_no_inprocess/post` | POST     | Save exclusion list changes                |

#### Roles Management

| Endpoint                    | Method   | Description                     |
| --------------------------- | -------- | ------------------------------- |
| `?ty=admins`                | GET/POST | List, add, delete coordinators  |
| `?ty=admins/post`           | POST     | Save coordinator changes        |
| `?ty=full_translators`      | GET/POST | Manage full article translators |
| `?ty=full_translators/post` | POST     | Save full translator changes    |

#### Language Settings

| Endpoint                    | Method   | Description                        |
| --------------------------- | -------- | ---------------------------------- |
| `?ty=wikirefs_options`      | GET      | Per-language fix wikirefs settings |
| `?ty=wikirefs_options/edit` | GET/POST | Edit language settings             |

### Flask Endpoints

| Endpoint                         | Method | Description                   |
| -------------------------------- | ------ | ----------------------------- |
| `/admin/`                        | GET    | Admin panel index             |
| `/admin/last`                    | GET    | Last dashboard                |
| `/admin/last/pages/<lang>`       | GET    | Dashboard pages by lang       |
| `/admin/last/pages/`             | GET    | Dashboard all pages           |
| `/admin/last/pages_users/<lang>` | GET    | Dashboard pages/users by lang |
| `/admin/last/pages_users/`       | GET    | Dashboard all pages/users     |
| `/admin/reports`                 | GET    | Admin reports                 |
| `/admin/process`                 | GET    | In-process dashboard          |
| `/admin/process_total`           | GET    | In-process total dashboard    |
| `/admin/edit_done`               | GET    | Edit done page                |
| `/admin/categories`              | GET    | Categories dashboard          |

#### Users

| Endpoint                                    | Method | Description                    |
| ------------------------------------------- | ------ | ------------------------------ |
| `/admin/coordinators/`                      | GET    | Coordinators dashboard         |
| `/admin/coordinators/add`                   | POST   | Add coordinator                |
| `/admin/coordinators/<id>/activate`         | POST   | Activate coordinator           |
| `/admin/coordinators/<id>/deactivate`       | POST   | Deactivate coordinator         |
| `/admin/coordinators/<id>/delete`           | POST   | Delete coordinator             |
| `/admin/full_translators/`                  | GET    | Full translators dashboard     |
| `/admin/full_translators/add`               | POST   | Add full translator            |
| `/admin/full_translators/<id>/delete`       | POST   | Delete full translator         |
| `/admin/full_translators/<id>/activate`     | POST   | Activate translator record     |
| `/admin/full_translators/<id>/deactivate`   | POST   | Deactivate translator record   |
| `/admin/users_no_inprocess/`                | GET    | No-inprocess users dashboard   |
| `/admin/users_no_inprocess/add`             | POST   | Add no-inprocess user          |
| `/admin/users_no_inprocess/<id>/delete`     | POST   | Delete no-inprocess user       |
| `/admin/users_no_inprocess/<id>/activate`   | POST   | Activate no-inprocess record   |
| `/admin/users_no_inprocess/<id>/deactivate` | POST   | Deactivate no-inprocess record |

#### Language Settings

| Endpoint                               | Method | Description        |
| -------------------------------------- | ------ | ------------------ |
| `/admin/language_settings/`            | GET    | Settings dashboard |
| `/admin/language_settings/add`         | POST   | Add setting        |
| `/admin/language_settings/<id>/update` | POST   | Update setting     |
| `/admin/language_settings/<id>/delete` | POST   | Delete setting     |

#### Translation Tools

| Endpoint                       | Method | Description                 |
| ------------------------------ | ------ | --------------------------- |
| `/admin/add/`                  | GET    | Add translation form        |
| `/admin/add/`                  | POST   | Add translation submit      |
| `/admin/tt/`                   | GET    | Translation tools index     |
| `/admin/tt/`                   | POST   | Edit translation tool       |
| `/admin/tt/edit`               | GET    | Edit translation tool form  |
| `/admin/tt/add`                | GET    | Add translation tool form   |
| `/admin/tt/add`                | POST   | Add translation tool submit |
| `/admin/translated/`           | GET    | Translated pages index      |
| `/admin/translated/edit`       | GET    | Edit translated page        |
| `/admin/translated/edit`       | POST   | Edit translated page submit |
| `/admin/translated_users/`     | GET    | Translated users index      |
| `/admin/translated_users/edit` | GET    | Edit translated user        |
| `/admin/translated_users/edit` | POST   | Edit translated user submit |

#### Communications

| Endpoint                                              | Method | Description              |
| ----------------------------------------------------- | ------ | ------------------------ |
| `/admin/email_msg/dashboard/<last_table>/<id>`        | GET    | Email message dashboard  |
| `/admin/email_msg/dashboard/<last_table>/<id>/<user>` | GET    | Email dashboard for user |
| `/admin/email_msg/send`                               | POST   | Send email message       |
| `/admin/users_emails/`                                | GET    | Users emails dashboard   |
| `/admin/users_emails/add`                             | POST   | Add user email           |
| `/admin/users_emails/<id>/delete`                     | POST   | Delete user email        |
| `/admin/users_emails/<id>/update`                     | POST   | Update user email        |
| `/admin/users_emails/<id>/edit`                       | GET    | Edit user email form     |

#### QIDs

| Endpoint                  | Method | Description           |
| ------------------------- | ------ | --------------------- |
| `/admin/qids/`            | GET    | QIDs index            |
| `/admin/qids/`            | POST   | Edit QID submit       |
| `/admin/qids/edit`        | GET    | Edit QID form         |
| `/admin/qids/add`         | GET    | Add QID form          |
| `/admin/qids/add`         | POST   | Add QID submit        |
| `/admin/qids_others/`     | GET    | Other QIDs index      |
| `/admin/qids_others/`     | POST   | Edit other QID submit |
| `/admin/qids_others/edit` | GET    | Edit other QID form   |
| `/admin/qids_others/add`  | GET    | Add other QID form    |
| `/admin/qids_others/add`  | POST   | Add other QID submit  |

#### Utilities

| Endpoint                            | Method | Description               |
| ----------------------------------- | ------ | ------------------------- |
| `/admin/pages_users_to_main/`       | GET    | Pages-users to main index |
| `/admin/pages_users_to_main/fix_it` | GET    | Fix pages-users form      |
| `/admin/pages_users_to_main/fix_it` | POST   | Fix pages-users submit    |
| `/admin/stat/`                      | GET    | Statistics dashboard      |
| `/admin/settings/`                  | GET    | Settings dashboard        |
| `/admin/settings/create`            | POST   | Create setting            |
| `/admin/settings/update`            | POST   | Update setting            |
| `/admin/projects/`                  | GET    | Projects dashboard        |
| `/admin/projects/add`               | POST   | Add project               |
| `/admin/projects/update`            | POST   | Update project            |
| `/admin/campaigns/`                 | GET    | Campaigns dashboard       |
| `/admin/campaigns/add`              | POST   | Add campaign              |
| `/admin/campaigns/update`           | POST   | Update campaign           |
