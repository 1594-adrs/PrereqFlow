"""Grafo dirigido de prerrequisitos académicos.

Implementa la clase PrereqGraph que modela un plan de estudios como un
grafo dirigido acíclico (DAG). Proporciona operaciones fundamentales:
inserción/eliminación de nodos y aristas, detección de ciclos mediante
DFS, ordenamiento topológico, cierre transitivo de prerrequisitos,
cálculo de profundidad de dependencias y consulta de cursos elegibles.
"""

from typing import Dict, List, Optional, Set

from .models import Course


class PrereqGraph:
    """Grafo dirigido que modela las relaciones de prerrequisito entre asignaturas.

    Mantiene diccionarios paralelos para consultas eficientes en ambas
    direcciones de la dependencia (prerrequisitos y dependientes), así
    como un registro de corequisitos.

    La clase garantiza que los códigos de curso se almacenan en mayúsculas
    sin espacios, normalizando toda entrada.

    Attributes:
        courses: Mapeo de código de curso a instancia de Course.
        prerequisites: Mapeo de código de curso al conjunto de sus
            prerrequisitos directos.
        dependents: Mapeo inverso: código de curso al conjunto de cursos
            que dependen directament de él.
        co_requisites: Mapeo de código de curso al conjunto de sus
            corequisitos (relación simétrica).
    """

    def __init__(self) -> None:
        self.courses: Dict[str, Course] = {}
        self.prerequisites: Dict[str, Set[str]] = {}
        self.dependents: Dict[str, Set[str]] = {}
        self.co_requisites: Dict[str, Set[str]] = {}

    def add_course(self, course: Course) -> None:
        """Agrega un curso al grafo.

        Normaliza el código a mayúsculas sin espacios. Inicializa las
        estructuras auxiliares (prerrequisitos, dependientes,
        corequisitos) si el curso es nuevo. Los corequisitos declarados
        en el objeto Course se registran automáticamente.

        Args:
            course: Instancia de Course a agregar.

        Raises:
            ValueError: Si el código del curso está vacío.

        Complejidad: O(k) donde k es el número de corequisitos del curso.
        """
        if not course.code:
            raise ValueError("Course code is required")
        code = course.code.strip().upper()
        course.code = code
        self.courses[code] = course
        self.prerequisites.setdefault(code, set())
        self.dependents.setdefault(code, set())
        self.co_requisites.setdefault(code, set())
        for co_req in course.co_requisites:
            self.co_requisites.setdefault(co_req.strip().upper(), set()).add(code)

    def add_prerequisite(self, course_code: str, prereq_code: str) -> None:
        """Agrega una relación de prerrequisito entre dos cursos.

        Establece que prereq_code debe cursarse antes que course_code.

        Args:
            course_code: Código del curso que requiere el prerrequisito.
            prereq_code: Código del curso que actúa como prerrequisito.

        Raises:
            ValueError: Si ambos códigos son iguales (autoprerrequisito).
            KeyError: Si alguno de los códigos no existe en el grafo.

        Complejidad: O(1).
        """
        course_code = course_code.strip().upper()
        prereq_code = prereq_code.strip().upper()
        if course_code == prereq_code:
            raise ValueError("A course cannot be its own prerequisite")
        if course_code not in self.courses or prereq_code not in self.courses:
            raise KeyError("Both course and prerequisite must exist in the graph")
        self.prerequisites.setdefault(course_code, set()).add(prereq_code)
        self.dependents.setdefault(prereq_code, set()).add(course_code)

    def add_co_requisite(self, course_code: str, co_req_code: str) -> None:
        """Agrega una relación de corequisito simétrica entre dos cursos.

        Establece que ambos cursos deben cursarse simultáneamente.

        Args:
            course_code: Código del primer curso.
            co_req_code: Código del segundo curso.

        Raises:
            ValueError: Si ambos códigos son iguales.
            KeyError: Si alguno de los códigos no existe en el grafo.

        Complejidad: O(1).
        """
        course_code = course_code.strip().upper()
        co_req_code = co_req_code.strip().upper()
        if course_code == co_req_code:
            raise ValueError("A course cannot be its own co-requisite")
        if course_code not in self.courses or co_req_code not in self.courses:
            raise KeyError("Both course and co-requisite must exist in the graph")
        self.co_requisites.setdefault(course_code, set()).add(co_req_code)
        self.co_requisites.setdefault(co_req_code, set()).add(course_code)

    def remove_course(self, course_code: str) -> None:
        """Elimina un curso y todas sus relaciones del grafo.

        Limpia todas las referencias al curso en las estructuras de
        prerrequisitos, dependientes y corequisitos antes de eliminarlo.

        Args:
            course_code: Código del curso a eliminar.

        Complejidad: O(V + E) en el peor caso.
        """
        course_code = course_code.strip().upper()
        if course_code not in self.courses:
            return
        for prereq in self.prerequisites.get(course_code, set()):
            self.dependents.get(prereq, set()).discard(course_code)
        for dependent in self.dependents.get(course_code, set()):
            self.prerequisites.get(dependent, set()).discard(course_code)
        for co_req in self.co_requisites.get(course_code, set()):
            self.co_requisites.get(co_req, set()).discard(course_code)
        self.prerequisites.pop(course_code, None)
        self.dependents.pop(course_code, None)
        self.co_requisites.pop(course_code, None)
        self.courses.pop(course_code, None)

    def remove_prerequisite(self, course_code: str, prereq_code: str) -> None:
        """Elimina una relación de prerrequisito específica.

        Args:
            course_code: Código del curso que tenía el prerrequisito.
            prereq_code: Código del prerrequisito a eliminar.

        Complejidad: O(1).
        """
        course_code = course_code.strip().upper()
        prereq_code = prereq_code.strip().upper()
        self.prerequisites.get(course_code, set()).discard(prereq_code)
        self.dependents.get(prereq_code, set()).discard(course_code)

    def remove_co_requisite(self, course_code: str, co_req_code: str) -> None:
        """Elimina una relación de corequisito (en ambos sentidos).

        Args:
            course_code: Código del primer curso.
            co_req_code: Código del segundo curso.

        Complejidad: O(1).
        """
        course_code = course_code.strip().upper()
        co_req_code = co_req_code.strip().upper()
        self.co_requisites.get(course_code, set()).discard(co_req_code)
        self.co_requisites.get(co_req_code, set()).discard(course_code)

    def get_prerequisites(self, course_code: str) -> Set[str]:
        """Retorna los prerrequisitos directos de un curso.

        Args:
            course_code: Código del curso a consultar.

        Returns:
            Conjunto de códigos de cursos prerrequisito (copia defensiva).

        Complejidad: O(1).
        """
        return set(self.prerequisites.get(course_code.strip().upper(), set()))

    def get_dependents(self, course_code: str) -> Set[str]:
        """Retorna los cursos que dependen directamente de este.

        Args:
            course_code: Código del curso a consultar.

        Returns:
            Conjunto de códigos de cursos que tienen este como prerrequisito.

        Complejidad: O(1).
        """
        return set(self.dependents.get(course_code.strip().upper(), set()))

    def get_co_requisites(self, course_code: str) -> Set[str]:
        """Retorna los corequisitos de un curso.

        Args:
            course_code: Código del curso a consultar.

        Returns:
            Conjunto de códigos de cursos corequisito.

        Complejidad: O(1).
        """
        return set(self.co_requisites.get(course_code.strip().upper(), set()))

    def get_prerequisite_closure(self, course_code: str) -> Set[str]:
        """Calcula el cierre transitivo de prerrequisitos.

        Obtiene todos los cursos que deben aprobarse directa o
        indirectamente antes de poder cursar el curso dado.

        Args:
            course_code: Código del curso a consultar.

        Returns:
            Conjunto con todos los prerrequisitos (directos e indirectos).

        Complejidad: O(V + E) en el peor caso.
        """
        closure: Set[str] = set()

        def visit(node: str) -> None:
            for prereq in self.get_prerequisites(node):
                if prereq not in closure:
                    closure.add(prereq)
                    visit(prereq)

        visit(course_code.strip().upper())
        return closure

    def course_dependency_depth(self, course_code: str) -> int:
        """Calcula la profundidad máxima de la cadena de prerrequisitos.

        La profundidad es la longitud de la cadena más larga de
        prerrequisitos que debe completarse antes de este curso.
        Un curso sin prerrequisitos tiene profundidad 0.

        Args:
            course_code: Código del curso a consultar.

        Returns:
            Profundidad máxima de dependencias.

        Complejidad: O(V + E) en el peor caso.
        """
        course_code = course_code.strip().upper()
        if not self.get_prerequisites(course_code):
            return 0
        return 1 + max(self.course_dependency_depth(prereq) for prereq in self.get_prerequisites(course_code))

    def completed_credits(self, completed: Set[str]) -> int:
        """Calcula el total de créditos de un conjunto de cursos completados.

        Args:
            completed: Conjunto de códigos de cursos aprobados.

        Returns:
            Suma de créditos de los cursos aprobados que existen en el grafo.

        Complejidad: O(k) donde k = |completed|.
        """
        return sum(
            self.courses[code].credits
            for code in completed
            if code in self.courses
        )

    def critical_courses(self) -> List[Course]:
        """Identifica los cursos más críticos del plan de estudios.

        Ordena los cursos por profundidad de dependencias, número de
        dependientes y dificultad. Los cursos al inicio de la lista
        son los que más impacto tienen en el plan (más prerrequisitos
        y más cursos que dependen de ellos).

        Returns:
            Lista de cursos ordenados por criticidad descendente.

        Complejidad: O(V log V + V * (V + E)) por el ordenamiento
            y los cálculos de profundidad.
        """
        return sorted(
            self.courses.values(),
            key=lambda course: (
                self.course_dependency_depth(course.code),
                len(self.get_dependents(course.code)),
                course.difficulty,
            ),
            reverse=True,
        )

    def detect_cycle(self) -> bool:
        """Detecta si el grafo contiene algún ciclo (DFS con pila).

        Utiliza una variante del algoritmo DFS con seguimiento de la
        pila de recursión actual para detectar back edges, que indican
        la presencia de ciclos.

        Returns:
            True si se detecta al menos un ciclo en el grafo.

        Complejidad: O(V + E).
        """
        visited: Set[str] = set()
        stack: Set[str] = set()

        def visit(node: str) -> bool:
            if node in stack:
                return True
            if node in visited:
                return False
            visited.add(node)
            stack.add(node)
            for prereq in self.prerequisites.get(node, set()):
                if visit(prereq):
                    return True
            stack.remove(node)
            return False

        return any(visit(node) for node in self.courses)

    def topological_sort(self) -> List[Course]:
        """Genera un ordenamiento topológico del grafo mediante DFS.

        Produce una ordenación lineal de los cursos tal que todos los
        prerrequisitos aparecen antes que los cursos que los requieren.
        Lanza un error si el grafo contiene ciclos.

        Returns:
            Lista de cursos en orden topológico.

        Raises:
            ValueError: Si el grafo contiene ciclos.

        Complejidad: O(V + E).
        """
        if self.detect_cycle():
            raise ValueError("The course graph contains a cycle and cannot be sorted")
        visited: Set[str] = set()
        ordered: List[Course] = []

        def visit(node: str) -> None:
            if node in visited:
                return
            visited.add(node)
            for prereq in sorted(self.prerequisites.get(node, set())):
                visit(prereq)
            ordered.append(self.courses[node])

        for node in sorted(self.courses):
            visit(node)

        return ordered

    def eligible_courses(
        self,
        completed: Optional[Set[str]] = None,
        semester: Optional[int] = None,
        completed_credits: Optional[int] = None,
    ) -> List[Course]:
        """Retorna los cursos que pueden cursarse dado el estado actual.

        Un curso es elegible si cumple todas las siguientes condiciones:
        - No ha sido completado.
        - Todos sus prerrequisitos están completados.
        - Si tiene requisito de créditos mínimos, estos están satisfechos.
        - Si se especifica un semestre, el curso se ofrece en él.
        - Sus corequisitos también son elegibles (o ya están completados).

        Args:
            completed: Conjunto de códigos de cursos ya aprobados.
            semester: Semestre para el cual se consulta elegibilidad.
            completed_credits: Total de créditos aprobados. Si es None,
                se calcula automáticamente.

        Returns:
            Lista de cursos elegibles ordenados por código.

        Complejidad: O(V * (V + E)) en el peor caso.
        """
        completed = {code.strip().upper() for code in (completed or set())}
        if completed_credits is None:
            completed_credits = self.completed_credits(completed)
        eligible: List[Course] = []
        for code, course in self.courses.items():
            if code in completed:
                continue
            prereqs = self.get_prerequisites(code)
            if not prereqs.issubset(completed):
                continue
            if course.min_completed_credits is not None and completed_credits < course.min_completed_credits:
                continue
            if semester is not None and not course.is_offered_in_semester(semester):
                continue
            missing_co_reqs = [
                co_req
                for co_req in self.get_co_requisites(code)
                if co_req not in completed
            ]
            can_take = True
            for co_req_code in missing_co_reqs:
                co_req_course = self.courses.get(co_req_code)
                if co_req_course is None:
                    can_take = False
                    break
                co_prereqs = self.get_prerequisites(co_req_code)
                if not co_prereqs.issubset(completed):
                    can_take = False
                    break
                if semester is not None and not co_req_course.is_offered_in_semester(semester):
                    can_take = False
                    break
                if co_req_course.min_completed_credits is not None and completed_credits < co_req_course.min_completed_credits:
                    can_take = False
                    break
            if not can_take:
                continue
            eligible.append(course)
        return sorted(eligible, key=lambda c: c.code)

    def to_dict(self) -> Dict[str, object]:
        """Convierte el grafo completo a un diccionario serializable.

        Returns:
            Diccionario con listas de cursos, aristas de prerrequisito
            y aristas de corequisito.

        Complejidad: O(V + E).
        """
        return {
            "courses": [course.to_dict() for course in self.courses.values()],
            "prerequisites": [
                {"course": course, "prereq": prereq}
                for course, prereqs in self.prerequisites.items()
                for prereq in prereqs
            ],
            "co_requisites": [
                {"course": course, "co_req": co_req}
                for course, co_reqs in self.co_requisites.items()
                for co_req in co_reqs
            ],
        }

    @staticmethod
    def from_dict(data: Dict[str, object]) -> "PrereqGraph":
        """Construye un PrereqGraph desde un diccionario.

        Args:
            data: Diccionario con las claves 'courses', 'prerequisites'
                y 'co_requisites' en el formato generado por to_dict().

        Returns:
            Nueva instancia de PrereqGraph poblada con los datos.

        Complejidad: O(V + E).
        """
        graph = PrereqGraph()
        for entry in data.get("courses", []):
            course = Course.from_dict(entry)
            graph.add_course(course)
        for edge in data.get("prerequisites", []):
            graph.add_prerequisite(str(edge["course"]), str(edge["prereq"]))
        for edge in data.get("co_requisites", []):
            graph.add_co_requisite(str(edge["course"]), str(edge["co_req"]))
        return graph
