# Flask-SQLAlchemy Migration Guide

This project has been successfully migrated from standalone SQLAlchemy to Flask-SQLAlchemy.

## What Changed

### 1. Dependencies
- Added `flask-sqlalchemy` and `flask-migrate` to `requirements.txt`

### 2. Extensions Module
- Created `src/sqlalchemy_app/extensions.py` with centralized `db` and `migrate` objects
- Moved `LONGTEXT` custom type to extensions module
- Created `Model` base class with `to_dict()` mixin functionality

### 3. Configuration
- Updated `config.py` to include Flask-SQLAlchemy settings:
  - `SQLALCHEMY_DATABASE_URI`
  - `SQLALCHEMY_TRACK_MODIFICATIONS = False`
  - `SQLALCHEMY_ENGINE_OPTIONS` with connection pooling settings

### 4. Application Initialization
- Replaced manual `init_db()` with `db.init_app(app)` and `migrate.init_app(app, db)`
- Database tables are created using `db.create_all()` within application context

### 5. Models
All 10 model files updated:
- Changed base class from `BaseDb` to `Model` (which extends `db.Model`)
- Replaced `Column` with `db.Column`
- Replaced type imports (e.g., `Integer` with `db.Integer`)
- Preserved all custom functionality (validation, defaults, `to_dict()`)

### 6. Session Management
- **Old Pattern:**
  ```python
  with get_session() as session:
      session.query(Model).all()
      session.commit()
  ```

- **New Pattern:**
  ```python
  db.session.query(Model).all()
  db.session.commit()
  ```

- Flask-SQLAlchemy automatically manages session lifecycle per request
- No need for context managers or manual session creation

### 7. Backward Compatibility
- `shared/engine.py` provides compatibility layer for code still using `get_session()`
- `BaseDb` is aliased to `Model` for backward compatibility
- Deprecated functions (`init_db`, `build_db_url`) kept with warnings

## Using Flask-Migrate

### Initialize Migrations (One-time setup)
```bash
# Navigate to the project root
cd /path/to/publish_py

# Initialize migration repository
flask --app src.app db init
```

This creates a `migrations/` directory with Alembic configuration.

### Create a Migration
```bash
# Auto-generate migration from model changes
flask --app src.app db migrate -m "Description of changes"

# Review the generated migration file in migrations/versions/
```

### Apply Migrations
```bash
# Apply all pending migrations
flask --app src.app db upgrade

# Rollback one migration
flask --app src.app db downgrade
```

### Common Migration Commands
```bash
# Show current migration status
flask --app src.app db current

# Show migration history
flask --app src.app db history

# Upgrade to specific revision
flask --app src.app db upgrade <revision>

# Downgrade to specific revision
flask --app src.app db downgrade <revision>
```

## Testing the Migration

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run Tests
```bash
pytest
```

### 3. Start Development Server
```bash
# Using development config
python src/app.py

# Or using flask command
flask --app src.app run
```

## Migration Checklist

- [x] Install Flask-SQLAlchemy and Flask-Migrate
- [x] Create extensions.py with db and migrate objects
- [x] Update config.py with Flask-SQLAlchemy settings
- [x] Update application initialization
- [x] Migrate all model files to use db.Model
- [x] Update service files to use db.session
- [x] Update API route files to use db.session
- [x] Set up Flask-Migrate
- [ ] Run tests to verify functionality
- [ ] Initialize migration repository
- [ ] Create initial migration
- [ ] Deploy to staging
- [ ] Monitor for issues

## Benefits of Flask-SQLAlchemy

1. **Simplified Session Management**: Flask-SQLAlchemy automatically manages sessions per request
2. **Better Integration**: Seamless integration with Flask application context
3. **Migration Support**: Flask-Migrate provides Alembic-based database migrations
4. **Reduced Boilerplate**: Less code for database setup and configuration
5. **Best Practices**: Follows Flask ecosystem conventions

## Troubleshooting

### Issue: "RuntimeError: Working outside of application context"
**Solution**: Ensure database operations are within Flask application context:
```python
with app.app_context():
    db.session.query(Model).all()
```

### Issue: Migration conflicts
**Solution**: 
1. Backup your database
2. Review migration file
3. Manually adjust if needed
4. Test on staging first

### Issue: Import errors
**Solution**: Ensure all models are imported before `db.create_all()` is called

## Next Steps

1. Run existing tests to ensure no regressions
2. Initialize Flask-Migrate: `flask db init`
3. Create initial migration: `flask db migrate -m "Initial migration"`
4. Review and apply migration: `flask db upgrade`
5. Deploy to staging environment
6. Monitor logs for any issues
7. Gradually update remaining service files to use `db.session` directly

## Support

For questions or issues related to this migration, refer to:
- [Flask-SQLAlchemy Documentation](https://flask-sqlalchemy.palletsprojects.com/)
- [Flask-Migrate Documentation](https://flask-migrate.readthedocs.io/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
