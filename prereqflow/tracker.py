"""Seguimiento de progreso académico y soporte avanzado de electivas.

Gestiona el progreso de un estudiante a través de múltiples periodos
académicos (semestres), incluyendo el registro de cursos aprobados,
créditos acumulados y la selección de asignaturas electivas dentro
de grupos definidos. Proporciona capacidades de simulación what-if
para explorar diferentes rutas de avance.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set

from .graph import PrereqGraph
from .models import Course


@dataclass
class StudentRecord:
    """Registro completo del progreso académico de un estudiante.

    Almacena el historial de cursos aprobados semestre a semestre,
    los créditos totales acumulados y las selecciones de electivas
    realizadas.

    Attributes:
        completed_courses: Conjunto de códigos de cursos aprobados.
        completed_by_semester: Mapeo de semestre (1-indexed) a
            lista de códigos de cursos aprobados en ese semestre.
        current_semester: Último semestre cursado.
        total_credits: Total de créditos aprobados acumulados.
        elective_selections: Mapeo de nombre de grupo electivo a
            código del curso seleccionado.
    """
    completed_courses: Set[str] = field(default_factory=set)
    completed_by_semester: Dict[int, List[str]] = field(default_factory=dict)
    current_semester: int = 0
    total_credits: int = 0
    elective_selections: Dict[str, str] = field(default_factory=dict)


class ElectiveManager:
    """Gestor de grupos electivos y reglas de selección.

    Administra la configuración de grupos electivos, permitiendo
    definir reglas como "seleccionar N cursos del grupo" o
    "seleccionar hasta M créditos del grupo". Valida que las
    selecciones del estudiante cumplan con las reglas definidas.
    """

    def __init__(self) -> None:
        self.elective_groups: Dict[str, "ElectiveGroup"] = {}

    def add_group(self, group: "ElectiveGroup") -> None:
        """Registra un grupo electivo en el gestor.

        Args:
            group: Grupo electivo a registrar.
        """
        self.elective_groups[group.name] = group

    def add_course_to_group(self, group_name: str, course_code: str) -> None:
        """Asigna un curso a un grupo electivo existente.

        Args:
            group_name: Nombre del grupo electivo.
            course_code: Código del curso a asignar al grupo.
        """
        if group_name in self.elective_groups:
            self.elective_groups[group_name].course_codes.add(course_code)

    def get_available_electives(
        self, graph: PrereqGraph, completed: Set[str]
    ) -> Dict[str, List[Course]]:
        """Retorna los cursos electivos disponibles por grupo.

        Para cada grupo electivo, filtra los cursos cuyos
        prerrequisitos están completados y que aún no han sido
        cursados.

        Args:
            graph: Grafo de prerrequisitos del programa.
            completed: Conjunto de códigos de cursos ya aprobados.

        Returns:
            Diccionario que mapea nombre de grupo electivo a lista
            de cursos disponibles.
        """
        result: Dict[str, List[Course]] = {}
        for group_name, group in self.elective_groups.items():
            available = []
            for code in group.course_codes:
                if code in completed:
                    continue
                course = graph.courses.get(code)
                if course is None:
                    continue
                prereqs = graph.get_prerequisites(code)
                if not prereqs.issubset(completed):
                    continue
                available.append(course)
            if available:
                result[group_name] = sorted(available, key=lambda c: c.code)
        return result

    def validate_selection(
        self, group_name: str, selected_codes: Set[str]
    ) -> List[str]:
        """Valida que una selección cumpla con las reglas del grupo.

        Args:
            group_name: Nombre del grupo electivo.
            selected_codes: Conjunto de códigos seleccionados.

        Returns:
            Lista de mensajes de error. Vacía si la selección es válida.
        """
        errors: List[str] = []
        group = self.elective_groups.get(group_name)
        if group is None:
            errors.append(f"El grupo electivo '{group_name}' no existe.")
            return errors

        invalid = selected_codes - group.course_codes
        if invalid:
            errors.append(
                f"Los cursos {invalid} no pertenecen al grupo '{group_name}'."
            )

        if group.min_select is not None and len(selected_codes) < group.min_select:
            errors.append(
                f"Debe seleccionar al menos {group.min_select} curso(s) "
                f"del grupo '{group_name}'."
            )

        if group.max_select is not None and len(selected_codes) > group.max_select:
            errors.append(
                f"No puede seleccionar más de {group.max_select} curso(s) "
                f"del grupo '{group_name}'."
            )

        if group.min_credits is not None:
            total = sum(
                self.elective_groups[group_name].course_credits.get(c, 0)
                for c in selected_codes
            )
            if total < group.min_credits:
                errors.append(
                    f"Debe completar al menos {group.min_credits} créditos "
                    f"en el grupo '{group_name}'."
                )

        return errors


@dataclass
class ElectiveGroup:
    """Define un grupo de asignaturas electivas con reglas de selección.

    Attributes:
        name: Nombre del grupo electivo (ej. "Tecnologías Emergentes").
        course_codes: Conjunto de códigos de cursos que pertenecen al grupo.
        course_credits: Mapeo de código de curso a créditos (para validación).
        min_select: Número mínimo de cursos a seleccionar (opcional).
        max_select: Número máximo de cursos a seleccionar (opcional).
        min_credits: Mínimo de créditos a completar en el grupo (opcional).
        description: Descripción textual del grupo.
    """
    name: str
    course_codes: Set[str] = field(default_factory=set)
    course_credits: Dict[str, int] = field(default_factory=dict)
    min_select: Optional[int] = None
    max_select: Optional[int] = None
    min_credits: Optional[int] = None
    description: str = ""


class ProgressTracker:
    """Seguimiento del progreso académico multi-periodo.

    Permite registrar el avance de un estudiante semestre a semestre,
    consultar el estado actual, simular decisiones futuras y verificar
    el cumplimiento de requisitos de graduación.
    """

    def __init__(self, graph: PrereqGraph) -> None:
        self.graph = graph
        self.record = StudentRecord()

    def complete_semester(
        self, semester_courses: List[str], semester_number: Optional[int] = None
    ) -> None:
        """Registra la finalización de un semestre con sus cursos.

        Args:
            semester_courses: Lista de códigos de cursos aprobados.
            semester_number: Número de semestre. Si es None, se usa
                el siguiente al último registrado.

        Raises:
            ValueError: Si algún curso no existe en el grafo o si
                algún prerrequisito no está completado.
        """
        if semester_number is None:
            semester_number = self.record.current_semester + 1

        for code in semester_courses:
            code = code.strip().upper()
            if code not in self.graph.courses:
                raise ValueError(f"El curso {code} no existe en el plan de estudios.")
            prereqs = self.graph.get_prerequisites(code)
            missing = prereqs - self.record.completed_courses - set(semester_courses)
            if missing:
                raise ValueError(
                    f"No se puede cursar {code}: faltan prerrequisitos {missing}."
                )

        self.record.completed_by_semester[semester_number] = [
            c.strip().upper() for c in semester_courses
        ]
        for code in semester_courses:
            code = code.strip().upper()
            if code not in self.record.completed_courses:
                self.record.completed_courses.add(code)
                self.record.total_credits += self.graph.courses[code].credits

        if semester_number > self.record.current_semester:
            self.record.current_semester = semester_number

    def get_completed_courses(self) -> Set[str]:
        """Retorna el conjunto de códigos de cursos aprobados.

        Returns:
            Conjunto de códigos de cursos completados.
        """
        return set(self.record.completed_courses)

    def get_completed_credits(self) -> int:
        """Retorna el total de créditos aprobados.

        Returns:
            Suma de créditos de todos los cursos completados.
        """
        return self.record.total_credits

    def get_eligible_courses(self, semester: int = 1) -> List[Course]:
        """Retorna los cursos elegibles para el próximo semestre.

        Args:
            semester: Semestre para el cual consultar elegibilidad.

        Returns:
            Lista de cursos disponibles para cursar.
        """
        return self.graph.eligible_courses(
            completed=self.record.completed_courses,
            semester=semester,
            completed_credits=self.record.total_credits,
        )

    def get_progress_summary(self) -> Dict[str, object]:
        """Genera un resumen completo del progreso académico.

        Returns:
            Diccionario con estadísticas de progreso: semestre actual,
            créditos, cursos aprobados, cursos restantes, porcentaje
            de avance y distribución por área académica.
        """
        total_courses = len(self.graph.courses)
        total_credits_program = sum(c.credits for c in self.graph.courses.values())
        completed = self.record.completed_courses
        remaining_courses = total_courses - len(completed)

        area_distribution: Dict[str, int] = {}
        for code in completed:
            course = self.graph.courses.get(code)
            if course and course.area:
                area_distribution[course.area] = area_distribution.get(course.area, 0) + 1

        return {
            "semestre_actual": self.record.current_semester,
            "cursos_aprobados": len(completed),
            "cursos_totales": total_courses,
            "cursos_restantes": remaining_courses,
            "creditos_aprobados": self.record.total_credits,
            "creditos_totales": total_credits_program,
            "porcentaje_avance": round(
                (len(completed) / total_courses) * 100 if total_courses > 0 else 0, 1
            ),
            "distribucion_areas": area_distribution,
            "electivas_seleccionadas": dict(self.record.elective_selections),
        }

    def simulate_semester(
        self, course_codes: List[str], semester: Optional[int] = None
    ) -> Dict[str, object]:
        """Simula la aprobación de cursos en un semestre sin modificar el registro.

        Útil para exploración what-if: permite ver cómo cambiaría el
        progreso si se aprueban ciertos cursos.

        Args:
            course_codes: Códigos de cursos a simular como aprobados.
            semester: Semestre de la simulación.

        Returns:
            Diccionario con el estado simulado: cursos elegibles,
            créditos totales, cursos aprobados, etc.
        """
        simulated_completed = set(self.record.completed_courses)
        simulated_credits = self.record.total_credits
        for code in course_codes:
            code = code.strip().upper()
            if code not in simulated_completed and code in self.graph.courses:
                simulated_completed.add(code)
                simulated_credits += self.graph.courses[code].credits

        next_sem = semester or (self.record.current_semester + 1)
        eligible = self.graph.eligible_courses(
            completed=simulated_completed,
            semester=next_sem,
            completed_credits=simulated_credits,
        )

        return {
            "semestre_simulado": next_sem,
            "cursos_aprobados_simulados": len(simulated_completed),
            "creditos_simulados": simulated_credits,
            "cursos_elegibles": [c.code for c in eligible],
            "nuevos_aprobados": course_codes,
        }

    def select_elective(
        self, group_name: str, course_code: str, manager: ElectiveManager
    ) -> List[str]:
        """Selecciona un curso electivo dentro de un grupo.

        Valida que el curso pertenezca al grupo y que el grupo tenga
        reglas de selección satisfechas.

        Args:
            group_name: Nombre del grupo electivo.
            course_code: Código del curso a seleccionar.
            manager: Gestor de grupos electivos.

        Returns:
            Lista de errores de validación. Vacía si la selección
            fue exitosa.
        """
        errors = manager.validate_selection(group_name, {course_code})
        if not errors:
            self.record.elective_selections[group_name] = course_code
        return errors

    def get_elective_requirements_status(
        self, manager: ElectiveManager
    ) -> Dict[str, Dict[str, object]]:
        """Evalúa el estado de cumplimiento de todos los grupos electivos.

        Args:
            manager: Gestor de grupos electivos.

        Returns:
            Diccionario mapeando nombre de grupo a su estado:
            cursos disponibles, seleccionados, reglas, satisfecho.
        """
        status: Dict[str, Dict[str, object]] = {}
        for group_name, group in manager.elective_groups.items():
            selected = self.record.elective_selections.get(group_name)
            selected_set = {selected} if selected else set()
            errors = manager.validate_selection(group_name, selected_set)
            completed_in_group = group.course_codes & self.record.completed_courses
            status[group_name] = {
                "descripcion": group.description,
                "cursos_en_grupo": sorted(group.course_codes),
                "cursos_completados": sorted(completed_in_group),
                "seleccion_actual": selected,
                "min_select": group.min_select,
                "max_select": group.max_select,
                "min_credits": group.min_credits,
                "satisfecho": len(errors) == 0,
                "errores": errors,
            }
        return status
