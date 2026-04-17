import pytest
from sqlalchemy import Column, Integer, String, DateTime
from src.app_main.shared.db.engine import BaseDb

class _PagesUsersRecord(BaseDb):
    __tablename__ = "pages_users"
    id = Column(Integer, primary_key=True)
    title = Column(String(255))
    lang = Column(String(30))
    user = Column(String(120))
    target = Column(String(120))
    pupdate = Column(DateTime)
