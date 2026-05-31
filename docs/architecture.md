# Arquitectura del Sistema — PrereqFlow

## Visión General

PrereqFlow sigue una **arquitectura en tres capas** con cuatro modos de operación que
comparten la misma capa de lógica y datos. La capa de presentación se organiza en
módulos independientes dentro de ``prereqflow/modes/``, todos invocados desde el
despachador central ``main.py``.

```
+----------------------------------------------------------------------+
|                    CAPA DE PRESENTACIÓN (main.py)                      |
|                                                                        |
|  ┌─────────────────┐  ┌───────────────┐  ┌─────────────┐  ┌──────────┐|
|  │ modes/planner_ui│  │ modes/editor_ui│  │modes/upload_ │  │modes/track│|
|  │ - Grafo PyVis   │  │ - Formularios │  │ - Drag&Drop  │  │ - Progreso│
|  │ - Plan semest.  │  │ - Edición     │  │ - Validación │  │ - Electiv.│
|  │ - Info curso    │  │ - Eliminar    │  │ - Formato    │  │ - Simulad.│
|  └─────────────────┘  └───────────────┘  └─────────────┘  └──────────┘|
+----------------------------------------------------------------------+
          |                    |              |              |
          v                    v              v              v
+----------------------------------------------------------------------+
|                      CAPA DE LÓGICA (prereqflow/)                      |
|                                                                        |
|  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌───────┐ ┌───────┐ ┌───────┐|
|  │ models   │ │ graph    │ │ planner  │ │editor │ │upload │ │tracker│|
|  │ Course   │ │PrereqGraph││SemPlan.  │ │render │ │render │ │Progr. │|
|  └──────────┘ └──────────┘ └──────────┘ └───────┘ └───────┘ └───────┘|
|       │            │            │                                      |
|       │       ┌────┴────┐      │        ┌─────────────────┐           |
|       │       │ utils   │      │        │ visualization   │           |
|       │       │ labels  │      │        │ build_pyvis_net │           |
|       │       └────┬────┘      │        └─────────────────┘           |
|       │            │            │                                      |
+----------------------------------------------------------------------+
          |                        |
          v                        v
+----------------------------------------------------------------------+
|                      CAPA DE DATOS                                     |
|                                                                        |
|  ┌─────────────────────────────┐  ┌────────────────────────────────┐   |
|  │ io.py                       │  │ data/utp_sistemas.json         │   |
|  │ save/load JSON              │  │ Currículo UTP serializado      │   |
|  │                            │  │ examples/ (*.json)             │   |
|  └─────────────────────────────┘  └────────────────────────────────┘   |
+----------------------------------------------------------------------+
```

### Módulos de interfaz (``modes/``)

Cada modo es un módulo independiente con su propia función ``render_*_mode()``:

| Módulo | Función | Propósito |
|--------|---------|-----------|
| ``planner_ui.py`` | ``render_planner_mode()`` | Visualización, planificación y consulta de cursos |
| ``editor_ui.py`` | ``render_editor_mode()`` | Edición interactiva y guardado a JSON |
| ``uploader_ui.py`` | ``render_uploader_mode()`` | Carga Drag & Drop con validación y guía de formato |
| ``tracker_ui.py`` | ``render_tracker_mode()`` | Seguimiento, electivas y simulador what-if |

## Flujo de datos por modo

### Modo Planificador
1. Carga del grafo desde JSON o currículo integrado.
2. Usuario configura parámetros en sidebar.
3. Se ejecuta `generate_study_plan()`.
4. Se renderiza grafo con `render_graph()`.
5. Se muestra plan semestral e información de curso seleccionado.

### Modo Editor
1. `render_course_editor()` muestra formularios dinámicos.
2. Usuario agrega/edita/elimina cursos y relaciones.
3. Cada operación modifica el `PrereqGraph` en `st.session_state.graph`.
4. `st.rerun()` actualiza toda la interfaz con los cambios reflejados.
5. Opcional: `save_graph_to_json()` persiste los cambios.

### Modo Carga
1. `render_uploader_mode()` (en ``uploader_ui.py``) muestra el título y la guía de formato.
2. `render_file_uploader()` presenta el componente `st.file_uploader` (solo .json).
3. Usuario arrastra archivo JSON.
4. Se valida estructura, se construye `PrereqGraph`.
5. Se detectan ciclos automáticamente.
6. Si es válido, se reemplaza el grafo actual en sesión.

### Modo Seguimiento
1. `ProgressTracker` mantiene `StudentRecord` en `st.session_state.tracker`.
2. Pestaña Progreso: muestra métricas y permite registrar semestres.
3. Pestaña Electivas: `ElectiveManager` filtra cursos disponibles.
4. Pestaña Simulador: `simulate_semester()` explora escenarios hipotéticos.

## Diagrama de clases completo

```
┌──────────────────────────────────┐
│            Course                │
├──────────────────────────────────┤
│ code, name, credits, semester,   │
│ area, elective_group, required,  │
│ co_requisites, weight, difficulty│
│ semester_offered, metadata       │
├──────────────────────────────────┤
│ + to_dict(): Dict                │
│ + is_offered_in_semester(): bool │
│ + from_dict(): Course            │
└──────────────────────────────────┘
              │ 1..*
              ▼
┌──────────────────────────────────┐
│          PrereqGraph             │
├──────────────────────────────────┤
│ courses, prerequisites,          │
│ dependents, co_requisites        │
├──────────────────────────────────┤
│ CRUD de cursos y relaciones      │
│ detect_cycle(), topological_sort │
│ prerequisite_closure(), depth()  │
│ eligible_courses(), to/from_dict │
└──────────────────────────────────┘
         ▲              │
         │              │
┌────────┴────────┐     │ 1
│ SemesterPlanner │     │
├─────────────────┤     │
│ plan()          │     │
└─────────────────┘     │
                        │ 1
┌──────────────────────────────────┐
│       ProgressTracker           │
├──────────────────────────────────┤
│ record: StudentRecord            │
│ graph: PrereqGraph               │
├──────────────────────────────────┤
│ complete_semester()              │
│ get_progress_summary()           │
│ simulate_semester()              │
│ get_eligible_courses()           │
└──────────────────────────────────┘
         │ 1
         ▼
┌──────────────────────────────────┐
│      ElectiveManager             │
├──────────────────────────────────┤
│ elective_groups: Dict            │
├──────────────────────────────────┤
│ add_group(), add_course_to_group │
│ get_available_electives()        │
│ validate_selection()             │
└──────────────────────────────────┘
         │ 1..*
         ▼
┌──────────────────────────────────┐
│       ElectiveGroup              │
├──────────────────────────────────┤
│ name, course_codes, course_creds │
│ min_select, max_select, min_cred │
│ description                      │
└──────────────────────────────────┘
```

## Tecnologías y dependencias

| Componente | Tecnología | Propósito |
|---|---|---|
| Interfaz de usuario | Streamlit 1.24+ | Framework web reactivo en Python |
| Visualización de grafos | PyVis 0.3.1+ / vis-network 9.1.2 | Renderizado interactivo HTML5 |
| Modelo de datos | Python dataclasses | Estructuras tipadas inmutables |
| Serialización | JSON | Persistencia del plan de estudios |
| Pruebas | pytest 8.0+ | Framework de testing unitario |
