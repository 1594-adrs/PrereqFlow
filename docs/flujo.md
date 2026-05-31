# Flujo de Funcionamiento Interno — PrereqFlow

## 1. Flujo de inicio de la aplicación

```
main()
  │
  ├── Inicializar st.session_state (graph, data_source)
  │
  ├── Cargar grafo: load_data_graph()
  │    ├── data/utp_sistemas.json existe? → load_graph_from_json()
  │    └── No existe → build_sample_graph() (currículo UTP integrado)
  │
  ├── Sidebar: selector de modo
  │    ├── "📊 Planificador"  → render_planner_mode(graph, ...)
  │    ├── "✏️ Editor"        → render_editor_mode(graph, data_file)
  │    ├── "📂 Cargar archivo" → render_uploader_mode()
  │    └── "📈 Seguimiento"   → render_tracker_mode(graph)
  │
  └── Según el modo, se ejecuta el flujo correspondiente
```

## 2. Flujo de planificación detallado

```
generate_study_plan(graph, max_credits, max_semesters, plan_type, completed)
  │
  └─ SemesterPlanner(graph, max_credits, max_semesters, plan_type)
       │
       └─ planner.plan(completed)
            │
            ├─ detect_cycle()? → SÍ → raise ValueError
            │
            ├─ completed_set = {normalizar códigos}
            ├─ remaining = cursos no completados
            ├─ plan = [], semester = 1, completed_credits = suma créditos
            │
            ├─ while remaining AND semester <= max_semesters:
            │    │
            │    ├─ available = _available_courses(completed, sem, créditos)
            │    │    │
            │    │    └─ Para cada curso:
            │    │         ├─ _is_available(curso, completed, sem, créditos)
            │    │         │    ├─ prerreq ⊆ completed?
            │    │         │    ├─ is_offered_in_semester(sem)?
            │    │         │    ├─ min_credits ≤ créditos?
            │    │         │    └─ corequisitos: cierre transitivo
            │    │         │       └─ cada coreq: prerreq ⊆ pool?
            │    │         │                              is_offered?
            │    │         │                              créditos mínimos?
            │    │         └─ Ordenar por _course_priority()
            │    │
            │    ├─ Asignación greedy:
            │    │    └─ Para course en available:
            │    │         ├─ closure = _co_requisite_closure()
            │    │         ├─ candidate = {course} ∪ closure
            │    │         ├─ créditos ≤ max_credits?
            │    │         │    ├─ SÍ → agregar al semestre
            │    │         │    └─ NO → continuar
            │    │         └─ ¿créditos ≥ max_credits? → break
            │    │
            │    ├─ ¿semester_courses vacío? → raise ValueError
            │    ├─ plan.append(semester_courses)
            │    ├─ Actualizar completed_set, completed_credits, remaining
            │    └─ semester += 1
            │
            └─ ¿remaining no vacío? → raise ValueError
                 │
                 └─ Retornar plan
```

## 3. Flujo de edición interactiva

```
render_course_editor(graph)
  │
  ├── Formulario: Agregar curso
  │     └── _add_course_to_graph(code, name, credits, sem, area, offered)
  │           ├── Validar: code != "" AND name != "" AND code not in graph
  │           ├── course = Course(code, name, ...)
  │           ├── graph.add_course(course)
  │           └── st.rerun()
  │
  ├── Selector: Editar curso
  │     └── Formulario con valores actuales
  │           ├── Guardar: modificar atributos del dataclass
  │           ├── Agregar prerrequisito:
  │           │     └── _render_add_prerequisite_dialog()
  │           │           ├── listar candidatos (no ya prereq, no self)
  │           │           └── graph.add_prerequisite(course_code, prereq_code)
  │           └── Agregar corequisito:
  │                 └── _render_add_co_requisite_dialog()
  │                       └── graph.add_co_requisite(course_code, co_code)
  │
  └── Controles de eliminación
        ├── Eliminar curso: graph.remove_course(code)
        ├── Eliminar prerrequisito: graph.remove_prerequisite(c, p)
        └── Eliminar corequisito: graph.remove_co_requisite(c1, c2)
```

## 4. Flujo de carga Drag & Drop

```
render_uploader_mode()              # uploader_ui.py
  │
  ├── Mostrar título e instrucciones
  ├── st.expander("Ver formato JSON esperado") → ejemplo colapsable
  │
  ├── render_file_uploader()        # uploader.py
  │    │
  │    ├── st.file_uploader("Seleccionar archivo", type=["json"])
  │    │
  │    ├── ¿Archivo == None? → return None
  │    │
  │    ├── Leer contenido, detectar extensión
  │    ├── CASO .json:
  │    │     ├── data = json.loads(content)
  │    │     ├── Validar "courses" in data
  │    │     └── graph = PrereqGraph.from_dict(data)
  │    │
  │    ├── CASO otro: → error "Formato no soportado"
  │    │
  │    ├── ¿graph.detect_cycle()? → st.warning()
  │    ├── st.success("Cargado: N cursos, M prereqs, K coreqs")
  │    ├── Mostrar vista previa expandible
  │    └── return graph
  │
  ├── ¿graph cargado? → st.session_state.graph = graph
  │                      st.session_state.data_source = "Archivo cargado"
  │                      Limpiar tracker previo
  │
  └── (sin botón "Volver" — el cambio de modo se hace por sidebar)
```

