from pathlib import Path
import re
from functools import lru_cache
from typing import Dict

@lru_cache(maxsize=32)
def load_css_variables(path: str) -> Dict[str, str]:
    """
    Load CSS variables from a given CSS file and return them as a dictionary.
    """
    try:
        text = Path(path).read_text(encoding="utf-8")
    except Exception:
        return {}
    pairs = re.findall(r'(--[\w-]+)\s*:\s*([^;]+);', text)
    return {name: value.strip() for name, value in pairs}

