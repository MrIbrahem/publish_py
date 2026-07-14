# Flask-Security Migration & Integration Plan

## 1. Executive Summary

This document presents a comprehensive, production-grade architectural review and step-by-step migration plan for integrating **Flask-Security-Too** into the existing Flask-based Wikipedia translation application.

Currently, the application relies on custom-built authentication mechanisms, custom decorators (`@user_login_required`, `@oauth_required`, `@admin_required`), manual cookie and session manipulation, and a decoupled database schema for administrative roles (`coordinators` table). While functional, this custom implementation increases the maintenance burden, lacks native security audits, and is susceptible to architectural drift.

Integrating Flask-Security-Too (the modern, actively-maintained branch of Flask-Security) will:
- Standardize authentication and session lifecycle management.
- Provide robust, built-in Role-Based Access Control (RBAC) and Permission-Based Access Control (PBAC).
- Enhance session security through features like session invalidation, cryptographic uniquifiers, and native token tracking.
- Dramatically reduce custom boilerplates and code duplication.

This plan is specifically structured for **incremental implementation**. It guarantees that the application remains fully functional and deployable after every phase, maintaining perfect coexistence between the old session loader and the new Flask-Security engine.

---

## 2. Current Architecture Analysis

### High-Level Assessment
The current system operates on a hybrid cookie-session authentication flow centered around a third-party login provider (MediaWiki OAuth 1.0a):
1. **User Identity Source**: `users` table holds user identity (`user_id`, `username`, `email`, `user_group`).
2. **Access Credentials**: `user_tokens` table holds encrypted MediaWiki OAuth credentials (`access_token`, `access_secret`).
3. **Session State**: Flask's client-side secure cookie session holds `"uid"` and `"username"`.
4. **Custom Fallback Cookie**: A separate signed cookie (configured via `settings.cookie.name`) is used as a fallback to re-establish the session if the session cookie is cleared or expires.
5. **Authorization (Coordinators)**: A separate table, `coordinators` (AdminUserRecord), references `users.username` with an `is_active` flag.

### Flow of Authentication and Context Population
Every request triggers a `before_app_request` hook (`load_logged_in_user` in `src/main_app/public/auth/utils.py`), which:
1. Extracts `user_id` from the session.
2. If missing, attempts to extract it from the signed fallback cookie.
3. Queries the DB service `AuthUserService.get_authenticated_user(user_id)` to construct a custom frozen dataclass `CurrentUser`.
4. Checks if the user is listed as active in the `coordinators` table to set `is_active_admin = True`.
5. Binds the `CurrentUser` instance to Flask's global request context as `g._current_user`.

### Affected Components
Integrating Flask-Security-Too touches several layers:
- **Models**: `UserRecord` (needs additions like `active`, `password`, `fs_uniquifier`, and relationships), and new models `RoleRecord` and `UserRoles`.
- **Database Schema**: New tables `roles` and `roles_users`.
- **Authentication Lifecycle**: `/auth/login` and `/auth/callback` must bridge into Flask-Login's `login_user` mechanism.
- **Context Handling**: `g._current_user` is replaced by Flask-Security's thread-local `current_user` proxy.
- **Route Access Control**: Custom decorators must be replaced across all blueprints:
  - `src/main_app/admin/admin_panel.py`
  - `src/main_app/admin/routes/*.py` (coordinators, settings, full_translators, etc.)
  - `src/main_app/public/routes/refs/routes.py` (and others requiring login/credentials).

### Dependency Graph & Authentication Flow

Below is the text-based ASCII flow showing how authentication, context population, and decorators currently interact:

```
[ Request Received ]
         │
         ▼
[ bp_auth.before_app_request ]
         │
         ▼
[ load_logged_in_user() ]
         │
         ├─► Read session["uid"] ───────┐
         │                              ▼
         └─► (Fallback) Read Cookie ──► [ Extract User ID ]
                                                │
                                                ▼
                                    [ Query Database Layer ]
                                                │
                                                ▼
                                    [ Check coordinators table ]
                                                │
                                                ▼
                                    [ Instantiate CurrentUser ]
                                                │
                                                ▼
                                    [ Populate g._current_user ]
         ┌──────────────────────────────────────┴──────────────────────────────────────┐
         ▼                                      ▼                                      ▼
 [ @user_login_required ]               [ @oauth_required ]                    [ @admin_required ]
  Checks if loaded user                  Checks loaded user +                  Checks loaded user +
  is present in context.                 active OAuth tokens.                  is_active_admin == True.
```

---

## 3. Migration Roadmap

