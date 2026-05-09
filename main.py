from pathlib import Path

import streamlit as st
from streamlit.components.v1 import html

from prereqflow.graph import PrereqGraph
from prereqflow.io import load_graph_from_json, save_graph_to_json
from prereqflow.models import Course
from prereqflow.planner import generate_study_plan
from prereqflow.visualization import render_graph

PROGRAM_NAME = "UTP Ingeniería de Sistemas y Computación"
DATA_FILE = Path("data/utp_sistemas.json")

SAMPLE_COURSES = [
    Course(code="SIS001", name="Ingeniería de Sistemas y Computación", credits=2),
    Course(code="SIS002", name="Humanidades I", credits=1),
    Course(code="SIS003", name="Deportes I", credits=5),
    Course(code="SIS004", name="Matemáticas I", credits=5),
    Course(code="SIS005", name="Programación I", credits=2),
    Course(code="SIS006", name="Técnicas de la comunicación oral y escrita", credits=3),
    Course(code="SIS007", name="Introducción a la Informática", credits=1),
    Course(code="SIS008", name="Deportes II", credits=5),
    Course(code="SIS009", name="Matemáticas II", credits=3),
    Course(code="SIS010", name="Álgebra Lineal", credits=4),
    Course(code="SIS011", name="Física I", credits=2),
    Course(code="SIS012", name="Laboratorio de Física I", credits=4),
    Course(code="SIS013", name="Programación II", credits=2),
    Course(code="SIS014", name="Humanidades II", credits=4),
    Course(code="SIS015", name="Matemáticas III", credits=4),
    Course(code="SIS016", name="Física II", credits=2),
    Course(code="SIS017", name="Laboratorio de Física II", credits=4),
    Course(code="SIS018", name="Estructura de Datos", credits=3),
    Course(code="SIS019", name="Lógica", credits=3),
    Course(code="SIS020", name="Matemáticas IV", credits=3),
    Course(code="SIS021", name="Métodos Numéricos", credits=4),
    Course(code="SIS022", name="Física III", credits=2),
    Course(code="SIS023", name="Laboratorio de Física III", credits=4),
    Course(code="SIS024", name="Estructura de lenguajes", credits=3),
    Course(code="SIS025", name="Teoría de sistemas", credits=3),
    Course(code="SIS026", name="Administración de empresas", credits=2),
    Course(code="SIS027", name="Estadística", credits=3),
    Course(code="SIS028", name="Electrónica I", credits=2),
    Course(code="SIS029", name="Laboratorio de Electrónica I", credits=3),
    Course(code="SIS030", name="Programación orientada a objetos", credits=3),
    Course(code="SIS031", name="Sistemas contables", credits=3),
    Course(code="SIS032", name="Teoría económica", credits=4),
    Course(code="SIS033", name="Arquitectura de Computadores", credits=4),
    Course(code="SIS034", name="Electrónica II", credits=3),
    Course(code="SIS035", name="Base de Datos I", credits=3),
    Course(code="SIS036", name="Contabilidad de costos", credits=3),
    Course(code="SIS037", name="Investigación de Operaciones", credits=2),
    Course(code="SIS038", name="Estadística Especial", credits=2),
    Course(code="SIS039", name="Dibujo", credits=4),
    Course(code="SIS040", name="Ingeniería de Software I", credits=3),
    Course(code="SIS041", name="Comunicaciones I", credits=4),
    Course(code="SIS042", name="Sistemas Operativos I", credits=4),
    Course(code="SIS043", name="Compiladores", credits=3),
    Course(code="SIS044", name="Finanzas", credits=2),
    Course(code="SIS045", name="Laboratorio de Electrónica II", credits=3),
    Course(code="SIS046", name="Ingeniería de Software II", credits=3),
    Course(code="SIS047", name="Comunicaciones II", credits=2),
    Course(code="SIS048", name="Sistemas Distribuidos", credits=3),
    Course(code="SIS049", name="Legislación, ética y Contratación", credits=1),
    Course(code="SIS050", name="Microcontroladores y Control de procesos en tiempo real", credits=3),
    Course(code="SIS051", name="Laboratorio de microcontroladores y Control de procesos en tiempo real", credits=3),
    Course(code="SIS052", name="Laboratorio de Software", credits=3),
    Course(code="SIS053", name="Nuevas tecnologías informáticas", credits=4),
    Course(code="SIS054", name="Comunicaciones III", credits=3),
    Course(code="SIS055", name="Arquitectura Cliente/Servidor", credits=3),
    Course(code="SIS056", name="Gerencia Institucional", credits=2),
    Course(code="SIS057", name="Sistemas Expertos", credits=3),
    Course(code="SIS058", name="Proyecto de Grado I", credits=3),
    Course(code="SIS059", name="Administración de Información", credits=1),
    Course(code="SIS060", name="Auditoría de Sistemas", credits=2),
    Course(code="SIS061", name="Constitución Política", credits=3),
    Course(code="SIS062", name="Planeación estratégica de Sistemas", credits=6),
    Course(code="SIS063", name="Gerencia de proyectos", credits=3),
    Course(code="SIS064", name="Proyecto de Grado II", credits=3),
]

