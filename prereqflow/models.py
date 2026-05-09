from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set


@dataclass
class Course:
    code: str
    name: str
    credits: int = 3
    semester: Optional[int] = None
    area: Optional[str] = None
    elective_group: Optional[str] = None
    min_completed_credits: Optional[int] = None
    required: bool = True
    co_requisites: Set[str] = field(default_factory=set)
    weight: float = 1.0
    difficulty: float = 1.0
    semester_offered: Optional[List[int]] = None
    metadata: Dict[str, object] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, object]:
        return {
            "code": self.code,
            "name": self.name,
            "credits": self.credits,
            "semester": self.semester,
            "area": self.area,
            "elective_group": self.elective_group,
            "required": self.required,
            "co_requisites": sorted(self.co_requisites),
            "min_completed_credits": self.min_completed_credits,
            "weight": self.weight,
            "difficulty": self.difficulty,
            "semester_offered": self.semester_offered,
            "metadata": self.metadata,
        }

    def is_offered_in_semester(self, semester: int) -> bool:
        if self.semester_offered is None:
            return True
        offered_semesters = set(self.semester_offered)
        if offered_semesters.issubset({1, 2}):
            normalized = 2 if semester % 2 == 0 else 1
            return normalized in offered_semesters
        return semester in offered_semesters

    @staticmethod
    def from_dict(data: Dict[str, object]) -> "Course":
        return Course(
            code=str(data.get("code", "")).strip(),
            name=str(data.get("name", "")).strip(),
            credits=int(data.get("credits", 3)),
            semester=data.get("semester"),
            area=data.get("area"),
            elective_group=data.get("elective_group"),
            required=bool(data.get("required", True)),
            co_requisites=set(data.get("co_requisites", [])),
            min_completed_credits=(int(data.get("min_completed_credits")) if data.get("min_completed_credits") is not None else None),
            weight=float(data.get("weight", 1.0)),
            difficulty=float(data.get("difficulty", 1.0)),
            semester_offered=list(data.get("semester_offered")) if data.get("semester_offered") is not None else None,
            metadata=dict(data.get("metadata", {})),
        )
