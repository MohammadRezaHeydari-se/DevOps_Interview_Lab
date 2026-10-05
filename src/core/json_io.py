"""Shared JSON file reading.

One implementation used by every core data loader.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def read_json_file(path: Path) -> Any:
    """Read and decode a JSON file."""
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)