SAMPLE_PREREQUISITES = [
    ("SIS005", "SIS007"),
    ("SIS005", "SIS004"),
    ("SIS013", "SIS005"),
    ("SIS030", "SIS013"),
    ("SIS040", "SIS030"),
    ("SIS046", "SIS040"),
    ("SIS058", "SIS046"),
    ("SIS064", "SIS058"),
    ("SIS009", "SIS004"),
    ("SIS015", "SIS009"),
    ("SIS020", "SIS015"),
    ("SIS016", "SIS011"),
    ("SIS022", "SIS016"),
    ("SIS017", "SIS012"),
    ("SIS023", "SIS017"),
    ("SIS018", "SIS005"),
    ("SIS030", "SIS018"),
    ("SIS043", "SIS018"),
    ("SIS043", "SIS019"),
    ("SIS048", "SIS033"),
    ("SIS048", "SIS042"),
    ("SIS035", "SIS013"),
    ("SIS059", "SIS035"),
    ("SIS061", "SIS049"),
    ("SIS044", "SIS026"),
    ("SIS063", "SIS044"),
    ("SIS031", "SIS036"),
    ("SIS038", "SIS027"),
    ("SIS055", "SIS035"),
    ("SIS045", "SIS034"),
    ("SIS051", "SIS050"),
    ("SIS052", "SIS046"),
    ("SIS055", "SIS042"),
    ("SIS064", "SIS063"),
]

SEMESTER_ASSIGNMENTS = {
    **{f"SIS{code:03d}": 1 for code in range(1, 8)},
    **{f"SIS{code:03d}": 2 for code in range(8, 15)},
    **{f"SIS{code:03d}": 3 for code in range(15, 22)},
    **{f"SIS{code:03d}": 4 for code in range(22, 29)},
    **{f"SIS{code:03d}": 5 for code in range(29, 36)},
    **{f"SIS{code:03d}": 6 for code in range(36, 43)},
    **{f"SIS{code:03d}": 7 for code in range(43, 50)},
    **{f"SIS{code:03d}": 8 for code in range(50, 57)},
    **{f"SIS{code:03d}": 9 for code in range(57, 64)},
    "SIS064": 10,
}

