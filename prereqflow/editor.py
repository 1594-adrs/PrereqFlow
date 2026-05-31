"""Editor interactivo de cursos y dependencias para PrereqFlow.

Proporciona formularios y componentes de Streamlit que permiten al
usuario modificar en tiempo real el grafo de prerrequisitos: agregar
y eliminar cursos, editar sus propiedades, y gestionar las relaciones
de prerrequisito y corequisito directamente desde la interfaz web.
"""

from typing import Dict, List, Optional, Set

import streamlit as st

from .graph import PrereqGraph
from .models import Course
from .utils import course_label, course_select_options


def render_course_editor(graph: PrereqGraph) -> None:
    """Renderiza el panel completo de edición interactiva de cursos.

    Muestra un formulario para agregar nuevos cursos, una interfaz
    para editar cursos existentes y controles para eliminar cursos
    o relaciones del grafo.

    Todas las modificaciones se aplican directamente sobre el objeto
    ``graph`` en memoria, lo que permite ver los cambios reflejados
    de inmediato en la visualización y el planificador.

    Args:
        graph: Grafo de prerrequisitos a editar en caliente.
    """
    st.markdown("### Agregar nuevo curso")
    with st.form(key="add_course_form", clear_on_submit=True):
        cols = st.columns([2, 3, 1, 1])
        new_code = cols[0].text_input("Código", placeholder="Ej: SIS099").strip().upper()
        new_name = cols[1].text_input("Nombre", placeholder="Nombre de la asignatura").strip()
        new_credits = cols[2].number_input("Créditos", min_value=1, max_value=12, value=3, step=1)
        new_semester = cols[3].number_input("Semestre sugerido", min_value=1, max_value=14, value=1, step=1)
        cols2 = st.columns([2, 2, 1])
        new_area = cols2[0].selectbox(
            "Área académica",
            ["", "Computación", "Matemáticas", "Física", "Humanidades", "Gestión",
             "Electrónica", "Ingeniería de Software", "Redes y Comunicaciones",
             "Sistemas", "Proyecto", "Formación Básica", "Comunicación",
             "Estadística", "Diseño", "Derecho", "Tecnologías", "Auditoría", "Gerencia"],
        )
        new_offered = cols2[1].multiselect("Semestres ofrecidos", [1, 2], default=[1, 2])
        submitted = st.form_submit_button("Agregar curso", type="primary", use_container_width=True)

        if submitted:
            _add_course_to_graph(
                graph, new_code, new_name, new_credits,
                new_semester if new_semester else None,
                new_area if new_area else None,
                new_offered if new_offered else None,
            )

    st.markdown("### Editar curso existente")
    _opts = course_select_options(graph)
    edit_code = st.selectbox(
        "Seleccionar curso a editar",
        options=list(_opts.keys()),
        format_func=lambda k: _opts.get(k, k),
        key="edit_course_select",
    )
    if edit_code and edit_code in graph.courses:
        _render_edit_course_form(graph, edit_code)

    st.markdown("### Eliminar curso o relación")
    with st.expander("Controles de eliminación"):
        _opts_del = course_select_options(graph)
        del_code = st.selectbox(
            "Curso a eliminar",
            options=list(_opts_del.keys()),
            format_func=lambda k: _opts_del.get(k, k),
            key="del_course_select",
        )
        if st.button(f"Eliminar {del_code}", type="secondary", use_container_width=True):
            if del_code and del_code in graph.courses:
                graph.remove_course(del_code)
                st.success(f"Curso {del_code} eliminado.")
                st.rerun()

        st.markdown("#### Eliminar prerrequisito")
        _opts_dp = course_select_options(graph)
        del_prereq_course = st.selectbox(
            "Curso dependiente", options=list(_opts_dp.keys()),
            format_func=lambda k: _opts_dp.get(k, k), key="del_prereq_course"
        )
        if del_prereq_course and del_prereq_course in graph.courses:
            prereqs = graph.get_prerequisites(del_prereq_course)
            if prereqs:
                _opts_dpt = course_select_options(graph)
                del_prereq_target = st.selectbox(
                    "Prerrequisito a eliminar", options=sorted(prereqs),
                    format_func=lambda k: _opts_dpt.get(k, k), key="del_prereq_target"
                )
                if st.button("Eliminar prerrequisito", use_container_width=True):
                    graph.remove_prerequisite(del_prereq_course, del_prereq_target)
                    st.success(f"Prerrequisito {del_prereq_target} → {del_prereq_course} eliminado.")
                    st.rerun()
            else:
                st.info("Este curso no tiene prerrequisitos.")

        st.markdown("#### Eliminar corequisito")
        _opts_dco = course_select_options(graph)
        del_co_course = st.selectbox(
            "Curso con corequisito", options=list(_opts_dco.keys()),
            format_func=lambda k: _opts_dco.get(k, k), key="del_co_course"
        )
        if del_co_course and del_co_course in graph.courses:
            co_reqs = graph.get_co_requisites(del_co_course)
            if co_reqs:
                _opts_dcot = course_select_options(graph)
                del_co_target = st.selectbox(
                    "Corequisito a eliminar", options=sorted(co_reqs),
                    format_func=lambda k: _opts_dcot.get(k, k), key="del_co_target"
                )
                if st.button("Eliminar corequisito", use_container_width=True):
                    graph.remove_co_requisite(del_co_course, del_co_target)
                    st.success(f"Corequisito {del_co_course} ↔ {del_co_target} eliminado.")
                    st.rerun()
            else:
                st.info("Este curso no tiene corequisitos.")


