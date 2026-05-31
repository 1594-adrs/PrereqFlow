"""Punto de entrada de la aplicación PrereqFlow.

Define la interfaz de usuario con Streamlit, integrando cuatro modos
de operación (Planificador, Editor, Carga de Archivos y Seguimiento)
que se cargan dinámicamente desde ``prereqflow/modes/``.

Incluye el currículo de ejemplo de Ingeniería de Sistemas de la UTP
con 64 asignaturas distribuidas en 10 semestres.
"""

from pathlib import Path

import streamlit as st

from prereqflow.graph import PrereqGraph
from prereqflow.io import load_graph_from_json, save_graph_to_json
from prereqflow.models import Course
from prereqflow.modes.planner_ui import render_planner_mode
from prereqflow.modes.editor_ui import render_editor_mode
from prereqflow.modes.uploader_ui import render_uploader_mode
from prereqflow.modes.tracker_ui import render_tracker_mode

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
    ("SIS005", "SIS007"), ("SIS005", "SIS004"),
    ("SIS013", "SIS005"), ("SIS030", "SIS013"),
    ("SIS040", "SIS030"), ("SIS046", "SIS040"),
    ("SIS058", "SIS046"), ("SIS064", "SIS058"),
    ("SIS009", "SIS004"), ("SIS015", "SIS009"),
    ("SIS020", "SIS015"), ("SIS016", "SIS011"),
    ("SIS022", "SIS016"), ("SIS017", "SIS012"),
    ("SIS023", "SIS017"), ("SIS018", "SIS005"),
    ("SIS030", "SIS018"), ("SIS043", "SIS018"),
    ("SIS043", "SIS019"), ("SIS048", "SIS033"),
    ("SIS048", "SIS042"), ("SIS035", "SIS013"),
    ("SIS059", "SIS035"), ("SIS061", "SIS049"),
    ("SIS044", "SIS026"), ("SIS063", "SIS044"),
    ("SIS031", "SIS036"), ("SIS038", "SIS027"),
    ("SIS055", "SIS035"), ("SIS045", "SIS034"),
    ("SIS051", "SIS050"), ("SIS052", "SIS046"),
    ("SIS055", "SIS042"), ("SIS064", "SIS063"),
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
    "SIS001": "Formación Básica", "SIS002": "Humanidades",
    "SIS003": "Formación Básica", "SIS004": "Matemáticas",
    "SIS005": "Computación", "SIS006": "Comunicación",
    "SIS007": "Computación", "SIS008": "Formación Básica",
    "SIS009": "Matemáticas", "SIS010": "Matemáticas",
    "SIS011": "Física", "SIS012": "Física",
    "SIS013": "Computación", "SIS014": "Humanidades",
    "SIS015": "Matemáticas", "SIS016": "Física",
    "SIS017": "Física", "SIS018": "Computación",
    "SIS019": "Computación", "SIS020": "Matemáticas",
    "SIS021": "Matemáticas", "SIS022": "Física",
    "SIS023": "Física", "SIS024": "Computación",
    "SIS025": "Ingeniería", "SIS026": "Gestión",
    "SIS027": "Matemáticas", "SIS028": "Electrónica",
    "SIS029": "Electrónica", "SIS030": "Computación",
    "SIS031": "Gestión", "SIS032": "Gestión",
    "SIS033": "Computación", "SIS034": "Electrónica",
    "SIS035": "Computación", "SIS036": "Gestión",
    "SIS037": "Gestión", "SIS038": "Estadística",
    "SIS039": "Diseño", "SIS040": "Ingeniería de Software",
    "SIS041": "Redes y Comunicaciones", "SIS042": "Sistemas",
    "SIS043": "Computación", "SIS044": "Gestión",
    "SIS045": "Electrónica", "SIS046": "Ingeniería de Software",
    "SIS047": "Redes y Comunicaciones", "SIS048": "Sistemas",
    "SIS049": "Derecho y Ética", "SIS050": "Electrónica",
    "SIS051": "Electrónica", "SIS052": "Ingeniería de Software",
    "SIS053": "Tecnologías", "SIS054": "Redes y Comunicaciones",
    "SIS055": "Computación", "SIS056": "Gestión",
    "SIS057": "Computación", "SIS058": "Proyecto",
    "SIS059": "Gestión", "SIS060": "Auditoría",
    "SIS061": "Derecho", "SIS062": "Gerencia",
    "SIS063": "Gestión", "SIS064": "Proyecto",
}

COURSE_MIN_CREDITS = {"SIS058": 120, "SIS064": 140}
COURSE_OFFERINGS = {"SIS058": [1, 2], "SIS064": [1, 2]}

CO_REQUISITES = {
    "SIS011": {"SIS012"}, "SIS012": {"SIS011"},
    "SIS016": {"SIS017"}, "SIS017": {"SIS016"},
    "SIS022": {"SIS023"}, "SIS023": {"SIS022"},
    "SIS028": {"SIS029"}, "SIS029": {"SIS028"},
    "SIS034": {"SIS045"}, "SIS045": {"SIS034"},
    "SIS050": {"SIS051"}, "SIS051": {"SIS050"},
    "SIS046": {"SIS052"}, "SIS052": {"SIS046"},
}

ELECTIVE_GROUPS = {"SIS053": "Tecnologías Emergentes"}
ELECTIVE_COURSES = {"SIS053"}



def load_data_graph() -> PrereqGraph:
    """Carga el grafo desde el archivo JSON o retorna el de ejemplo."""
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    if DATA_FILE.exists():
        try:
            return load_graph_from_json(str(DATA_FILE))
        except Exception:
            return build_sample_graph()
    return build_sample_graph()


def build_sample_graph() -> PrereqGraph:
    """Construye el grafo de ejemplo con el currículo UTP."""
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


def main() -> None:
    """Punto de entrada principal de la aplicación Streamlit."""
    st.set_page_config(page_title=f"PrereqFlow - {PROGRAM_NAME}", layout="wide")

    if "graph" not in st.session_state:
        st.session_state.graph = load_data_graph()
    if "data_source" not in st.session_state:
        st.session_state.data_source = "Currículo de ejemplo integrado"

    st.sidebar.title("PrereqFlow")
    st.sidebar.subheader(PROGRAM_NAME)

    app_mode = st.sidebar.radio(
        "Modo de la aplicación",
        ["Planificador", "Editor de cursos", "Cargar archivo", "Seguimiento"],
        index=0,
    )

    if app_mode == "📂 Cargar archivo":
        render_uploader_mode()
        return

    graph = st.session_state.graph

    if app_mode == "Planificador":
        render_planner_mode(graph, st.session_state.data_source, PROGRAM_NAME)
    elif app_mode == "Editor de cursos":
        render_editor_mode(graph, DATA_FILE)
    elif app_mode == "Seguimiento":
        render_tracker_mode(graph)


if __name__ == "__main__":
    main()
