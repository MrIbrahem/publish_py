"""
NOTE: shared should not import anything from admin or public
├── shared/
│   ├── db/ (db_class.py, sql_schema_tables.py)
│   ├── services/ (pages_service.py, users_services.py)
│   ├── online_services/ (API Clients)
│   ├── utils/ (المساعدون helpers, crypto.py)
│   ├── config.py
│   └── extensions.py (SQLAlchemy, Migrate, etc.)
"""
