
from sqlalchemy.exc import DatabaseError


class UniqueError(DatabaseError):
    code = "gkpj-unique"
    message = "Unique constraint failed"

    def __init__(self, title):
        self.title = title


__all__ = [
    "UniqueError",
]