def _add_course_to_graph(
    graph: PrereqGraph,
    code: str,
    name: str,
    credits: int,
    semester: Optional[int],
    area: Optional[str],
    semester_offered: Optional[List[int]],
) -> None:
    """Valida y agrega un nuevo curso al grafo.

    Args:
        graph: Grafo destino.
        code: Código del curso.
        name: Nombre del curso.
        credits: Créditos.
        semester: Semestre sugerido.
        area: Área académica.
        semester_offered: Semestres en que se ofrece.
    """
    if not code:
        st.error("El código del curso no puede estar vacío.")
        return
    if not name:
        st.error("El nombre del curso no puede estar vacío.")
        return
    if code in graph.courses:
        st.error(f"El curso {code} ya existe en el grafo.")
        return

    course = Course(
        code=code,
        name=name,
        credits=credits,
        semester=semester,
        area=area,
        semester_offered=semester_offered,
    )
    graph.add_course(course)
    st.success(f"Curso {code} — {name} agregado correctamente.")
    st.rerun()


def _render_edit_course_form(graph: PrereqGraph, code: str) -> None:
    """Renderiza el formulario de edición para un curso existente.

    Permite modificar nombre, créditos, semestre sugerido, área,
    semestres de oferta y tipo (obligatoria/electiva). Los botones
    para agregar prerrequisitos y corequisitos se colocan fuera del
    formulario mediante popovers para evitar conflictos de botones
    dentro del mismo formulario.

    Args:
        graph: Grafo que contiene el curso.
        code: Código del curso a editar.
    """
    course = graph.courses[code]
    _opts_form = course_select_options(graph)
    with st.form(key=f"edit_course_{code}", clear_on_submit=False):
        new_name = st.text_input("Nombre", value=course.name)
        new_credits = st.number_input("Créditos", min_value=1, max_value=12, value=course.credits, step=1)
        new_semester = st.number_input(
            "Semestre sugerido", min_value=1, max_value=14,
            value=course.semester or 1, step=1,
        )
        new_area = st.text_input("Área académica", value=course.area or "")
        new_offered = st.multiselect(
            "Semestres ofrecidos", [1, 2],
            default=course.semester_offered or [1, 2],
        )
        new_required = st.checkbox("Obligatoria", value=course.required)
        new_elective_group = st.text_input(
            "Grupo electivo (dejar vacío si no aplica)",
            value=course.elective_group or "",
        )
        new_min_credits = st.number_input(
            "Créditos mínimos requeridos",
            min_value=0, max_value=300,
            value=course.min_completed_credits or 0,
            step=5,
        )

        cols = st.columns([1, 1])
        with cols[0]:
            prereq_labels = ", ".join(_opts_form.get(p, p) for p in sorted(graph.get_prerequisites(code))) or "Ninguno"
            st.markdown(f"**Prerrequisitos actuales:** {prereq_labels}")
        with cols[1]:
            co_labels = ", ".join(_opts_form.get(c, c) for c in sorted(graph.get_co_requisites(code))) or "Ninguno"
            st.markdown(f"**Corequisitos actuales:** {co_labels}")

        save = st.form_submit_button("Guardar cambios", type="primary", use_container_width=True)

        if save:
            course.name = new_name
            course.credits = new_credits
            course.semester = new_semester if new_semester else None
            course.area = new_area if new_area else None
            course.semester_offered = list(new_offered) if new_offered else None
            course.required = new_required
            course.elective_group = new_elective_group if new_elective_group else None
            course.min_completed_credits = new_min_credits if new_min_credits > 0 else None
            st.success(f"Curso {code} actualizado.")
            st.rerun()

    col_buttons = st.columns([1, 1])
    with col_buttons[0]:
        with st.popover("Agregar prerrequisito", use_container_width=True):
            _render_add_prerequisite_dialog(graph, code)
    with col_buttons[1]:
        with st.popover("Agregar corequisito", use_container_width=True):
            _render_add_co_requisite_dialog(graph, code)


