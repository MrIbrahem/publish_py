## 2025-05-15 - [Broken Access Control in Admin Routes]
**Vulnerability:** Multiple administrative routes (8+ files) were missing the `@admin_required` decorator, allowing unauthenticated or non-admin users to view and modify sensitive application data.
**Learning:** In a large project with many blueprints and files, it's easy to miss authorization decorators on new routes if there isn't a centralized enforcement mechanism (like a `before_request` hook at the blueprint level).
**Prevention:** Consider enforcing admin checks at the blueprint level using `bp.before_request` for all administrative blueprints to ensure a "secure by default" posture. When adding new admin sub-blueprints, always verify they are protected.
