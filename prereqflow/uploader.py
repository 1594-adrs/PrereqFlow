"""Carga dinámica de archivos curriculares mediante arrastrar y soltar.

Proporciona un componente de interfaz que permite al usuario cargar
archivos JSON desde su sistema local mediante Drag & Drop.
El contenido se valida, se parsea y se integra en el grafo de
prerrequisitos para su visualización y planificación inmediata.
"""

import json
from pathlib import Path
from typing import Optional

import streamlit as st

from .graph import PrereqGraph
from .io import load_graph_from_json


def render_file_uploader() -> Optional[PrereqGraph]:
    """Renderiza el componente de carga de archivos Drag & Drop.

    Muestra un área de carga que acepta archivos .json.
    Si el usuario arrastra un archivo válido, lo procesa y retorna
    el grafo resultante. Si el archivo es inválido, muestra un
    mensaje de error.

    Returns:
        PrereqGraph si la carga fue exitosa, None en caso contrario.
    """

    uploaded_file = st.file_uploader(
        "Seleccionar archivo",
        type=["json"],
        accept_multiple_files=False,
        key="curriculum_uploader",
        label_visibility="collapsed",
    )

    if uploaded_file is None:
        return None

    file_extension = Path(uploaded_file.name).suffix.lower()
    file_content = uploaded_file.read()

    if len(file_content) == 0:
        st.error("El archivo está vacío.")
        return None

    try:
        with st.spinner(f"Procesando {uploaded_file.name}..."):
            if file_extension == ".json":
                graph = _process_json_upload(file_content, uploaded_file.name)
            else:
                st.error(f"Formato '{file_extension}' no soportado. Use .json.")
                return None

            if graph is None:
                return None

            cycle_detected = graph.detect_cycle()
            num_courses = len(graph.courses)
            num_prereqs = sum(len(v) for v in graph.prerequisites.values())
            num_co = sum(len(v) for v in graph.co_requisites.values()) // 2

            st.success(
                f"✅ **{uploaded_file.name}** cargado correctamente: "
                f"{num_courses} cursos, {num_prereqs} prerrequisitos, "
                f"{num_co} pares de corequisitos."
            )

            if cycle_detected:
                st.warning(
                    "⚠️ El grafo cargado contiene **ciclos**. "
                    "No se podrá generar un plan de estudios hasta "
                    "que se resuelvan."
                )
            else:
                st.info("✅ El grafo es acíclico. La planificación está disponible.")

            with st.expander("Vista previa de cursos cargados"):
                for code, course in sorted(graph.courses.items()):
                    prereqs = graph.get_prerequisites(code)
                    st.write(
                        f"- **{code}** {course.name} "
                        f"({course.credits} créditos) "
                        f"[Área: {course.area or 'N/A'}] "
                        f"→ prereqs: {', '.join(sorted(prereqs)) or 'Ninguno'}"
                    )

            return graph

    except json.JSONDecodeError as exc:
        st.error(f"Error de formato JSON: {exc}")
        return None
    except (ValueError, KeyError) as exc:
        st.error(f"Error en los datos del archivo: {exc}")
        return None
    except Exception as exc:
        st.error(f"Error inesperado al procesar el archivo: {exc}")
        return None


def _process_json_upload(content: bytes, filename: str) -> Optional[PrereqGraph]:
    """Procesa un archivo JSON subido por el usuario.

    Valida la estructura mínima y construye el grafo.

    Args:
        content: Contenido del archivo en bytes.
        filename: Nombre del archivo original.

    Returns:
        PrereqGraph construido desde el JSON.

    Raises:
        ValueError: Si falta la clave 'courses' en el JSON.
    """
    data = json.loads(content.decode("utf-8"))
    if "courses" not in data:
        raise ValueError(
            "El archivo JSON no contiene la clave 'courses'. "
            "Asegúrese de usar el formato exportado por PrereqFlow."
        )
    return PrereqGraph.from_dict(data)
