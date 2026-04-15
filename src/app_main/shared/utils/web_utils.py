"""

"""

import logging
from typing import List, Optional

logger = logging.getLogger(__name__)


def parse_select_fields(select_param: Optional[str]) -> Optional[List[str]]:
    """Parse the select parameter into a list of field names."""
    if not select_param:
        return None
    return [f.strip() for f in select_param.split(",") if f.strip()]