The migration is divided into four distinct phases to minimize risk and avoid breaking core translation and publishing features.

```
┌────────────────────────┐      ┌────────────────────────┐      ┌────────────────────────┐      ┌────────────────────────┐
│  Phase 1: Foundation   │ ───► │   Phase 2: Hybrid S-D  │ ───► │  Phase 3: Decorators   │ ───► │   Phase 4: Cleanup &   │
│  Schema & Dependencies │      │   Dual Session Engine  │      │  Refactoring Routing   │      │   Hardening Security   │
└────────────────────────┘      └────────────────────────┘      └────────────────────────┘      └────────────────────────┘
```

### Detailed Checklist

#### Phase 1: Database Schema & Dependencies
- [ ] Add `flask-security-too` to `requirements.txt`.
- [ ] Implement database migrations to add `active`, `password`, and `fs_uniquifier` to the `users` table.
- [ ] Create `RoleRecord` and `UserRoles` models.
- [ ] Apply the schema changes using Flask-Migrate/Alembic.

#### Phase 2: Hybrid Session Dual-Engine
- [ ] Configure and initialize `Security` and `SQLAlchemyUserDatastore` in the application factory (`src/main_app/__init__.py`).
- [ ] Update `/auth/callback` to trigger Flask-Login's `login_user()` alongside the legacy session parameters.
- [ ] Build a database-level sync utility to automatically add/remove the `admin` role in Flask-Security when the `coordinators` table is modified.
- [ ] Ensure `g._current_user` fallback is still populated so old route decorators continue working.

#### Phase 3: Routing & Decorator Refactoring
- [ ] Map custom decorators to Flask-Security decorators.
- [ ] Refactor all routes in `/admin` to use `@roles_required('admin')` instead of `@admin_required`.
- [ ] Refactor public routes to use `@auth_required()` or `@login_required` instead of `@user_login_required`.
- [ ] Update templates to reference `current_user` instead of `g._current_user`.

#### Phase 4: Cleanup & Hardening
- [ ] Decommission and delete custom decorators (`@user_login_required`, `@admin_required`).
- [ ] Remove `load_logged_in_user` before-request hook.
- [ ] Set `g._current_user` references to use Flask-Security's `current_user` globally.
- [ ] Finalize configuration options for session timeout, passwordless setup, and CSRF token propagation.

### Risk Analysis & Rollback Strategy

| Phase | Core Risk | Mitigation Strategy | Rollback Action |
|---|---|---|---|
| **Phase 1** | Migration fails or locks production tables. | Execute migration during off-peak hours; verify schema locally with SQLite first. | Run `flask db downgrade` to revert to previous migration version. |
| **Phase 2** | Login callback broken, preventing users from logging in. | Keep the legacy session `uid` populate code active. Fail-safe catch block around FS login. | Revert `/auth/callback` edits. Legacy cookie parsing is completely untouched. |
| **Phase 3** | Admin user locked out of panel. | Sync script auto-promotes existing coordinators to the `admin` Role during initialization. | Restore custom `@admin_required` checks from git backup. |
| **Phase 4** | Legacy code paths break when hook is deleted. | Comprehensive integration testing. Deprecate elements incrementally rather than deleting instantly. | Revert hook removal and continue loading `g._current_user`. |

---

## 4. Step-by-Step Implementation Guide

### Step 1.1: Install Dependencies
- **Why**: Bring the standard libraries required for Flask-Security-Too.
- **Files**: `requirements.txt`
- **Expected Changes**: Add `Flask-Security-Too>=5.3.0` and dependencies like `bcrypt` or `argon2-cffi`.

### Step 1.2: Model Declarations
- **Why**: Define schemas to satisfy Flask-Security's datastore interface.
- **Files**: `src/main_app/db/models/users.py`
- **Expected Changes**:
  - Implement `UserMixin` on `UserRecord`.
  - Add `active`, `password`, and `fs_uniquifier` columns.
  - Define `RoleRecord` inheriting from `db.Model` and `RoleMixin`.
  - Define `UserRoles` table.

```python
# Expected model extensions
from flask_security import UserMixin, RoleMixin

class RoleRecord(db.Model, RoleMixin):
    __tablename__ = 'roles'
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(80), unique=True)
    description: Mapped[str | None] = mapped_column(String(255))

class UserRoles(db.Model):
    __tablename__ = 'roles_users'
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.user_id', ondelete='CASCADE'))
    role_id: Mapped[int] = mapped_column(ForeignKey('roles.id', ondelete='CASCADE'))
```

