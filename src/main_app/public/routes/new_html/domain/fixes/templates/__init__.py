from .delete_templates import (
    matches_deletion_pattern,
    check_temp_to_delete,
    remove_templates,
    remove_lead_templates,

)
from .fix_templates import (
    add_missing_title,
)

__all__ = [
    "matches_deletion_pattern",
    "check_temp_to_delete",
    "remove_templates",
    "remove_lead_templates",
    "add_missing_title",
]
