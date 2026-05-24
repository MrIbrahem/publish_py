
from sqlalchemy.exc import DatabaseError


class UniqueError(DatabaseError):
    code = "gkpj-unique"
    message = "Unique constraint failed"

    def __init__(self, title):
        super().__init__(None, None, None)
        self.title = title


__all__ = [
    "UniqueError",
]
