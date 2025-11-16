import re
from datetime import datetime
from typing import Any, Optional

DATE_PATTERNS = [
    "%Y-%m-%d",
    "%d-%m-%Y",
    "%m-%d-%Y",
    "%d/%m/%Y",
    "%m/%d/%Y",
    "%Y/%m/%d",
]


class TypeInference:
    """
    Rule-based type inference for fields.
    Determines: int, float, bool, date, string.
    """

    @staticmethod
    def infer_type(value: str) -> str:
        v = value.strip()

        # Boolean
        if v.lower() in ("true", "false", "yes", "no"):
            return "boolean"

        # Integer
        if re.fullmatch(r"[-+]?\d+", v):
            return "integer"

        # Float
        if re.fullmatch(r"[-+]?\d*\.\d+", v):
            return "float"

        # Date
        if TypeInference._looks_like_date(v):
            return "date"

        # Default
        return "string"

    @staticmethod
    def _looks_like_date(value: str) -> bool:
        for fmt in DATE_PATTERNS:
            try:
                datetime.strptime(value, fmt)
                return True
            except ValueError:
                continue
        return False
