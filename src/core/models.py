from __future__ import annotations

from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class Question:
    id: str
    category: str
    difficulty: str
    type: str
    question: str
    shortAnswer: str
    explanation: str
    followUps: List[str]

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "category": self.category,
            "difficulty": self.difficulty,
            "type": self.type,
            "question": self.question,
            "shortAnswer": self.shortAnswer,
            "explanation": self.explanation,
            "followUps": list(self.followUps),
        }
