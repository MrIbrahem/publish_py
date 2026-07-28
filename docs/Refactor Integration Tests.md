### Prompt for AI Agent

**Task:** Refactor Integration Tests to Remove Database/ORM Mocks and Use Real Service/Database Calls.

#### Context & Objective:

We are updating our test suite to align with our testing strategy specified in `tests/README.md`.
The core guideline is: **Do NOT mock SQLAlchemy queries, ORMs, or local database services.** Mocking database-related code creates fragile tests that test mock behavior rather than actual business logic, queries, schema constraints, and database relationships.

#### What Needs to Be Done:

1. **Identify and Remove Database Mocks/Patches:**

-   Remove `unittest.mock.patch` or `MagicMock` calls applied to services, models, repositories, or `db.session` (e.g., `LanguageSettingService`, `LangService`, `list_langs`, etc.).

2. **Replace Mocks with Real Service/Database Operations:**

-   Import the required internal services or models directly into the test file.
-   Instanciate the real service classes (or use test fixtures) to seed/create real test data before hitting endpoints or executing functions.
-   Let the code interact with the real test database.

3. **Follow the Allowed Boundaries (What TO Mock vs What NOT to Mock):**

-   ❌ **DO NOT Mock:**
-   `db.session` methods (`add`, `commit`, `query`, etc.).
-   Model instances or DB Entities.
-   Local service and repository methods that read from or write to the database.

-   ✅ **KEEP Mocking ONLY External/Non-Deterministic Dependencies:**
-   External HTTP API calls (S3, Payment Gateways, Webhooks).
-   Delays like `time.sleep`.
-   Non-deterministic utilities (e.g., system clock, `uuid4`).

#### Reference Example:

-   **Before (Incorrect - Mocking Services):**

```python
@pytest.mark.integration
class TestLanguageSettingsDashboard:
    def test_language_settings_dashboard_lists_settings(self, mock_admin_required, auth_client: FlaskClient):
        with patch("src.main_app.admin.routes.language_settings.LanguageSettingService.list_language_settings") as mock_list:
            mock_list.return_value = [MagicMock(lang_code="en", move_dots=1, expend=0, add_en_lang=1)]
            with patch("src.main_app.admin.routes.language_settings.list_langs") as mock_langs:
                mock_langs.return_value = [MagicMock(code="en", name="English")]

                response = auth_client.get("/admin/language_settings/")

        assert response.status_code == 200

```

-   **After (Correct - Seeding DB with Real Services):**

```python
from src.main_app.db.services import LanguageSettingService, LangService

@pytest.mark.integration
class TestLanguageSettingsDashboard:
    def test_language_settings_dashboard_lists_settings(self, mock_admin_required, auth_client: FlaskClient):
        # 1. Seed data using real services
        langs_service = LangService()
        langs_service.add_lang("en", "English", "English")
        langs_service.add_lang("ar", "Arabic", "Arabic")

        lang_setting_service = LanguageSettingService()
        lang_setting_service.add_language_setting(lang_code="en", move_dots=1, expend=0, add_en_lang=1)
        lang_setting_service.add_language_setting(lang_code="ar", move_dots=0, expend=1, add_en_lang=0)

        # 2. Perform the test request against the real populated database
        response = auth_client.get("/admin/language_settings/")

        # 3. Assert status code/response
        assert response.status_code == 200

```

Please review all integration test files and apply this pattern across any test suites using DB/Service patches.

quick find of files search for `"src\.[\._\w]+Service\.`