### Step 2.1: Security Initialization
- **Why**: Initialize Flask-Security context.
- **Files**: `src/main_app/__init__.py`, `src/main_app/extensions/__init__.py`
- **Expected Changes**:
  - Instantiate `Security` in `extensions`.
  - Configure `user_datastore` and call `security.init_app(app, user_datastore)` inside `create_app()`.

### Step 2.2: Bridging Login Flow
- **Why**: Log user into Flask-Security when OAuth verification succeeds.
- **Files**: `src/main_app/public/auth/routes.py`
- **Expected Changes**:
  - Within `@bp_auth.get("/callback")`, after loading or registering `UserRecord`, execute:
    ```python
    from flask_security import login_user
    login_user(user_record, remember=True)
    ```

---

## 5. Flask-Security Integration

### User & Role Model Integration
To ensure perfect backward compatibility, our customized Flask-Security models are mapped directly onto our existing database, preventing schema naming conflicts:

```python
from flask_security import UserMixin, RoleMixin
from sqlalchemy import String, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

class RoleRecord(db.Model, RoleMixin):
    __tablename__ = "roles"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(80), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(String(255), nullable=True)

class UserRecord(db.Model, UserMixin):
    __tablename__ = "users"

    user_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False, default="")

    # Flask-Security specific additions
    active: Mapped[bool] = mapped_column(Boolean(), nullable=False, default=True, server_default="1")
    password: Mapped[str | None] = mapped_column(String(255), nullable=True) # Nullable since we use MW OAuth
    fs_uniquifier: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)

    # Relationships
    roles: Mapped[list[RoleRecord]] = relationship(
        "RoleRecord", secondary="roles_users", backref="users"
    )

    # Overriding get_id to match our primary key column "user_id"
    def get_id(self):
        return str(self.user_id)
```

### Password Hashing Config (OAuth Support)
Since user authentication is managed externally by Wikipedia OAuth, local password checking is bypassed by setting passwordless options in Flask-Security config:

```python
# Add these settings to src/main_app/config/flask_config.py
SECURITY_PASSWORD_HASH = "bcrypt"
SECURITY_PASSWORD_SINGLE_HASH = True
SECURITY_REGISTERABLE = False  # Bypasses local registration page
SECURITY_CONFIRMABLE = False
SECURITY_SEND_REGISTER_EMAIL = False
```

### Coordinator Sync Utility (Coexistence Insurance)
To allow custom database tools to manage coordinators without locking out Flask-Security's authorization checks, we use SQLAlchemy event listeners or service layer hooks to sync role status:

```python
# Hook to be added in admin_service.py or database setup
def sync_coordinator_to_role(username: str, is_active: bool):
    """Automatically adds or removes 'admin' role based on coordinator model state."""
    user = UserRecord.query.filter_by(username=username).first()
    if not user:
        return

    admin_role = RoleRecord.query.filter_by(name="admin").first()
    if not admin_role:
        admin_role = RoleRecord(name="admin", description="Administrator access")
        db.session.add(admin_role)
        db.session.commit()

    if is_active:
        if admin_role not in user.roles:
            user.roles.append(admin_role)
    else:
        if admin_role in user.roles:
            user.roles.remove(admin_role)

    db.session.commit()
```

---

## 6. Decorator Mapping Table

| Custom Decorator | Flask-Security Equivalent | Implementation & Notes |
|---|---|---|
| `@user_login_required` | `@auth_required()` | Enforces active session, fully managed by Flask-Login / Flask-Security context. |
| `@admin_required` | `@roles_required('admin')` | Checks if `current_user` belongs to the `admin` role. Returns 403 instantly on failure. |
| `@oauth_required` | Custom wrapper / Context Check | Flask-Security ensures authenticated context; we inspect `current_user.token` for credentials. |

---

## 7. Code Refactoring (Before & After)

### A. Custom Decorator `admin_required`
#### Existing Code (`src/main_app/admin/decorators.py`)
```python
def admin_required(view: FuncType) -> FuncType:
    @wraps(view)
    def wrapped(*args, **kwargs):
        user: CurrentUser | None = load_user()
        if not user:
            return redirect(url_for("auth.login"))
        if not user.is_active_admin:
            logger.warning("User %s tried to access admin-only route", user.username)
            abort(403)
        return view(*args, **kwargs)
    return cast(FuncType, wrapped)
```

#### Flask-Security Replacement
```python
from flask_security import roles_required

# In routes, replace "@admin_required" directly with:
# @roles_required('admin')
```

#### Why the replacement is correct:
The custom decorator manually parses context, handles logging, redirects, and aborts with status code 403. Flask-Security's `@roles_required('admin')` handles all of these securely under the hood. It integrates seamlessly with Flask-Security's global handler, firing standard signals that can be audited by security tools.

