## 87

-   This pull request introduces a development-only bypass for the coordinator authorization check (controlled by the <code>UI_TEST_BYPASS_COORDINATOR_CHECK</code> environment variable) to facilitate local development and automated UI testing without requiring a real database entry in the coordinators table. This bypass is strictly restricted to run only under <code>DevelopmentConfig</code>. Feedback on the pull request highlights an issue in the newly added unit tests: the tests assert that <code>is_active_coordinator</code> and <code>active_coordinators</code> respect the bypass, but these functions do not actually implement the bypass logic, which will cause the tests to fail. It is recommended to either integrate the bypass check into those functions or adjust the test assertions accordingly. [#87](https://github.com/MrIbrahem/publish_py/pull/87)

## 86

-   This pull request refactors the administrator check logic by storing the <code>is_active_admin</code> flag directly on the <code>CurrentUser</code> dataclass, removing the need to query and cache <code>active_coordinators</code> during the request lifecycle. Feedback on the changes highlights that several test cases in <code>tests/conftest.py</code> and <code>tests/integration/admin/routes/test_admin_routes_integration.py</code> attempt to patch <code>active_coordinators</code> within the decorators module where it is no longer imported, which will result in <code>AttributeError</code>s. The reviewer recommends setting the <code>is_active_admin</code> attribute directly on the mocked user instances instead. [#86](https://github.com/MrIbrahem/publish_py/pull/86)

## 85

-   This pull request restructures the application's routing by introducing a dedicated Translation Dashboard (<code>td</code>) blueprint, refactoring the admin panel routes, and removing several unused static assets and scripts. Feedback on the changes highlights critical issues, including potential type mismatches when handling database settings, a bug that hides the translation button due to a boolean-to-string comparison mismatch, and potential JavaScript syntax errors from wrapping JSON-serialized chart data in single quotes. Additionally, the reviewer noted missing default values or empty checks for query parameters, a copy-paste error in the users API exception logging, and multiple potential <code>TypeError</code> crashes in <code>publish_reports.js</code> if date fields are null or undefined when calling <code>split()</code>. [#85](https://github.com/MrIbrahem/publish_py/pull/85)

## 82

-   This pull request refactors and enhances the admin email message dashboard, introducing dynamic translation suggestions, HTML email templates, and support for CC'ing the sender. It also adds a sidebar persistence feature using local storage. The review feedback highlights several critical issues: a bug in <code>make_sugustion</code> where passing integer <code>0</code> triggers incorrect default behavior, a potential rendering issue in <code>create_email_msg</code> when suggestions are missing, a potential <code>TypeError</code> in <code>sidebar.js</code> if the toggle element is absent, a missing check for empty targets before querying page views, and a CSS typo (<code>hight</code> instead of <code>height</code>) in the email template. [#82](https://github.com/MrIbrahem/publish_py/pull/82)

## 81

-   This pull request refactors database models by removing <code>BaseModel</code> inheritance, introducing explicit <code>**init**</code> and <code>to_dict</code> methods, and extracting publishing database logic into a dedicated <code>to_db.py</code> module. It also centralizes custom Jinja filters into <code>jinja_filters.py</code> and updates templates to use these filters and macros. Feedback on these changes highlights critical bugs, including potential <code>UnboundLocalError</code> exceptions in the new <code>to_db.py</code> functions when records are missing, and an undefined context variable (<code>yesterday</code>) in the <code>pageviews_link</code> macro. Additionally, the review points out a misleading docstring and potential <code>TypeError</code> in the timestamp formatting filter, along with widespread incorrect type annotations for <code>\*\*kwargs</code> across several models and services. [#81](https://github.com/MrIbrahem/publish_py/pull/81)

## 80

-   This pull request migrates multiple database models to SQLAlchemy 2.0's modern declarative mapping style using <code>Mapped</code> and <code>mapped_column</code>. The review feedback highlights several instances where annotating columns as <code>Mapped[int]</code> implicitly changes their database constraints to <code>NOT NULL</code> (e.g., <code>move_dots</code>, <code>en_views</code>, and <code>views</code>). To preserve the existing schema, these should be annotated as <code>Mapped[int | None]</code>. Additionally, the <code>is_active</code> column in <code>AdminUserRecord</code> should use <code>default=1</code> instead of <code>default=True</code> to maintain type consistency with its <code>Mapped[int]</code> annotation. [#80](https://github.com/MrIbrahem/publish_py/pull/80)

## 79

-   This pull request refactors the database models and services, introducing a centralized <code>delete_service.py</code> for record deletions, renaming <code>CoordinatorRecord</code> to <code>AdminUserRecord</code>, and adding database utility decorators like <code>db_guard</code> and <code>retry_on_db_disconnect</code>. Feedback on these changes highlights several critical issues: exception handling in settings updates and deletions is bypassed because the underlying services catch exceptions and return booleans instead of raising them; the <code>active_coordinators</code> cache is not cleared when updating a coordinator's active status, posing a security risk; null settings can be incorrectly converted to the string 'None'; a potential <code>AttributeError</code> exists if a coordinator is not found during deletion; the retry decorator may cause <code>DetachedInstanceError</code> by detaching ORM instances; and <code>AdminUserRecord</code>'s custom <code>**init**</code> fails to call <code>super().**init**(\*\*kwargs)</code>. [#79](https://github.com/MrIbrahem/publish_py/pull/79)

## 78

-   This pull request introduces comprehensive reference documentation for mwclient operations (covering error handling, images, listings, pages, and site operations) and applies extensive code formatting, import sorting, and minor cleanup across the codebase. Feedback on the changes highlights a type annotation mismatch in form_utils.py where the user field is annotated as an integer but parsed as a string, as well as a potential file resource leak in an upload code example within the newly added image documentation. [#78](https://github.com/MrIbrahem/publish_py/pull/78)

## 75

-   This pull request consolidates and refactors the project documentation by moving comprehensive details, including project overview, installation, architecture, and configuration, from CLAUDE.md to AGENTS.md. CLAUDE.md is simplified to a quick-commands reference. The feedback suggests correcting an outdated reference to src/main_app/config.py in AGENTS.md (which is now a package directory) and removing redundant formatting commands (black and isort) in CLAUDE.md since ruff is already used. [#75](https://github.com/MrIbrahem/publish_py/pull/75)

## 74

-   This pull request refactors the codebase by extracting leaderboard-related database service functions from <code>page_service.py</code> into a new dedicated <code>leaderboard_service.py</code> module, updating all relevant imports across routes and tests. The review feedback highlights compatibility issues with SQLite (commonly used for local testing) in the newly moved functions (<code>get_pages_years</code>, <code>get_months_of_pages_years</code>, and <code>get_pages</code>) due to the use of MySQL-specific date functions (<code>YEAR</code> and <code>MONTH</code>). Additionally, it is recommended to add a return type annotation to <code>top_lang_of_users</code> for better type safety. [#74](https://github.com/MrIbrahem/publish_py/pull/74)

## 73

-   This pull request refactors the leaderboard chart data retrieval by introducing a centralized service function, <code>get_leaderboard_chart_data</code>, and updating the API and main leaderboard routes to use it. This simplifies the route handlers and adds support for both SQLite and other database engines. Unit tests have also been added to verify the new service function. Feedback on these changes includes a critical bug fix in the main leaderboard route where passing both <code>camp</code> and <code>cat</code> parameters bypasses campaign-level filtering, as well as a recommendation to add a null check on <code>PageRecord.target</code> for consistency and defensive programming. [#73](https://github.com/MrIbrahem/publish_py/pull/73)

## 72

-   This pull request implements comprehensive filtering capabilities (by campaign, user group, year, and month) for the leaderboard dashboard, adding new database service helpers, form parsing utilities, and UI updates to support these filters. The review feedback highlights several critical issues: using <code>outerjoin</code> instead of <code>join</code> in the leaderboard API query leads to incorrect counts, summing string-typed page views directly in the templates' routes will cause a <code>TypeError</code>, and sorting queried years or months without filtering out potential <code>None</code> values can trigger runtime crashes. [#72](https://github.com/MrIbrahem/publish_py/pull/72)

## 71

-   This pull request reorganizes the <code>mwclient</code> skill documentation, adds a comprehensive <code>PROJECT_AUDIT_REPORT.md</code> auditing the MDWiki Translation Dashboard, adds several README files, formats <code>pyproject.toml</code>, and introduces type annotations across multiple modules. The code review feedback highlights a type annotation error where <code>word</code> (representing word count) is incorrectly annotated as <code>str</code> instead of <code>int</code> in <code>worker.py</code>. Additionally, PEP 8 spacing violations around default parameter values with type annotations were identified in <code>worker.py</code> and <code>text_api.py</code>. Finally, it is recommended to stop ignoring <code>F401</code> and <code>E252</code> in <code>pyproject.toml</code> to enforce cleaner code and prevent unused imports and spacing issues. [#71](https://github.com/MrIbrahem/publish_py/pull/71)

## 70

-   This pull request refactors the admin routing and database services, modularizing QID management through a new QidsModel and reorganizing Flask extensions to improve project structure. It includes significant updates to admin templates for better responsiveness and consistency, alongside service-level changes such as renaming listing functions and implementing custom exception handling for unique constraint violations. Review feedback highlights several critical improvement opportunities: addressing logic errors in update functions where default parameters or truthiness checks could lead to unintended data overwrites, and correcting type inconsistencies where string IDs from request arguments are passed directly to database service methods expecting integers. [#70](https://github.com/MrIbrahem/publish_py/pull/70)

## 69

-   This pull request introduces a comprehensive admin dashboard for managing translations, QIDs, and page promotions, including new Flask blueprints, SQLAlchemy services, and Jinja2 templates. The reviewer feedback identifies a potential data persistence issue in the page promotion workflow where updates might not be committed if subsequent steps fail. Additionally, the review suggests optimizations to avoid redundant database lookups in the translation edit routes, recommends moving inline imports to the top of files for PEP 8 compliance, and points out opportunities to simplify SQLAlchemy queries and remove unused helper functions. [#69](https://github.com/MrIbrahem/publish_py/pull/69)

## 68

-   This pull request introduces the QidOthersRecord model and a corresponding service for its management, while also removing the add_date field from the QidRecord model and adding QID format validation. Key feedback includes addressing a bug where a non-existent add_date argument is passed to the QidOthersRecord constructor and recommending the use of SQLAlchemy's @validates decorator to centralize validation logic for both new and updated records. Additionally, it is suggested to lower the logging level for missing records to reduce noise. [#68](https://github.com/MrIbrahem/publish_py/pull/68)

## 67

-   This pull request refactors the application's routing and settings management, notably splitting the index page into a search form at <code>/</code> and a results table at <code>/table</code>. It also cleans up the <code>results_loader_2026</code> logic by removing several unused parameters and simplifies boolean setting storage to use "1" and "0" strings. Feedback from the review identifies a high-severity risk of an <code>AttributeError</code> for unauthenticated users on the new results route, as well as concerns regarding the lack of normalization in the updated boolean parsing logic which could break existing configurations. [#67](https://github.com/MrIbrahem/publish_py/pull/67)

## 66

-   This pull request refactors the application's configuration system by migrating from a single file to a structured package, introducing a dedicated SecurityConfig for Flask 3.1+ features, and removing the optional OAuth toggle. The review identifies a critical regression where the legacy configuration path fails to set the database URI, leading to initialization failures. Additionally, the feedback points out several instances of redundant code, unused functions, and inconsistent environment variable handling within the new configuration classes, while suggesting the use of a centralized URI builder to ensure consistent database encoding. [#66](https://github.com/MrIbrahem/publish_py/pull/66)

## 65

-   This pull request implements a comprehensive port of the PHP <code>results_2026</code> pipeline into Flask, spanning data models, raw SQL services, URL generation utilities, orchestration logic, route handling with request parsing, and templated UI rendering. Changes include the new <code>CategoryMemberRecord</code> model, SQL-based article statistics services, Flask route refactoring with PHP-compatible parameter resolution, and Jinja templates for displaying translation results in three states. [#65](https://github.com/MrIbrahem/publish_py/pull/65)

## 64

-   This pull request ports the results_2026 PHP module to the Flask-based publish_py application, introducing new database services, route logic, and Jinja templates to replicate the 2026 results pipeline. The review feedback identifies a logic error in title deduplication that incorrectly favors lower-viewed articles, a mismatch in title formatting (spaces vs. underscores) when checking translation types against database records, and a deviation from the implementation plan regarding URL parameter encoding in the tr_link_medwiki helper. [#64](https://github.com/MrIbrahem/publish_py/pull/64)

## 63

-   This pull request significantly improves database reliability by implementing standardized transaction rollback handling across various service modules. It also introduces stricter input validation for project titles, adds a unique constraint to the QID model, and implements numeric filtering in the report service. Feedback from the review focuses on ensuring consistent application of the new rollback pattern in remaining services, refining title validation logic, and cleaning up redundant imports. [#63](https://github.com/MrIbrahem/publish_py/pull/63)

## 62

-   This pull request migrates the application's database layer to use Flask-SQLAlchemy and Flask-Migrate, replacing manual SQLAlchemy session management. The changes involve updating the application factory, configuration, models, and all database services to utilize the <code>db.session</code> proxy. Feedback identifies critical typos in <code>category_service.py</code> where <code>db.session.session.get</code> was used, and recommends using <code>db.session.get()</code> for primary key lookups in <code>users_no_inprocess_service.py</code> to maintain consistency. Additionally, leftover migration notes and regex strings in <code>user_service.py</code> should be removed. [#62](https://github.com/MrIbrahem/publish_py/pull/62)

## 61

-   This pull request reorganizes the codebase to consolidate database service implementations from a flat <code>shared/services/</code> structure into organized subpackages under <code>db/services/</code>. All service consumers—admin routes, public routes, shared utilities, and tests—are updated to reference the new locations. Delete function return types change from returning deleted records to returning booleans. ORM lookups are optimized to use <code>session.get()</code>. Documentation and the project tree are updated to reflect the restructuring. [#61](https://github.com/MrIbrahem/publish_py/pull/61)

## 60

-   This pull request introduces a comprehensive migration plan to transition the project from plain SQLAlchemy to Flask-SQLAlchemy, covering architecture, strategy, and implementation details. It also refactors service layer exports and updates configuration type hints and docstrings. Review feedback identifies inconsistencies in the migration plan's recommended strategy and configuration keys, points out incorrect environment variable names in new docstrings, and advises against leaving commented-out dependencies or code in the configuration. [#60](https://github.com/MrIbrahem/publish_py/pull/60)

## 56

-   This pull request performs a comprehensive renaming of the core application module from <code>sqlalchemy_app</code> to <code>main_app</code>. The changes encompass directory restructuring, updates to documentation and configuration files, and a global refactoring of imports and mock paths within the source code and test suites. I have no feedback to provide as there are no review comments. [#56](https://github.com/MrIbrahem/publish_py/pull/56)

## 55

-   This pull request refactors environment loading from a centralized <code>env_config.py</code> module to direct <code>load_dotenv()</code> calls in WSGI entry points, updates guidance documentation to reflect the change, adjusts tooling configuration, and standardizes test file import formatting across the codebase. [#55](https://github.com/MrIbrahem/publish_py/pull/55)

## 52

-   This pull request updates the environment variable name for the tables directory from JSON_TABLES_PATH to TABLES_PATH in the mdwiki_api client. Feedback suggests centralizing this configuration within the application's config module to improve architectural consistency and ensure proper path resolution, or alternatively, wrapping the environment variable access with os.path.expanduser to handle home directory paths correctly. [#52](https://github.com/MrIbrahem/publish_py/pull/52)

## 51

-   This pull request implements a full Results API backed by a MediaWiki category fetcher, adds ORM models and service query helpers, re-exports client/service helpers, updates route wiring to include execution timing, and inverts test-placeholder file naming logic. [#51](https://github.com/MrIbrahem/publish_py/pull/51)