def _render_add_prerequisite_dialog(graph: PrereqGraph, course_code: str) -> None:
    """Muestra un diálogo para agregar un prerrequisito a un curso.

    Args:
        graph: Grafo de prerrequisitos.
        course_code: Código del curso que recibirá el prerrequisito.
    """
    existing = graph.get_prerequisites(course_code)
    _opts_prereq = course_select_options(graph)
    candidates = sorted(
        c for c in graph.courses
        if c != course_code and c not in existing
    )
    if not candidates:
        st.info("No hay cursos disponibles para agregar como prerrequisito.")
        return

    prereq_code = st.selectbox(
        "Seleccionar prerrequisito",
        options=candidates,
        format_func=lambda k: _opts_prereq.get(k, k),
        key=f"add_prereq_{course_code}",
    )
    if st.button("Confirmar prerrequisito", key=f"confirm_prereq_{course_code}"):
        try:
            graph.add_prerequisite(course_code, prereq_code)
            st.success(f"Prerrequisito {course_label(prereq_code, graph)} → {course_code} agregado.")
            st.rerun()
        except (ValueError, KeyError) as exc:
            st.error(str(exc))


def _render_add_co_requisite_dialog(graph: PrereqGraph, course_code: str) -> None:
    """Muestra un diálogo para agregar un corequisito a un curso.

    Args:
        graph: Grafo de prerrequisitos.
        course_code: Código del curso que recibirá el corequisito.
    """
    existing = graph.get_co_requisites(course_code)
    _opts_co = course_select_options(graph)
    candidates = sorted(
        c for c in graph.courses
        if c != course_code and c not in existing
    )
    if not candidates:
        st.info("No hay cursos disponibles para agregar como corequisito.")
        return

    co_code = st.selectbox(
        "Seleccionar corequisito",
        options=candidates,
        format_func=lambda k: _opts_co.get(k, k),
        key=f"add_co_{course_code}",
    )
    if st.button("Confirmar corequisito", key=f"confirm_co_{course_code}"):
        try:
            graph.add_co_requisite(course_code, co_code)
            st.success(f"Corequisito {course_code} ↔ {course_label(co_code, graph)} agregado.")
            st.rerun()
        except (ValueError, KeyError) as exc:
            st.error(str(exc))