---

### B. Route Blueprint Protection
#### Existing Code (`src/main_app/admin/admin_panel.py`)
```python
class AdminPanelRoutes:
    def __init__(self) -> None:
        self.bp = Blueprint("admin", __name__, url_prefix="/admin")
        self._setup_routes()

    def _setup_routes(self) -> None:
        @self.bp.route("/", methods=["GET"])
        @admin_required
        def index():
            return redirect(url_for("admin.last_dashboard"))
```

#### Flask-Security Replacement (Using Blueprint before_request)
Instead of decorating dozens of endpoints manually, we can protect the entire Blueprint in one place:

```python
from flask_security import roles_required

class AdminPanelRoutes:
    def __init__(self) -> None:
        self.bp = Blueprint("admin", __name__, url_prefix="/admin")
        self._setup_routes()
        self._secure_blueprint()

    def _secure_blueprint(self) -> None:
        @self.bp.before_request
        @roles_required('admin')
        def restrict_blueprint():
            pass # Implicitly protects all routes under this blueprint
```

#### Why the replacement is correct:
Blueprint-level protection ensures that new endpoints added to the admin namespace are secure by default, eliminating the risk of un-decorated route leaks.

---

### C. Context Access and `current_user`
#### Existing Code
```python
@bp_auth.before_app_request
def before_request() -> None:
    load_logged_in_user()

# Accessing current user
user = g._current_user
```

#### Flask-Security Replacement
```python
# No custom before_request is needed. Flask-Security auto-loads user via Flask-Login.
from flask_security import current_user

# Accessing user attributes
username = current_user.username
```

#### Why the replacement is correct:
The thread-local `current_user` proxy is highly optimized, lazy-loaded, and automatically synchronized across database changes and authentication state toggles.

---

## 8. Testing Strategy

### 1. Incremental Integration Checks
During Phase 2, tests must confirm both custom `g._current_user` and Flask-Security's `current_user` load the exact same user entity during a single request:

```python
def test_hybrid_session_loading(auth_client):
    # Log in user through the standard test client helper
    response = auth_client.get('/admin/')

    # Verify legacy fallback user is available
    assert g._current_user.username == "TestUser"
    # Verify Flask-Security user is logged in
    assert current_user.username == "TestUser"
```

### 2. Integration Testing the New Access Control
We will test the updated decorators by replacing the patched decorators in `tests/integration/admin/routes/test_admin_routes_integration.py` with mock Role assignments:

```python
def test_authenticated_non_admin_forbidden_flask_security(auth_client, user_datastore):
    # Ensure TestUser has NO admin role
    test_user = user_datastore.find_user(username="TestUser")
    admin_role = user_datastore.find_role("admin")
    if admin_role in test_user.roles:
        test_user.roles.remove(admin_role)
    db.session.commit()

    response = auth_client.get("/admin/", follow_redirects=False)
    assert response.status_code == 403
```

---

## 9. Rollback Plan & Cleanup

### Rollback Protocol
If any regression is detected in production during deployment:
1. **Database Rollback**:
   Run `flask db downgrade` to remove the schema migration without affecting core user indices.
2. **Code Rollback**:
   Restore decorators from git state of the release tag preceding the migration branch.
3. **Session Cleardown**:
   Issue a global cookie salt rotation to clear any active sessions structured with invalid Flask-Security configurations, forcing users to re-authenticate via OAuth.

### Post-Migration Cleanup Tasks
Once Phase 4 is verified as completely successful:
- [ ] Remove `src/main_app/admin/decorators.py`.
- [ ] Delete references to `load_logged_in_user` and `_set_response_cookies`.
- [ ] Clean up configuration variables related to custom cookie generation (`settings.cookie.name`, etc.).

---

## 10. Best Practices & Final Recommendations

1. **Security-First Headers**: Maintain the existing `@app.after_request` hooks enforcing security headers alongside Flask-Security controls.
2. **Audit Logging**: Implement custom event listeners on Flask-Security signals (`user_logged_in`, `user_login_failed`, `unauthorized`) to track security threats or suspicious access patterns.
3. **Session Lifetime**: Set a reasonable `PERMANENT_SESSION_LIFETIME` (e.g., 30 days) combined with `SECURITY_TRACKABLE` to monitor active IP addresses and login histories.
4. **Token Security**: Always encrypt the MediaWiki OAuth tokens in transit and storage, regardless of the authentication wrapper. Keep `OAUTH_ENCRYPTION_KEY` isolated and secure in production environment configs.
