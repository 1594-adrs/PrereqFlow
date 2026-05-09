# PrereqFlow

PrereqFlow is a Python-based academic planning system for university curricula. The project models courses as nodes and prerequisite requirements as directed edges, then generates feasible semester-by-semester study plans while showing course dependencies in an interactive graph.

This repository includes a sample dataset modeled after the UTP Ingeniería de Sistemas curriculum.

## What it solves
- Visualizes course prerequisites as a directed graph.
- Detects cycles and impossible prerequisite loops.
- Generates valid semester plans under credit constraints.
- Respecta semestres sugeridos, disponibilidad de materias y requisitos de créditos aprobados.
- Soporta co-requisitos y metadatos de área académica en el plan.
- Permite cargar el currículo desde `data/utp_sistemas.json` o usar el currículo integrado de ejemplo.
- Ayuda a estudiantes y asesores a explorar la estructura del currículo y las rutas de avance.

## Key features
- Course and prerequisite graph model.
- Graph algorithms for cycle detection and topological sorting.
- Semester assignment planner.
- Interactive visualization using Streamlit and PyVis.
- Persistence support for JSON and CSV course data.

## Getting started
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Run the application:
   ```bash
   streamlit run main.py
   ```
3. The first run generates `data/utp_sistemas.json` automatically from the embedded curriculum model. The current JSON dataset reflects the UTP Ingeniería de Sistemas plan extracted from the official PDF.
   ```bash
   streamlit run main.py
   ```

## Project structure
- `main.py` — interactive Streamlit application entrypoint.
- `prereqflow/models.py` — course model definitions.
- `prereqflow/graph.py` — directed prerequisite graph operations.
- `prereqflow/planner.py` — study plan generation algorithms.
- `prereqflow/visualization.py` — PyVis graph renderer.
- `prereqflow/io.py` — JSON/CSV persistence utilities.
- `tests/` — baseline unit tests for graph behavior and planning.

## Future improvements
- Add course editing directly in the UI.
- Load custom curriculum files from the browser.
- Support elective groups, student progress tracking, and multi-term planning options.
