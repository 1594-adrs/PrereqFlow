"""Utilidades compartidas para la interfaz de PrereqFlow.

Proporciona funciones auxiliares para formato de etiquetas de cursos,
selectores unificados y helpers de UI consistentes en toda la aplicación.
"""

from typing import Dict, List

from .graph import PrereqGraph


def course_label(code: str, graph: PrereqGraph) -> str:
    """Genera una etiqueta legible para un curso: ``CÓDIGO — Nombre``.

    Args:
        code: Código del curso.
        graph: Grafo que contiene los datos del curso.

    Returns:
        String con formato ``SIS018 — Estructura de Datos``.
        Si el curso no existe, retorna solo el código.
    """
    course = graph.courses.get(code)
    if course is None:
        return code
    return f"{course.code} — {course.name}"


def sorted_course_labels(graph: PrereqGraph) -> List[str]:
    """Retorna todos los códigos de cursos ordenados alfabéticamente.

    Args:
        graph: Grafo con los cursos.

    Returns:
        Lista de códigos ordenados.
    """
    return sorted(graph.courses.keys())


def course_select_options(graph: PrereqGraph) -> Dict[str, str]:
    """Genera un mapeo código → etiqueta para usar en ``st.selectbox``.

    Uso típico::

        opts = course_select_options(graph)
        chosen = st.selectbox("Curso", options=list(opts.keys()),
                              format_func=lambda k: opts.get(k, k))

    Args:
        graph: Grafo con los cursos.

    Returns:
        Diccionario ``{codigo: "CODIGO — Nombre"}``.
    """
    return {
        code: course_label(code, graph)
        for code in sorted(graph.courses.keys())
    }
