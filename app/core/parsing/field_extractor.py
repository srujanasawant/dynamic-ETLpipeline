import json
import re
from typing import Dict, Any, List
from .type_inference import TypeInference

KEYVAL_RE = re.compile(r"^\s*([A-Za-z0-9 _\-\(\)]+)\s*:\s*(.+)$")


class FieldExtractor:
    """
    Extracts structured key->value fields from fragments.
    Supports:
      - explicit JSON blocks
      - inline JSON blocks
      - key:value fragments
    """

    def extract_fields(self, fragments: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        results = []

        for frag in fragments:
            ftype = frag["type"]
            content = frag["content"]

            # JSON blocks
            if ftype in ("json_block", "inline_json"):
                try:
                    obj = json.loads(content)
                    results.append({
                        "fields": self._infer_field_types(obj),
                        "source": ftype
                    })
                except json.JSONDecodeError:
                    continue

            # Key-value fragments
            elif ftype == "key_value":
                kv_fields = {}
                for line in content.splitlines():
                    m = KEYVAL_RE.match(line)
                    if m:
                        key = m.group(1).strip()
                        val = m.group(2).strip()
                        kv_fields[key] = val

                results.append({
                    "fields": self._infer_field_types(kv_fields),
                    "source": "key_value"
                })

            # Ignore paragraphs/headings here

        return results

    def _infer_field_types(self, obj: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        """
        Convert every field into:
          { value: "...", type: "string/int/etc." }
        """
        out = {}
        for key, value in obj.items():
            if value is None:
                out[key] = {"value": None, "type": "null"}
                continue

            if isinstance(value, (dict, list)):
                out[key] = {"value": value, "type": "json"}
                continue

            val_str = str(value).strip()
            inferred = TypeInference.infer_type(val_str)

            out[key] = {"value": val_str, "type": inferred}

        return out
