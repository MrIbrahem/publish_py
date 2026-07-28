Task: Migrate All Module-Level Service Function Aliases to Direct Service Class Usage

You are working in an existing Python codebase that uses SQLAlchemy service classes.

I want to refactor the codebase so that application code directly uses the relevant service classes instead of importing and calling module-level function aliases that delegate to a "_crud" service instance.

Services in Scope

Apply this refactoring to all of the following services:

FullTranslatorService
UsersNoInprocessService
PagesService
ReportService
PagesUsersToMainPagesService
TranslateTypeService
UserPagesService
InProcessService
LangService
ProjectService
PagesUsersToMainService
QidService
QidOthersService
CategoryService
AdminService
UsersService
UserTokenService
SettingsService
LanguageSettingService

"InProcessService" appears twice in the original list; process it only once.

---

Current Pattern

Many service modules may follow a pattern similar to:

class LanguageSettingService(CRUDService[LanguageSettingRecord]):
    ...

_crud = LanguageSettingService()

list_language_settings = _crud.list_language_settings
get_language_setting = _crud.get_language_setting
add_language_setting = _crud.add_language_setting
update_language_setting = _crud.update_language_setting

__all__ = [
    "list_language_settings",
    "get_language_setting",
    "add_language_setting",
    "update_language_setting",
]

Other services may expose different methods, but the architectural pattern is the same: module-level functions are aliases to methods on a service instance.

For example, callers may currently do:

from ...language_setting_service import get_language_setting

setting = get_language_setting(setting_id)

The desired pattern is to use the service class directly:

from ...language_setting_service import LanguageSettingService

service = LanguageSettingService()
setting = service.get_language_setting(setting_id)

Follow the project's existing conventions for service instantiation and dependency management. Do not introduce a new service lifecycle pattern if one already exists in the codebase.

---

Required Work

1. Inspect Every Service

For each service listed below:

FullTranslatorService
UsersNoInprocessService
PagesService
ReportService
PagesUsersToMainPagesService
TranslateTypeService
UserPagesService
InProcessService
LangService
ProjectService
PagesUsersToMainService
QidService
QidOthersService
CategoryService
AdminService
UsersService
UserTokenService
SettingsService
LanguageSettingService

Inspect the corresponding service module and identify:

- The service class.
- Its module-level "_crud" or equivalent singleton instance.
- Every module-level function alias pointing to a service method.
- The module's "__all__" exports.
- Any alternative aliasing patterns.
- Any wrapper functions that simply delegate to the service instance.

Do not assume all services use exactly the same naming convention. Inspect the actual code.

---

2. Find All Internal Callers

Search the entire repository for all usages of the module-level functions exposed by these services.

Identify all files that:

- Import the module-level functions directly.
- Import them with aliases.
- Import them using wildcard imports.
- Import the service module and access functions through the module.
- Call the functions indirectly through aliases that can be reliably identified.
- Use them in tests or fixtures.
- Use them in API routes/controllers.
- Use them in CLI commands.
- Use them in background jobs/tasks.
- Use them in scripts or utilities.
- Use them in other service modules.

Examples of patterns to search for include:

from some_service import some_function

from some_service import some_function as renamed_function

import some_service

some_service.some_function(...)

from some_service import *

Also search for direct calls to each exported function name throughout the repository.

---

3. Refactor Callers to Use Service Classes

Replace module-level function usage with direct calls to the appropriate service class.

For example, change:

from ...language_setting_service import get_language_setting

setting = get_language_setting(setting_id)

to:

from ...language_setting_service import LanguageSettingService

service = LanguageSettingService()
setting = service.get_language_setting(setting_id)

If multiple methods from the same service are used in a file, prefer reusing one service instance:

service = LanguageSettingService()

setting = service.get_language_setting(setting_id)
settings = service.list_language_settings()

Do not unnecessarily instantiate a service repeatedly.

Use the actual service class and actual method names discovered in the codebase. Do not invent methods.

For example, if a module exposes:

get_user = _crud.get_user
create_user = _crud.create_user
update_user = _crud.update_user

migrate callers to:

service = UsersService()

user = service.get_user(...)
user = service.create_user(...)
user = service.update_user(...)

Preserve the exact arguments, return values, exception behavior, and control flow.

---

4. Handle All Listed Services

Perform the same migration for every service in the list, not only "LanguageSettingService".

The full scope is:

