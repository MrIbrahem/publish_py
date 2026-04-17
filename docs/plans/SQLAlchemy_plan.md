# Python Refactoring Agent: SQLAlchemy ORM Integration

You are a Python refactoring agent. Your task is to add a SQLAlchemy ORM model alongside every existing dataclass model found in the following directory paths:

-   src/app_main/shared/domain/models/
-   src/app_main/admin/domain/models/
-   src/app_main/public/domain/models/

## ⚠️ Critical Context: Database Schemas

Before generating any ORM model, you **must** refer to the SQL CREATE TABLE definitions found in:

1.  src/app_main/shared/domain/db/schema.py
2.  src/app_main/admin/domain/db/schema.py
3.  src/app_main/public/domain/db/schema.py
    **The ORM models must strictly match the table names and column definitions (types, constraints, nullability) defined in these schema files.** Do not guess column names or types; use the SQL provided in these files as the "Source of Truth".

## Task Instructions

For each .py file in the models directories:

1.  **Identify Dataclasses:** Locate all classes decorated with @dataclass.
2.  **Add ORM Class:** For each dataclass, add a new SQLAlchemy ORM class **ABOVE** it. Do NOT remove or modify the original dataclass.
3.  **ORM Class Requirements:**

-   **Name:** Leading underscore + Dataclass Name (e.g., FooRecord → \_FooRecord).
-   **Inheritance:** Inherit from BaseDb.
-   **Table Name:** Must match the table name in the corresponding schema.py file. (Usually snake_case of the class name minus "Record").
-   **Field Mapping:** Mirror fields from the dataclass, but cross-reference with the SQL in schema.py:
    -   Use Column(Integer, ...) for int (check SQL for UNSIGNED).
    -   Use Column(String(N), ...) for str (match N with varchar(N) in SQL).
    -   Map float, bool, datetime to their SQLAlchemy equivalents.
-   **Constraints:**
    -   Identify the PRIMARY KEY from the SQL (not just assuming it's id).
    -   Set nullable=False unless the SQL allows NULL or the dataclass uses Optional.
    -   Match UNIQUE keys and DEFAULT values found in the SQL.
-   **Methods:** Add a to_dict() method that mirrors the dataclass structure.

4.  **Imports:** Add required imports at the top:

-   from ...shared.db.engine import BaseDb (adjust relative path depth).
-   from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime
-   from sqlalchemy.orm import relationship

## Rules

-   **Non-Destructive:** Never delete or rename existing code.
-   **Placement:** New ORM class goes directly above the @dataclass.
-   **Complexity:** If a field is complex (List/Dict) and not clearly defined in the SQL schema, use Column(JSON) or String(500) with a # TODO: review type comment.
-   **Workflow:** Process one file at a time.

## Output Format per File

After editing, report:

-   **File:** <path>
-   **Added ORM models:** <list of class names>
-   **Matched Table(s) from Schema:** <list of table names matched from schema.py>
-   **Status:** Done
