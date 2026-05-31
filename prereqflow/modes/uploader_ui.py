"""Modo Carga de Archivos — interfaz Drag & Drop para datos curriculares.

Proporciona el envoltorio de Streamlit que integra el cargador
de archivos y gestiona el flujo de reemplazo del grafo en sesión.
"""

import streamlit as st

from ..graph import PrereqGraph
from ..uploader import render_file_uploader

JSON_FORMAT_EXAMPLE = r"""
{
  "courses": [
    {
      "code": "SIS001",
      "name": "Matemáticas I",
      "credits": 4,
      "semester": 1,
      "area": "Matemáticas",
      "required": true
    }
  ],
  "prerequisites": [
    { "course": "SIS005", "prereq": "SIS004" }
  ],
  "co_requisites": [
    { "course": "SIS011", "co_req": "SIS012" }
  ]
}
"""


def render_uploader_mode() -> None:
    """Renderiza el modo Carga de Archivo completo.

    Muestra el área de Drag & Drop con instrucciones de formato,
    y si se carga un archivo válido, actualiza el grafo en
    session_state y limpia el tracker previo.
    """
    st.title("📂 Cargar archivo curricular")
    st.markdown(
        "Arrastre un archivo **JSON** con la estructura del plan de estudios. "
        "El archivo debe contener los cursos, prerrequisitos y corequisitos "
        "del programa académico."
    )

    with st.expander("Ver formato JSON esperado"):
        st.code(JSON_FORMAT_EXAMPLE, language="json")
        st.markdown(
            "**Campos obligatorios de cada curso:**\n"
            "- `code` — Código único de la asignatura\n"
            "- `name` — Nombre completo\n"
            "- `credits` — Número de créditos\n\n"
            "**Campos opcionales:** `semester`, `area`, `required`, "
            "`elective_group`, `semester_offered`, `min_completed_credits`, "
            "`difficulty`, `weight`, `metadata`."
        )

    uploaded_graph = render_file_uploader()
    if uploaded_graph is not None:
        st.session_state.graph = uploaded_graph
        st.session_state.data_source = "Archivo cargado"
        if "tracker" in st.session_state:
            del st.session_state.tracker
        st.success("Grafo cargado desde archivo. Cambie al modo Planificador para verlo.")
