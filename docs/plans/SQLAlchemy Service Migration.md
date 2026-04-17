
# Prompt: SQLAlchemy Service Migration Agent (Strict Version)
You are an expert Python developer. Your task is to implement a new service layer using SQLAlchemy ORM, replacing the legacy logic found in db/ and services/ folders.
## 📁 Source & Destination
For each entity (e.g., Coordinator, User, Page):
 1. **Read Legacy DB:** .../domain/db/db_<entity>s.py
 2. **Read Legacy Service:** .../domain/services/<entity>s_service.py
 3. **Read Model:** .../domain/models/<entity>.py (Use the ORM class _EntityRecord).
 4. **Create New Service:** .../domain/sqlalchemy_services/<entity>_service.py
## 🛠 Technical Requirements
### 1. Imports & Session Management
 * Import get_session and BaseDb from the local engine.py module.
 * Every function that interacts with the database must use get_session() as a context manager:
   ```python
   with get_session() as session:
       # logic here
   
   ```
### 2. Backward Compatibility (CRITICAL)
 * **Function Names:** Must be identical to the ones in the legacy services/ folder.
 * **Parameters:** Must match exactly (including default values).
 * **Return Types:** All functions must return the **Dataclass** version (e.g., CoordinatorRecord), NOT the ORM object.
 * **Conversion:** Convert ORM objects to Dataclasses using: DataclassRecord(**orm_obj.to_dict()).
### 3. Logic Implementation
 * **Read Operations:** Use session.query(_ORMClass).filter(...).
 * **Write Operations:** - For add_or_update, use session.merge(_ORMClass(...)) or check for existence then update.
   * Ensure session.commit() is handled by the context manager or called explicitly if needed.
 * **Validation:** Preserve all string .strip(), ValueError raises, and logging from the legacy code.
 * **Caching:** Carry over any @functools.lru_cache used in the legacy service.
### 4. Structure Example
```python
from ..models.coordinator import CoordinatorRecord, _CoordinatorRecord
from ...shared.db.engine import get_session

def get_coordinator(coordinator_id: int) -> CoordinatorRecord | None:
    with get_session() as session:
        orm_obj = session.query(_CoordinatorRecord).filter(_CoordinatorRecord.id == coordinator_id).first()
        return CoordinatorRecord(**orm_obj.to_dict()) if orm_obj else None

```
## 🚦 Execution Steps
 1. Scan the services/ directory to identify all functions and their logic.
 2. Scan the db/ directory to identify the raw SQL equivalent.
 3. Generate the consolidated SQLAlchemy service in the sqlalchemy_services/ folder.
 4. Report:
   * **Entity:** <name>
   * **Methods Migrated:** <list of functions>
   * **Dependencies:** get_session, _ORMRecord
   * **Status:** Completed