## 5. Flujo de seguimiento multi-periodo

```
render_tracker_panel(graph)
  │
  ├── TAB 1: Progreso
  │     ├── Métricas: semestre, cursos, créditos, % avance
  │     ├── Distribución por área académica
  │     ├── Formulario: cursos aprobados en este semestre
  │     └── complete_semester(courses) con validación de prerreq
  │
  ├── TAB 2: Electivas
  │     ├── Estado de cada grupo electivo (✅/⚠️)
  │     ├── Cursos disponibles: get_available_electives()
  │     └── Selector con validación: validate_selection()
  │
  └── TAB 3: Simulador
        ├── Seleccionar cursos a simular como aprobados
        ├── simulate_semester(courses, semester)
        │     ├── Calcular estado simulado
        │     ├── Recalcular créditos y cursos elegibles
        │     └── Retornar resultados simulados
        └── Mostrar resultados: créditos, cursos elegibles
```

## 6. Flujo de detección de ciclos (DFS)

```
detect_cycle()
  │
  ├─ visited = set()    # Nodos ya procesados
  ├─ stack = set()      # Nodos en pila de recursión actual
  │
  └─ Para cada nodo en courses:
       └─ visit(node):
            ├─ ¿node in stack? → SÍ → ciclo → return True
            ├─ ¿node in visited? → SÍ → return False
            ├─ visited.add(node)
            ├─ stack.add(node)
            ├─ Para cada prereq: visit(prereq)
            ├─ stack.remove(node)
            └─ return False
```

## 7. Flujo de simulación what-if

```
simulate_semester(course_codes, semester)
  │
  ├─ simulated_completed = copy(record.completed_courses)
  ├─ simulated_credits = record.total_credits
  │
  ├─ Para cada code en course_codes:
  │    └─ Si code not in simulated_completed AND code in graph:
  │         ├─ simulated_completed.add(code)
  │         └─ simulated_credits += graph.courses[code].credits
  │
  ├─ next_sem = semester or (current_semester + 1)
  ├─ eligible = graph.eligible_courses(simulated_completed, next_sem, simulated_credits)
  │
  └─ return { cursos_elegibles, creditos_simulados, nuevos_aprobados, ... }
```

## 8. Interacción backend ↔ frontend

```
┌──────────────────────────────────────────────────────────────────────┐
│                      NAVEGADOR (cliente)                              │
│                                                                       │
│  ┌──────────────────────────────────────────────────────────────┐    │
│  │  Streamlit (Reactivo - re-ejecución completa)                │    │
│  │                                                              │    │
│  │  ┌──────────────┐  ┌──────────────┐  ┌───────────────────┐  │    │
│  │  │ Sidebar      │  │ Grafo PyVis  │  │ Plan/Seguimiento  │  │    │
│  │  │ selector modo│──▶│ HTML embebido│──▶│ /Editor/Electivas │  │    │
│  │  │ controles    │  │ vis-network  │  │ componentes        │  │    │
│  │  └──────────────┘  └──────────────┘  └───────────────────┘  │    │
│  └──────────────────────────────────────────────────────────────┘    │
└──────────────────────────────────────────────────────────────────────┘
          │                          ▲
          │ eventos UI               │ HTML/st.rerun()
          ▼                          │
┌──────────────────────────────────────────────────────────────────────┐
│                      SERVIDOR Streamlit                               │
│                                                                       │
│  ┌──────────────────────────────────────────────────────────────┐    │
│  │  Python runtime + st.session_state (persistencia entre       │    │
│  │  re-ejecuciones)                                            │    │
│  │                                                              │    │
│  │  main.py (despachador)                                         │    │
│  │    ├── Planificador: modes/planner_ui.py → planner.py        │    │
│  │    ├── Editor:      modes/editor_ui.py → editor.py           │    │
│  │    ├── Carga:       modes/uploader_ui.py → uploader.py       │    │
│  │    └── Seguimiento: modes/tracker_ui.py → tracker.py         │    │
│  │                                                              │    │
│  │  st.session_state:                                           │    │
│  │    ├── graph        → PrereqGraph (compartido entre modos)   │    │
│  │    ├── tracker      → ProgressTracker                        │    │
│  │    └── data_source  → str                                    │    │
│  └──────────────────────────────────────────────────────────────┘    │
└──────────────────────────────────────────────────────────────────────┘
```

### Ciclo de vida de una interacción

1. Usuario realiza acción (clic en botón, cambio de slider, arrastra archivo).
2. Streamlit dispara re-ejecución completa de `main.py` de arriba a abajo.
3. El modo actual determina qué componentes se renderizan.
4. Si hay modificaciones al grafo, se reflejan inmediatamente.
5. `st.session_state` preserva el estado entre re-ejecuciones.
6. El navegador recibe el HTML actualizado y lo renderiza.