AREA_ASSIGNMENTS = {
    "SIS001": "Formación Básica",
    "SIS002": "Humanidades",
    "SIS003": "Formación Básica",
    "SIS004": "Matemáticas",
    "SIS005": "Computación",
    "SIS006": "Comunicación",
    "SIS007": "Computación",
    "SIS008": "Formación Básica",
    "SIS009": "Matemáticas",
    "SIS010": "Matemáticas",
    "SIS011": "Física",
    "SIS012": "Física",
    "SIS013": "Computación",
    "SIS014": "Humanidades",
    "SIS015": "Matemáticas",
    "SIS016": "Física",
    "SIS017": "Física",
    "SIS018": "Computación",
    "SIS019": "Computación",
    "SIS020": "Matemáticas",
    "SIS021": "Matemáticas",
    "SIS022": "Física",
    "SIS023": "Física",
    "SIS024": "Computación",
    "SIS025": "Ingeniería",
    "SIS026": "Gestión",
    "SIS027": "Matemáticas",
    "SIS028": "Electrónica",
    "SIS029": "Electrónica",
    "SIS030": "Computación",
    "SIS031": "Gestión",
    "SIS032": "Gestión",
    "SIS033": "Computación",
    "SIS034": "Electrónica",
    "SIS035": "Computación",
    "SIS036": "Gestión",
    "SIS037": "Gestión",
    "SIS038": "Estadística",
    "SIS039": "Diseño",
    "SIS040": "Ingeniería de Software",
    "SIS041": "Redes y Comunicaciones",
    "SIS042": "Sistemas",
    "SIS043": "Computación",
    "SIS044": "Gestión",
    "SIS045": "Electrónica",
    "SIS046": "Ingeniería de Software",
    "SIS047": "Redes y Comunicaciones",
    "SIS048": "Sistemas",
    "SIS049": "Derecho y Ética",
    "SIS050": "Electrónica",
    "SIS051": "Electrónica",
    "SIS052": "Ingeniería de Software",
    "SIS053": "Tecnologías",
    "SIS054": "Redes y Comunicaciones",
    "SIS055": "Computación",
    "SIS056": "Gestión",
    "SIS057": "Computación",
    "SIS058": "Proyecto",
    "SIS059": "Gestión",
    "SIS060": "Auditoría",
    "SIS061": "Derecho",
    "SIS062": "Gerencia",
    "SIS063": "Gestión",
    "SIS064": "Proyecto",
}

COURSE_MIN_CREDITS = {
    "SIS058": 120,
    "SIS064": 140,
}

COURSE_OFFERINGS = {
    "SIS058": [1, 2],
    "SIS064": [1, 2],
}

CO_REQUISITES = {
    "SIS011": {"SIS012"},
    "SIS012": {"SIS011"},
    "SIS016": {"SIS017"},
    "SIS017": {"SIS016"},
    "SIS022": {"SIS023"},
    "SIS023": {"SIS022"},
    "SIS028": {"SIS029"},
    "SIS029": {"SIS028"},
    "SIS034": {"SIS045"},
    "SIS045": {"SIS034"},
    "SIS050": {"SIS051"},
    "SIS051": {"SIS050"},
    "SIS046": {"SIS052"},
    "SIS052": {"SIS046"},
}

ELECTIVE_GROUPS = {
    "SIS053": "Tecnologías Emergentes",
}

ELECTIVE_COURSES = {"SIS053"}


def ensure_data_file() -> None:
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    if not DATA_FILE.exists():
        save_graph_to_json(build_sample_graph(), str(DATA_FILE))


def load_data_graph() -> PrereqGraph:
    if DATA_FILE.exists():
        try:
            return load_graph_from_json(str(DATA_FILE))
        except Exception:
            return build_sample_graph()
    return build_sample_graph()


def build_sample_graph() -> PrereqGraph:
    graph = PrereqGraph()
    for course in SAMPLE_COURSES:
        if course.code in SEMESTER_ASSIGNMENTS:
            course.semester = SEMESTER_ASSIGNMENTS[course.code]
        if course.code in AREA_ASSIGNMENTS:
            course.area = AREA_ASSIGNMENTS[course.code]
        if course.code in COURSE_MIN_CREDITS:
            course.min_completed_credits = COURSE_MIN_CREDITS[course.code]
        if course.code in COURSE_OFFERINGS:
            course.semester_offered = COURSE_OFFERINGS[course.code]
        if course.code in CO_REQUISITES:
            course.co_requisites = CO_REQUISITES[course.code]
        if course.code in ELECTIVE_GROUPS:
            course.elective_group = ELECTIVE_GROUPS[course.code]
        if course.code in ELECTIVE_COURSES:
            course.required = False
        graph.add_course(course)
    for course_code, prereq_code in SAMPLE_PREREQUISITES:
        graph.add_prerequisite(course_code, prereq_code)
    return graph


