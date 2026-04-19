"""
NOTE: shared should not import anything from admin or public
├── shared/
│   ├── db/ (db_driver.py, schema.py)
│   ├── services/ (page_service.py, user_token_service.py)
│   ├── online_services/ (API Clients)
│   ├── utils/ (المساعدون helpers, crypto.py)
│   ├── config.py
│   └── extensions.py (SQLAlchemy, Migrate, etc.)
"""
