import csv
import json
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Set

from .graph import PrereqGraph
from .models import Course


def save_graph_to_json(graph: PrereqGraph, path: str) -> None:
    data = graph.to_dict()
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(data, handle, indent=2)


def load_graph_from_json(path: str) -> PrereqGraph:
    with open(path, "r", encoding="utf-8") as handle:
        data = json.load(handle)
    return PrereqGraph.from_dict(data)


def save_graph_to_csv(graph: PrereqGraph, path: str) -> None:
    path_obj = Path(path)
    path_obj.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(
            [
                "code",
                "name",
                "credits",
                "semester",
                "area",
                "semester_offered",
                "min_completed_credits",
                "co_requisites",
                "required",
                "prerequisites",
            ]
        )
        for code, course in sorted(graph.courses.items()):
            prereq_list = ";".join(sorted(graph.get_prerequisites(code)))
            semester_offered = ";".join(str(x) for x in (course.semester_offered or []))
            co_requisites = ";".join(sorted(course.co_requisites))
            writer.writerow(
                [
                    course.code,
                    course.name,
                    course.credits,
                    course.semester or "",
                    course.area or "",
                    semester_offered,
                    course.min_completed_credits or "",
                    co_requisites,
                    int(course.required),
                    prereq_list,
                ]
            )


def load_graph_from_csv(path: str) -> PrereqGraph:
    graph = PrereqGraph()
    with open(path, "r", newline="", encoding="utf-8") as csvfile:
        rows = list(csv.DictReader(csvfile))
    for row in rows:
        course = Course(
            code=row["code"].strip(),
            name=row["name"].strip(),
            credits=int(row.get("credits", 3) or 3),
            semester=int(row["semester"]) if row.get("semester") else None,
            area=row.get("area") or None,
            semester_offered=[
                int(x) for x in row.get("semester_offered", "").split(";") if x.strip()
            ] or None,
            min_completed_credits=(
                int(row["min_completed_credits"])
                if row.get("min_completed_credits")
                else None
            ),
            co_requisites={
                co.strip().upper()
                for co in row.get("co_requisites", "").split(";")
                if co.strip()
            },
            required=bool(int(row.get("required", "1"))) if row.get("required") else True,
        )
        graph.add_course(course)
    for row in rows:
        prerequisites = [pr.strip() for pr in row.get("prerequisites", "").split(";") if pr.strip()]
        for prereq in prerequisites:
            graph.add_prerequisite(row["code"], prereq)
    return graph
