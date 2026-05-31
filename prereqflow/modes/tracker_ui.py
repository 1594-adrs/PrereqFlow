"""Modo Seguimiento — interfaz de progreso académico, electivas y simulación.

Proporciona la interfaz de Streamlit para el seguimiento multi-periodo
del avance del estudiante, la selección de electivas y el simulador
what-if.
"""

import streamlit as st

from ..graph import PrereqGraph
from ..models import Course
from ..tracker import ElectiveGroup, ElectiveManager, ProgressTracker
from ..utils import course_label, course_select_options


def build_elective_manager(graph: PrereqGraph) -> ElectiveManager:
    """Construye el gestor de electivas con los grupos del currículo UTP."""
    manager = ElectiveManager()
    grupo_tecnologias = ElectiveGroup(
        name="Tecnologías Emergentes",
        description="Electivas profesionales en tecnologías de vanguardia",
        min_select=1,
        max_select=2,
        min_credits=3,
    )
    elective_groups = {"SIS053": "Tecnologías Emergentes"}
    for code, group_name in elective_groups.items():
        if group_name == "Tecnologías Emergentes":
            grupo_tecnologias.course_codes.add(code)
            if code in graph.courses:
                grupo_tecnologias.course_credits[code] = graph.courses[code].credits
    manager.add_group(grupo_tecnologias)
    return manager


def render_tracker_mode(graph: PrereqGraph) -> None:
    """Renderiza el modo Seguimiento de Progreso completo.

    Args:
        graph: Grafo de prerrequisitos del programa.
    """
    st.title("📈 Seguimiento de Progreso Académico")
    st.markdown(
        "Gestione su avance en el programa, seleccione electivas "
        "y simule diferentes rutas de planificación."
    )

    if "tracker" not in st.session_state:
        st.session_state.tracker = ProgressTracker(graph)
    if "elective_manager" not in st.session_state:
        st.session_state.elective_manager = build_elective_manager(graph)

    tracker = st.session_state.tracker
    manager = st.session_state.elective_manager

    tab1, tab2, tab3 = st.tabs(["Progreso", "Electivas", "Simulador"])

    with tab1:
        summary = tracker.get_progress_summary()
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Semestre actual", summary["semestre_actual"])
        col2.metric("Cursos aprobados", f"{summary['cursos_aprobados']}/{summary['cursos_totales']}")
        col3.metric("Créditos", f"{summary['creditos_aprobados']}/{summary['creditos_totales']}")
        col4.metric("Avance", f"{summary['porcentaje_avance']}%")

        if summary["distribucion_areas"]:
            st.markdown("**Distribución por área académica:**")
            for area, count in sorted(summary["distribucion_areas"].items()):
                st.write(f"- {area}: {count} curso(s)")

        st.markdown("### Registrar semestre completado")
        _opts_prog = course_select_options(graph)
        completed_this = st.multiselect(
            "Cursos aprobados en este semestre",
            options=list(_opts_prog.keys()),
            format_func=lambda k: _opts_prog.get(k, k),
            key="tracker_semester_courses",
        )
        if st.button("Registrar semestre", type="primary", use_container_width=True):
            if completed_this:
                try:
                    tracker.complete_semester(completed_this)
                    st.success(f"Semestre {tracker.record.current_semester} registrado.")
                    st.rerun()
                except ValueError as exc:
                    st.error(str(exc))
            else:
                st.warning("Seleccione al menos un curso.")

    with tab2:
        st.markdown("### Estado de grupos electivos")
        status = tracker.get_elective_requirements_status(manager)
        if not status:
            st.info("No hay grupos electivos configurados en este plan.")
        else:
            for group_name, state in status.items():
                _opts_el = course_select_options(graph)
                with st.expander(f"{'✅' if state['satisfecho'] else '⚠️'} {group_name}"):
                    st.write(f"*{state['descripcion']}*")
                    st.write(f"Cursos en el grupo: {', '.join(_opts_el.get(c, c) for c in state['cursos_en_grupo'])}")
                    st.write(f"Completados: {', '.join(_opts_el.get(c, c) for c in state['cursos_completados']) or 'Ninguno'}")
                    st.write(f"Selección actual: {_opts_el.get(state['seleccion_actual'], state['seleccion_actual']) if state['seleccion_actual'] else 'Ninguna'}")
                    if state["min_select"]:
                        st.write(f"Mínimo requerido: {state['min_select']} curso(s)")
                    if state["errores"]:
                        for err in state["errores"]:
                            st.error(err)

        available = manager.get_available_electives(graph, tracker.get_completed_courses())
        if available:
            st.markdown("### Seleccionar electiva disponible")
            for group_name, courses in available.items():
                opts = {c.code: f"{c.code} — {c.name} ({c.credits} cr)" for c in courses}
                chosen = st.selectbox(
                    f"Elegir del grupo '{group_name}'",
                    options=list(opts.keys()),
                    format_func=lambda k: opts.get(k, k),
                    key=f"elective_select_{group_name}",
                )
                if st.button(f"Seleccionar {chosen}", key=f"elective_btn_{group_name}"):
                    errors = tracker.select_elective(group_name, chosen, manager)
                    if errors:
                        for err in errors:
                            st.error(err)
                    else:
                        st.success(f"Electiva {chosen} seleccionada.")
                        st.rerun()

    with tab3:
        st.markdown("### Simulador what-if")
        _opts_sim = course_select_options(graph)
        sim_courses = st.multiselect(
            "Cursos a simular como aprobados",
            options=list(_opts_sim.keys()),
            format_func=lambda k: _opts_sim.get(k, k),
            key="sim_courses",
        )
        sim_semester = st.number_input("Semestre de simulación", min_value=1, max_value=14, value=tracker.record.current_semester + 1, step=1)
        if st.button("Simular", use_container_width=True):
            if sim_courses:
                result = tracker.simulate_semester(sim_courses, sim_semester)
                st.info(
                    f"📊 **Simulación:** {result['nuevos_aprobados']} → "
                    f"{result['creditos_simulados']} créditos, "
                    f"{result['cursos_aprobados_simulados']} cursos aprobados. "
                    f"Cursos elegibles: {len(result['cursos_elegibles'])}"
                )
                if result["cursos_elegibles"]:
                    st.write("**Cursos elegibles tras la simulación:**")
                    cols = st.columns(3)
                    for i, code in enumerate(result["cursos_elegibles"][:12]):
                        cols[i % 3].write(f"- {course_label(code, graph)}")
            else:
                st.warning("Seleccione al menos un curso para simular.")
