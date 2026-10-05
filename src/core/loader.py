from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List

from .validators import validate_question
from .models import Question


def _load_json(path: Path) -> List[Dict]:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def load_questions(data_dir: str | None = None) -> List[Question]:
    if data_dir is None:
        base = Path(__file__).resolve().parents[2] / "data" / "questions"
    else:
        base = Path(data_dir)
    questions: List[Question] = []
    if not base.exists():
        return questions
    for fname in sorted(base.iterdir()):
        if not fname.is_file() or not fname.name.endswith(".json"):
            continue
        if fname.name == "schema.json":
            continue
        try:
            raw = _load_json(fname)
        except Exception:
            continue
        if not isinstance(raw, list):
            continue
        for item in raw:
            ok, _ = validate_question(item)
            if not ok:
                continue
            questions.append(
                Question(
                    id=str(item["id"]),
                    category=str(item["category"]),
                    difficulty=str(item["difficulty"]),
                    type=str(item["type"]),
                    question=str(item["question"]),
                    shortAnswer=str(item["shortAnswer"]),
                    explanation=str(item["explanation"]),
                    followUps=[str(f) for f in item["followUps"]],
                )
            )
    return questions
