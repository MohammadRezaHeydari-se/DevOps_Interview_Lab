from __future__ import annotations

from pathlib import Path
from typing import List

from .json_io import read_json_file
from .validators import validate_question
from .models import Question


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
            raw = read_json_file(fname)
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
