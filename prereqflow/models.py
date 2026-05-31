"""Modelo de datos del dominio académico.

Define la clase Course como dataclass inmutable que representa una
asignatura universitaria con todos sus atributos académicos.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set


@dataclass
class Course:
    """Representa una asignatura universitaria dentro del plan de estudios.

    Cada Course encapsula la información académica completa de una materia:
    código único, nombre, créditos, área, prerrequisitos y corequisitos,
    semestre sugerido, disponibilidad y metadatos adicionales.

    Attributes:
        code: Código único de la asignatura (ej. SIS018).
        name: Nombre completo de la asignatura.
        credits: Número de créditos académicos. Valor por defecto 3.
        semester: Semestre sugerido en el plan de estudios.
        area: Área académica (Matemáticas, Computación, Física, etc.).
        elective_group: Grupo electivo al que pertenece, si aplica.
        min_completed_credits: Mínimo de créditos aprobados requeridos.
        required: True si es obligatoria, False si es electiva.
        co_requisites: Conjunto de códigos de cursos que deben tomarse
            simultáneamente.
        weight: Peso relativo del curso para planificación (1.0 por defecto).
        difficulty: Nivel de dificultad estimado (1.0 por defecto).
        semester_offered: Lista de semestres en que se ofrece el curso
            (None = todos los semestres).
        metadata: Diccionario para metadatos adicionales extensibles.
    """
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
        """Convierte el curso a un diccionario serializable a JSON.

        Returns:
            Diccionario con todos los atributos del curso. Los conjuntos
            se convierten a listas ordenadas para serialización.
        """
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
        """Determina si el curso se ofrece en un semestre específico.

        Si el curso no tiene restricción de oferta (semester_offered es
        None), se considera disponible en cualquier semestre. Si la
        oferta está restringida a semestres 1 y/o 2, se normaliza el
        semestre consultado a 1 (impar) o 2 (par).

        Args:
            semester: Número de semestre a consultar (1-indexed).

        Returns:
            True si el curso se ofrece en el semestre indicado.
        """
        if self.semester_offered is None:
            return True
        offered_semesters = set(self.semester_offered)
        if offered_semesters.issubset({1, 2}):
            normalized = 2 if semester % 2 == 0 else 1
            return normalized in offered_semesters
        return semester in offered_semesters

    @staticmethod
    def from_dict(data: Dict[str, object]) -> "Course":
        """Crea una instancia de Course desde un diccionario.

        Realiza conversión de tipos y limpieza de espacios en blanco.
        Los valores ausentes se reemplazan por None o valores por defecto.

        Args:
            data: Diccionario con los atributos del curso.

        Returns:
            Nueva instancia de Course construida desde el diccionario.
        """
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
