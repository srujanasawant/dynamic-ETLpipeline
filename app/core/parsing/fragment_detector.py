import re
from typing import List, Dict, Any


JSON_BLOCK_RE = re.compile(r"```json\s*(\{[\s\S]*?\})\s*```", re.MULTILINE)
BRACE_JSON_RE = re.compile(r"(\{[\s\S]*?\})", re.MULTILINE)
KEYVAL_RE = re.compile(r"^\s*([A-Za-z0-9 _\-]+)\s*:\s*(.+)$")
HEADING_RE = re.compile(r"^\s{0,3}(#{1,6})\s*(.+)$", re.MULTILINE)


class FragmentDetector:
    """
    Simple rule-based fragment detector for unstructured text.

    It detects and yields fragments of types:
      - json_block: explicit fenced JSON (```json { ... } ```)
      - inline_json: JSON-like {...} blocks
      - key_value: simple "Key: Value" lines (grouped together)
      - heading: markdown headings (# ...)
      - paragraph: plain paragraphs (fallback)
    """

    def __init__(self, min_paragraph_length: int = 10):
        self.min_paragraph_length = min_paragraph_length

    def detect_fragments(self, text: str) -> List[Dict[str, Any]]:
        """
        Given raw text, return a list of fragments where each fragment is a dict:
          {
            "type": "json_block" | "inline_json" | "key_value" | "heading" | "paragraph",
            "content": "...",
            "meta": {...}  # optional metadata
          }
        """
        if not text:
            return []

        fragments: List[Dict[str, Any]] = []

        # 1) Extract fenced JSON blocks first (```json ... ```)
        for m in JSON_BLOCK_RE.finditer(text):
            payload = m.group(1).strip()
            fragments.append({"type": "json_block", "content": payload, "meta": {"source": "fenced_json"}})

        # Remove fenced JSON blocks from text so they don't get double-detected
        text_no_fenced = JSON_BLOCK_RE.sub("\n", text)

        # 2) Detect brace-style JSON blocks remaining
        for m in BRACE_JSON_RE.finditer(text_no_fenced):
            payload = m.group(1).strip()
            # Heuristic: only accept if looks like JSON (starts with { and has colon)
            if ":" in payload:
                fragments.append({"type": "inline_json", "content": payload, "meta": {"source": "brace_json"}})

        # Remove inline JSON blocks to reduce noise
        text_no_json = BRACE_JSON_RE.sub("\n", text_no_fenced)

        # 3) Detect headings (markdown)
        for m in HEADING_RE.finditer(text_no_json):
            level = len(m.group(1))
            title = m.group(2).strip()
            fragments.append({"type": "heading", "content": title, "meta": {"level": level}})

        # 4) Detect groups of key:value lines
        lines = text_no_json.splitlines()
        i = 0
        n = len(lines)
        while i < n:
            line = lines[i]
            # collect contiguous key:value lines
            kv_group = []
            while i < n:
                line = lines[i]
                if KEYVAL_RE.match(line):
                    kv_group.append(line.strip())
                    i += 1
                else:
                    break
            if kv_group:
                # join as a single fragment
                content = "\n".join(kv_group)
                fragments.append({"type": "key_value", "content": content, "meta": {"count": len(kv_group)}})
                continue
            i += 1

        # 5) Remaining paragraphs: split by two or more newlines and filter short ones
        paragraphs = [p.strip() for p in re.split(r"\n{2,}", text_no_json) if p.strip()]
        for p in paragraphs:
            if len(p) < self.min_paragraph_length:
                # skip tiny noise lines
                continue
            # Skip fragments we've already captured (heuristic: exact match)
            already = False
            for f in fragments:
                if f["content"].strip() == p.strip():
                    already = True
                    break
            if already:
                continue
            fragments.append({"type": "paragraph", "content": p, "meta": {"length": len(p)}})

        # 6) Sort fragments by a stable heuristic: prefer structured types first
        order = {"json_block": 0, "inline_json": 1, "key_value": 2, "heading": 3, "paragraph": 4}
        fragments.sort(key=lambda x: (order.get(x.get("type"), 99), -x.get("meta", {}).get("count", 0), -len(x.get("content", ""))))

        return fragments


# simple convenience function
def detect_fragments(text: str) -> List[Dict[str, Any]]:
    detector = FragmentDetector()
    return detector.detect_fragments(text)
