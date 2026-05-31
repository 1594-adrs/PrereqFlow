"""Persistencia de datos del grafo de prerrequisitos.

Proporciona funciones para serializar y deserializar el grafo de
asignaturas en formatos JSON y CSV. Permite guardar y cargar planes
de estudio completos con todas sus relaciones.
"""

import csv
import json
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Set

from .graph import PrereqGraph
from .models import Course


def save_graph_to_json(graph: PrereqGraph, path: str) -> None:
    """Guarda el grafo completo en un archivo JSON.

    Serializa cursos, prerrequisitos y corequisitos en formato JSON
    con indentación para legibilidad.

    Args:
        graph: Grafo de prerrequisitos a guardar.
        path: Ruta del archivo JSON de salida.

    Complejidad: O(V + E).
    """
    data = graph.to_dict()
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(data, handle, indent=2)


def load_graph_from_json(path: str) -> PrereqGraph:
    """Carga un grafo desde un archivo JSON.

    Lee el archivo JSON generado por save_graph_to_json y reconstruye
    el grafo completo con todas sus relaciones.

    Args:
        path: Ruta del archivo JSON de entrada.

    Returns:
        Grafo de prerrequisitos reconstruido.

    Complejidad: O(V + E).
    """
    with open(path, "r", encoding="utf-8") as handle:
        data = json.load(handle)
    return PrereqGraph.from_dict(data)


def save_graph_to_csv(graph: PrereqGraph, path: str) -> None:
    """Guarda el grafo completo en un archivo CSV.

    Cada fila del CSV representa un curso con sus prerrequisitos
    serializados como lista separada por punto y coma. Crea los
    directorios padre si no existen.

    Args:
        graph: Grafo de prerrequisitos a guardar.
        path: Ruta del archivo CSV de salida.

    Complejidad: O(V + E).
    """
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
    """Carga un grafo desde un archivo CSV.

    Lee el archivo CSV generado por save_graph_to_csv y reconstruye
    el grafo. Los prerrequisitos se leen de la columna 'prerequisites'
    (lista separada por ;) y se agregan en una segunda pasada.

    Args:
        path: Ruta del archivo CSV de entrada.

    Returns:
        Grafo de prerrequisitos reconstruido.

    Complejidad: O(V + E).
    """
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
            ]
            or None,
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
        prerequisites = [
            pr.strip()
            for pr in row.get("prerequisites", "").split(";")
            if pr.strip()
        ]
        for prereq in prerequisites:
            graph.add_prerequisite(row["code"], prereq)
    return graph
