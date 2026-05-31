"""PrereqFlow: Planificador académico basado en grafos dirigidos.

PrereqFlow modela planes de estudio universitarios como grafos acíclicos
dirigidos (DAG), donde las asignaturas son nodos y los prerrequisitos son
aristas. Proporciona visualización interactiva, detección de ciclos,
ordenamiento topológico, generación automatizada de planes semestrales,
edición interactiva en caliente, carga dinámica de archivos curriculares
mediante Drag & Drop, soporte avanzado de electivas y seguimiento del
progreso estudiantil multi-periodo.

Módulos principales:
    - models: Definición del modelo Course (dataclass).
    - graph: Clase PrereqGraph con operaciones sobre grafos dirigidos.
    - planner: Planificador semestral con múltiples estrategias.
    - visualization: Renderizado interactivo mediante PyVis.
    - io: Persistencia en formatos JSON y CSV.
    - editor: Edición interactiva de cursos y dependencias en caliente.
    - uploader: Carga dinámica de archivos curriculares (Drag & Drop).
    - tracker: Seguimiento de progreso y soporte avanzado de electivas.
"""

from .models import Course
from .graph import PrereqGraph
from .planner import SemesterPlanner, generate_study_plan
from .visualization import render_graph
from .io import (
    load_graph_from_json,
    save_graph_to_json,
    load_graph_from_csv,
    save_graph_to_csv,
)
from .editor import render_course_editor
from .uploader import render_file_uploader
from .utils import course_label, course_select_options
from .tracker import (
    ProgressTracker,
    ElectiveManager,
    ElectiveGroup,
    StudentRecord,
)

__all__ = [
    "Course",
    "PrereqGraph",
    "SemesterPlanner",
    "generate_study_plan",
    "render_graph",
    "load_graph_from_json",
    "save_graph_to_json",
    "load_graph_from_csv",
    "save_graph_to_csv",
    "render_course_editor",
    "render_file_uploader",
    "course_label",
    "course_select_options",
    "ProgressTracker",
    "ElectiveManager",
    "ElectiveGroup",
    "StudentRecord",
]
