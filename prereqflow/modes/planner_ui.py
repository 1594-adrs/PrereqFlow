"""Modo Planificador — interfaz de generación y visualización del plan de estudios.

Proporciona la interfaz de Streamlit para configurar parámetros,
visualizar el grafo de prerrequisitos, generar el plan semestral
y consultar información detallada de cada asignatura.
"""

from typing import List

import streamlit as st
from streamlit.components.v1 import html

from ..graph import PrereqGraph
from ..models import Course
from ..planner import generate_study_plan
from ..utils import course_label, course_select_options
from ..visualization import render_graph


def show_plan(plan: List[List[Course]]) -> None:
    """Muestra el plan de estudios generado en la interfaz."""
    for index, semester_courses in enumerate(plan, start=1):
        st.subheader(f"Semestre {index}")
        for course in semester_courses:
            st.markdown(
                f"**{course.code}**: {course.name} ({course.credits} créditos) — "
                f"Área: {course.area or 'N/A'} — Semestre sugerido: {course.semester or 'N/A'}"
            )


def render_course_info(graph: PrereqGraph, selected_course: str) -> None:
    """Muestra información detallada de una asignatura seleccionada."""
    if not selected_course or selected_course not in graph.courses:
        return
    selected = graph.courses[selected_course]
    prereqs = graph.get_prerequisites(selected_course)
    co_reqs = graph.get_co_requisites(selected_course)
    dependents = graph.get_dependents(selected_course)
    _opts_info = course_select_options(graph)
    st.write(f"**Área:** {selected.area or 'N/A'}")
    st.write(f"**Semestre sugerido:** {selected.semester or 'N/A'}")
    if selected.semester_offered is not None:
        st.write(f"**Semestres ofrecidos:** {', '.join(str(s) for s in selected.semester_offered)}")
    if selected.min_completed_credits is not None:
        st.write(f"**Requisito de créditos aprobados:** {selected.min_completed_credits}")
    if selected.elective_group:
        st.write(f"**Grupo electivo:** {selected.elective_group}")
    if not selected.required:
        st.write("**Tipo:** Electiva")
    st.write(f"**Prerrequisitos:** {', '.join(_opts_info.get(p, p) for p in sorted(prereqs)) or 'Ninguno'}")
    st.write(f"**Corequisitos:** {', '.join(_opts_info.get(c, c) for c in sorted(co_reqs)) or 'Ninguno'}")
    st.write(f"**Dependientes:** {', '.join(_opts_info.get(d, d) for d in sorted(dependents)) or 'Ninguno'}")


def render_planner_mode(
    graph: PrereqGraph,
    data_source: str,
    program_name: str,
) -> None:
    """Renderiza el modo Planificador completo.

    Args:
        graph: Grafo de prerrequisitos del programa.
        data_source: Nombre descriptivo de la fuente de datos.
        program_name: Nombre del programa académico.
    """
    st.title("PrereqFlow")
    st.subheader(program_name)
    st.markdown(
        "Planificador interactivo de asignaturas basado en grafos dirigidos. "
        f"**Fuente actual:** {data_source}. "
        f"**Cursos:** {len(graph.courses)}."
    )

    st.sidebar.header("Configuración del plan")
    max_credits = st.sidebar.slider("Créditos máximos por semestre", 9, 24, 18, 1)
    max_semesters = st.sidebar.slider("Máximo semestres", 6, 14, 12, 1)
    plan_type = st.sidebar.selectbox(
        "Tipo de plan", ["Balanceado", "Rápido", "Bajo riesgo"], index=0,
    )
    _opts_sidebar = course_select_options(graph)
    completed_courses = st.sidebar.multiselect(
        "Cursos ya cursados", options=list(_opts_sidebar.keys()),
        format_func=lambda k: _opts_sidebar.get(k, k), default=[],
    )
    show_dependencies = st.sidebar.checkbox("Mostrar grafo de prerrequisitos", value=True)
    selected_course = st.sidebar.selectbox(
        "Seleccionar materia", options=list(_opts_sidebar.keys()),
        format_func=lambda k: _opts_sidebar.get(k, k),
    )

    has_cycle = graph.detect_cycle()
    if has_cycle:
        st.sidebar.error("🔴 El grafo contiene ciclos")
    else:
        st.sidebar.success("🟢 Grafo acíclico — planificación disponible")

    if show_dependencies:
        st.markdown("## Grafo de prerrequisitos")
        graph_html = render_graph(graph)
        html(graph_html, height=700)

    completed_credits = sum(
        graph.courses[code].credits
        for code in completed_courses if code in graph.courses
    )
    st.sidebar.markdown(f"**Créditos aprobados:** {completed_credits}")
    eligible = graph.eligible_courses(set(completed_courses), semester=1, completed_credits=completed_credits)
    st.sidebar.markdown(f"**Cursos elegibles:** {len(eligible)}")
    if eligible:
        st.sidebar.write(", ".join(course_label(c.code, graph) for c in eligible[:10]) + (" ..." if len(eligible) > 10 else ""))

    st.markdown("## Plan de estudio generado")
    try:
        plan = generate_study_plan(
            graph,
            max_credits=max_credits,
            max_semesters=max_semesters,
            plan_type={"Balanceado": "balanced", "Rápido": "fast", "Bajo riesgo": "low_risk"}[plan_type],
            completed=completed_courses,
        )
        show_plan(plan)
        total_credits = sum(c.credits for sem in plan for c in sem)
        st.info(f"Plan completo en {len(plan)} semestres con {total_credits} créditos planificados.")
    except ValueError as exc:
        st.error(str(exc))

    st.markdown("---")
    st.markdown("### Información de la materia seleccionada")
    if selected_course:
        render_course_info(graph, selected_course)

    st.markdown("---")
    st.markdown("### Cursos del programa")
    _opts_list = course_select_options(graph)
    for course in sorted(graph.courses.values(), key=lambda c: c.code):
        prereqs = graph.get_prerequisites(course.code)
        prereq_labels = ", ".join(_opts_list.get(p, p) for p in sorted(prereqs)) or "Ninguno"
        st.write(f"**{course.code}** {course.name} — prereqs: {prereq_labels}")
