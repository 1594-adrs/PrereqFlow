"""Modo Editor — interfaz de edición interactiva de cursos.

Proporciona el envoltorio de Streamlit que integra el editor de cursos
con el guardado a archivo JSON.
"""

from pathlib import Path
from typing import Union

import streamlit as st

from ..graph import PrereqGraph
from ..editor import render_course_editor
from ..io import save_graph_to_json


def render_editor_mode(graph: PrereqGraph, data_file: Union[str, Path]) -> None:
    """Renderiza el modo Editor de Cursos completo.

    Args:
        graph: Grafo de prerrequisitos a editar.
        data_file: Ruta al archivo JSON donde persistir los cambios.
    """
    st.title("✏️ Editor Interactivo de Cursos")
    st.markdown(
        "Modifique el plan de estudios en tiempo real. "
        "Los cambios se reflejan inmediatamente en la visualización "
        "y el planificador."
    )
    st.sidebar.info(
        "Use el panel de edición para agregar, modificar o eliminar "
        "cursos y sus dependencias."
    )
    render_course_editor(graph)
    if st.sidebar.button("Guardar cambios a JSON", type="primary"):
        save_graph_to_json(graph, str(data_file))
        st.sidebar.success(f"Plan de estudios guardado en {data_file}")