FullTranslatorService
UsersNoInprocessService
PagesService
ReportService
PagesUsersToMainPagesService
TranslateTypeService
UserPagesService
InProcessService
LangService
ProjectService
PagesUsersToMainService
QidService
QidOthersService
CategoryService
AdminService
UsersService
UserTokenService
SettingsService
LanguageSettingService

The objective is to eliminate internal application dependencies on module-level CRUD/service function aliases for all of these services.

---

5. Remove Obsolete Module-Level Aliases

After migrating all internal callers, search again to determine whether each module-level alias is still used.

If an alias is no longer required internally and is not intentionally part of an external/public API, remove it.

For example, remove:

_crud = LanguageSettingService()

list_language_settings = _crud.list_language_settings
get_language_setting = _crud.get_language_setting
get_language_setting_by_code = _crud.get_language_setting_by_code
add_language_setting = _crud.add_language_setting
add_or_update_language_setting = _crud.add_or_update_language_setting
update_language_setting = _crud.update_language_setting

Also update:

__all__ = [
    ...
]

so that obsolete module-level function aliases are no longer exported.

Do not remove the service class or its instance methods.

If a module-level function is still required because it is part of an external/public API, is dynamically accessed, or is otherwise intentionally retained, leave it in place and clearly report it in the final summary.

---

6. Detect Similar Patterns Beyond the Listed Services

After completing the listed services, search the repository for other service modules that use the same architecture.

Look for patterns such as:

_crud = SomeService()
some_function = _crud.some_method

or:

_service = SomeService()
some_function = _service.some_method

or similar module-level delegation patterns.

For these additional services, apply the same refactoring only when the pattern is clearly equivalent.

Do not make unrelated architectural changes.

---

7. Preserve Existing Architecture

Important constraints:

- Preserve all existing behavior.
- Do not change business logic.
- Do not change SQLAlchemy queries.
- Do not change database models.
- Do not change method signatures unless absolutely necessary.
- Do not change validation behavior.
- Do not change exception behavior.
- Do not change transaction/session behavior.
- Preserve existing dependency injection patterns.
- Follow existing service instantiation conventions.
- Avoid circular imports.
- Avoid unnecessary service instantiation.
- Avoid unrelated formatting or cleanup.
- Do not blindly replace names based only on text matching.
- Verify that every replacement calls the correct service method.
- Pay special attention to functions that may have the same name across different service modules.

---

Validation Requirements

After completing the refactor:

A. Repository Search

Search the entire repository again for:

- Imports of the migrated module-level functions.
- Calls to the migrated module-level functions.
- Module-qualified calls to those functions.
- Remaining "_crud.method" aliases.
- Remaining "_service.method" module-level aliases.
- "__all__" entries exposing obsolete aliases.

Confirm that internal callers now use the appropriate service classes directly.

B. Check All Services

Create a checklist for all services in scope and verify each one was inspected:

[ ] FullTranslatorService
[ ] UsersNoInprocessService
[ ] PagesService
[ ] ReportService
[ ] PagesUsersToMainPagesService
[ ] TranslateTypeService
[ ] UserPagesService
[ ] InProcessService
[ ] LangService
[ ] ProjectService
[ ] PagesUsersToMainService
[ ] QidService
[ ] QidOthersService
[ ] CategoryService
[ ] AdminService
[ ] UsersService
[ ] UserTokenService
[ ] SettingsService
[ ] LanguageSettingService

C. Tests and Quality Checks

Run the relevant:

- Unit tests.
- Integration tests.
- Type checks.
- Lint checks.
- Import checks.
- Any project-specific validation commands.

Fix issues introduced by the refactoring.

---

Final Report

When finished, provide a concise report containing:

1. Services inspected
   
   - List all services that were processed.

2. Files changed
   
   - List files modified.

3. Callers migrated
   
   - Summarize which files were changed from module-level function calls to direct service class usage.

4. Aliases removed
   
   - List module-level aliases and "_crud" instances removed.

5. Additional services
   
   - List any other service modules discovered and refactored because they followed the same pattern.

6. Remaining aliases
   
   - List any aliases intentionally left in place and explain why.

7. Validation
   
   - List tests, linting, type checks, or other commands executed and their results.

The primary goal is to consistently migrate the codebase from module-level service function aliases to direct usage of the corresponding service classes, while preserving behavior and avoiding unrelated changes.