def show_plan(plan: list[list[Course]]) -> None:
    for index, semester_courses in enumerate(plan, start=1):
        st.subheader(f"Semestre {index}")
        for course in semester_courses:
            st.markdown(
                f"**{course.code}**: {course.name} ({course.credits} créditos) — "
                f"Área: {course.area or 'N/A'} — Semestre sugerido: {course.semester or 'N/A'}"
            )


def main() -> None:
    st.set_page_config(page_title=f"PrereqFlow - {PROGRAM_NAME}", layout="wide")
    st.title("PrereqFlow")
    st.subheader(PROGRAM_NAME)
    st.markdown(
        "Ejemplo de planificador de asignaturas para un programa estilo UTP Ingeniería de Sistemas. "
        "La app puede cargar los datos desde `data/utp_sistemas.json` o usar el currículo integrado de ejemplo. "
        "Si el archivo JSON no existe, se genera automáticamente a partir del currículo de ejemplo."
    )

    ensure_data_file()
    data_source = st.sidebar.selectbox(
        "Fuente de datos",
        ["Datos UTP JSON", "Currículo de ejemplo integrado"],
        index=0,
    )
    graph = load_data_graph() if data_source == "Datos UTP JSON" else build_sample_graph()
    st.sidebar.header("Configuración del plan")
    max_credits = st.sidebar.slider("Créditos máximos por semestre", min_value=9, max_value=24, value=18, step=1)
    max_semesters = st.sidebar.slider("Máximo semestres", min_value=6, max_value=14, value=12, step=1)
    plan_type = st.sidebar.selectbox(
        "Tipo de plan",
        ["Balanceado", "Rápido", "Bajo riesgo"],
        index=0,
    )
    completed_courses = st.sidebar.multiselect(
        "Cursos ya cursados",
        sorted(graph.courses),
        default=[],
    )
    show_dependencies = st.sidebar.checkbox("Mostrar grafo de prerrequisitos", value=True)
    selected_course = st.sidebar.selectbox(
        "Seleccionar materia",
        sorted(graph.courses),
    )

    if show_dependencies:
        st.markdown("## Grafo de prerrequisitos")
        graph_html = render_graph(graph)
        html(graph_html, height=700)

    completed_credits = sum(
        graph.courses[code].credits
        for code in completed_courses
        if code in graph.courses
    )
    st.sidebar.markdown(f"**Créditos aprobados hasta ahora:** {completed_credits}")
    eligible_courses = graph.eligible_courses(
        set(completed_courses), semester=1, completed_credits=completed_credits
    )
    st.sidebar.markdown(
        f"**Cursos actualmente elegibles:** {len(eligible_courses)}"
    )
    if eligible_courses:
        st.sidebar.write(
            ", ".join(f"{course.code}" for course in eligible_courses[:10])
            + (" ..." if len(eligible_courses) > 10 else "")
        )

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
        total_credits = sum(course.credits for semester in plan for course in semester)
        st.info(f"Plan completo en {len(plan)} semestres con {total_credits} créditos planificados.")
    except ValueError as exc:
        st.error(str(exc))

    st.markdown("---")
    st.markdown("### Información de la materia seleccionada")
    if selected_course:
        selected = graph.courses[selected_course]
        prereqs = graph.get_prerequisites(selected_course)
        co_reqs = graph.get_co_requisites(selected_course)
        dependents = graph.get_dependents(selected_course)
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
        st.write(f"**Prerrequisitos:** {', '.join(sorted(prereqs)) or 'Ninguno'}")
        st.write(f"**Corequisitos:** {', '.join(sorted(co_reqs)) or 'Ninguno'}")
        st.write(f"**Dependientes:** {', '.join(sorted(dependents)) or 'Ninguno'}")

    st.markdown("---")
    st.markdown("### Cursos del programa UTP")
    for course in sorted(graph.courses.values(), key=lambda course: course.code):
        prereqs = graph.get_prerequisites(course.code)
        st.write(
            f"**{course.code}** {course.name} — prereqs: {', '.join(sorted(prereqs)) or 'Ninguno'}"
        )


if __name__ == "__main__":
    main()
