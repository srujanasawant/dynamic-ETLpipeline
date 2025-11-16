from typing import Dict, Any


class DataCleaner:
    """
    Normalizes extracted field values:
      - trim whitespace
      - normalize booleans
      - convert numeric strings
      - convert date strings (pass-through here; validation already done)
    """

    def clean(self, extracted: Dict[str, Any]) -> Dict[str, Any]:
        cleaned = {}

        for key, meta in extracted.items():
            value = meta["value"]
            ftype = meta["type"]

            if value is None:
                cleaned[key] = None
                continue

            v = str(value).strip()

            # Convert booleans
            if ftype == "boolean":
                cleaned[key] = v.lower() in ("true", "yes")
                continue

            # Convert integers
            if ftype == "integer":
                try:
                    cleaned[key] = int(v)
                except ValueError:
                    cleaned[key] = v
                continue

            # Convert floats
            if ftype == "float":
                try:
                    cleaned[key] = float(v)
                except ValueError:
                    cleaned[key] = v
                continue

            # Date — keep string; later schema engine will handle
            if ftype == "date":
                cleaned[key] = v
                continue

            # Fallback: string
            cleaned[key] = v

        return cleaned
