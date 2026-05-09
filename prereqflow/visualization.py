import tempfile
from typing import Any, Optional

from .graph import PrereqGraph

try:
    from pyvis.network import Network
except ImportError:
    Network = None


def _area_color(area: Optional[str]) -> str:
    mapping = {
        "matemáticas": "#8ecae6",
        "programación": "#219ebc",
        "sistemas": "#fb8500",
        "redes": "#ffb703",
        "seguridad": "#023047",
        "inteligencia": "#219ebc",
        "proyecto": "#6a4c93",
        None: "#8ecae6",
    }
    if not area:
        return mapping[None]
    key = area.lower()
    for token, color in mapping.items():
        if token is not None and token in key:
            return color
    return mapping[None]


def build_pyvis_network(graph: PrereqGraph, height: str = "650px", width: str = "100%") -> Any:
    if Network is None:
        raise ImportError(
            "pyvis is required to build the prerequisite graph visualization. "
            "Install it with `pip install pyvis`."
        )
    net = Network(height=height, width=width, directed=True)
    net.toggle_physics(True)
    for course in sorted(graph.courses.values(), key=lambda item: item.code):
        label = f"{course.code}\n{course.name}"
        title = f"{course.name} ({course.credits} cr)"
        if not course.required:
            title += " - Electiva"
        color = _area_color(course.area)
        net.add_node(course.code, label=label, title=title, color=color)
    for course_code, prereqs in graph.prerequisites.items():
        for prereq_code in prereqs:
            net.add_edge(prereq_code, course_code, arrows="to", color="#073b4c")
    for course_code, co_reqs in graph.co_requisites.items():
        for co_req_code in co_reqs:
            if course_code < co_req_code:
                net.add_edge(course_code, co_req_code, color="#fb8500", dashes=True, title="Co-requisito")
    return net


def render_graph(graph: PrereqGraph, height: str = "650px", width: str = "100%") -> Optional[str]:
    try:
        net = build_pyvis_network(graph, height=height, width=width)
    except ImportError as exc:
        return f"<div style='padding: 1rem; font-family: sans-serif; color: #b00020;'>" \
               f"<strong>Gráfico no disponible:</strong> {exc}</div>"
    with tempfile.NamedTemporaryFile(suffix=".html", delete=False, mode="w", encoding="utf-8") as temp_file:
        net.write_html(temp_file.name)
        temp_file.flush()
        temp_file_path = temp_file.name
    with open(temp_file_path, "r", encoding="utf-8") as content_file:
        return content_file.read()
