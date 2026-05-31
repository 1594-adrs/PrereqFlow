# Estructuras de Datos — PrereqFlow

## 1. Grafo Dirigido (PrereqGraph)

### Representación

La estructura central del sistema es un **grafo dirigido** implementado con
listas de adyacencia mediante diccionarios de Python. Se mantienen dos
índices paralelos para consultas bidireccionales eficientes:

```python
self.courses: Dict[str, Course]        # Vértices: código → Course
self.prerequisites: Dict[str, Set[str]]  # Aristas: curso → {prerrequisitos}
self.dependents: Dict[str, Set[str]]     # Aristas inversas: curso → {dependientes}
self.co_requisites: Dict[str, Set[str]]  # Corequisitos (relación simétrica)
```

### Justificación

- **Diccionarios (`dict`):** Proveen acceso O(1) por código de curso.
  El código se normaliza a mayúsculas para evitar duplicados.
- **Conjuntos (`set`):** Garantizan que no haya aristas duplicadas y
  permiten pruebas de pertenencia O(1) (ej. `prereqs.issubset(completed)`).
- **Índice dual:** `prerequisites` da los prerrequisitos de un curso;
  `dependents` da los cursos que dependen de él. Sin este segundo índice,
  consultar dependientes requeriría recorrer todo el grafo O(V+E).

### Complejidades algorítmicas

| Operación | Complejidad | Descripción |
|---|---|---|
| `add_course` | O(k) | k = corequisitos declarados |
| `add_prerequisite` | O(1) | Inserción en diccionarios |
| `detect_cycle` | O(V + E) | DFS con pila de recursión |
| `topological_sort` | O(V + E) | DFS postorden |
| `get_prerequisite_closure` | O(V + E) | Recorrido recursivo |
| `course_dependency_depth` | O(V + E) | Recursión con memoización implícita |
| `eligible_courses` | O(V * (V + E)) | Evalúa cada curso contra completados |
| `critical_courses` | O(V log V + V*(V+E)) | Ordenamiento + profundidad |

### Invariantes

1. Todo código de curso se almacena en mayúsculas sin espacios.
2. Un curso no puede ser prerrequisito de sí mismo.
3. Las aristas en `prerequisites` y `dependents` son consistentes:
   si A está en `prerequisites[B]`, entonces B está en `dependents[A]`.
4. `co_requisites` es simétrico: si A está en `co_requisites[B]`,
   entonces B está en `co_requisites[A]`.
5. Un curso válido para planificar no puede tener ciclos (DAG).

## 2. Modelo Course (dataclass)

```python
@dataclass
class Course:
    code: str                       # PK: código único
    name: str                       # Nombre descriptivo
    credits: int = 3                # Peso académico
    semester: Optional[int]         # Semestre sugerido en la malla
    area: Optional[str]             # Área académica (para colorear nodos)
    elective_group: Optional[str]   # Grupo electivo
    min_completed_credits: Optional[int]  # Requisito de créditos aprobados
    required: bool = True           # True = obligatoria, False = electiva
    co_requisites: Set[str]         # Cursos que deben tomarse simultáneamente
    weight: float = 1.0             # Peso relativo para planificación
    difficulty: float = 1.0         # Dificultad estimada
    semester_offered: Optional[List[int]]  # Semestres en que se ofrece
    metadata: Dict[str, object]     # Metadatos extensibles
```

## 3. Algoritmo de Planificación (SemesterPlanner)

### Estrategia: Greedy con priorización

El planificador procesa los semestres secuencialmente. En cada semestre:

1. **Filtrar cursos disponibles:** se evalúa `_is_available()` que verifica:
   - Todos los prerrequisitos están en `completed`.
   - El curso se ofrece en el semestre actual.
   - Los créditos mínimos requeridos están satisfechos.
   - Los corequisitos también son elegibles (verificación recursiva).

2. **Ordenar por prioridad:** según la estrategia seleccionada (`plan_type`):

   - **balanced:** `(semestre_sugerido, dificultad, -profundidad, código)`
   - **fast:** `(-profundidad, créditos, dificultad, código)`
   - **low_risk:** `(dificultad, -dependientes, créditos, código)`

3. **Asignación greedy:** recorre los cursos ordenados y los agrega al
   semestre mientras no se exceda el límite de créditos. Los corequisitos
   se agrupan obligatoriamente mediante cierre transitivo.

## 4. Editor Interactivo (editor.py)

### Flujo de edición

```
render_course_editor(graph)
  │
  ├── SECCIÓN: Agregar nuevo curso
  │     └── Formulario con: código, nombre, créditos, semestre,
  │                          área, oferta semestral
  │     └── _add_course_to_graph():
  │           ├── Validar que código no esté vacío
  │           ├── Validar que nombre no esté vacío
  │           ├── Validar que código no exista ya
  │           ├── Crear Course(...)
  │           └── graph.add_course(course)
  │
  ├── SECCIÓN: Editar curso existente
  │     └── Selector de curso
  │     └── Formulario pre-poblado con valores actuales
  │     └── Botones: Guardar, Agregar prerrequisito, Agregar corequisito
  │
  └── SECCIÓN: Eliminar curso o relación
        └── Eliminar curso: graph.remove_course(code)
        └── Eliminar prerrequisito: graph.remove_prerequisite(c, p)
        └── Eliminar corequisito: graph.remove_co_requisite(c1, c2)
```

## 5. Carga Dinámica Drag & Drop (uploader.py)

### Flujo de procesamiento

```
render_file_uploader()
  │
  ├── st.file_uploader(type=["json", "csv"])
  │
  ├── ¿Archivo subido?
  │    ├── NO → return None
  │    └── SÍ → detectar extensión
  │
  ├── ¿Extensión .json?
  │    ├── json.loads(content)
  │    ├── Validar clave "courses"
  │    └── PrereqGraph.from_dict(data)
  │
  ├── ¿Extensión .csv?
  │    ├── Escribir a archivo temporal
  │    ├── load_graph_from_csv(tmp_path)
  │    └── Eliminar archivo temporal
  │
  ├── graph.detect_cycle()? → advertencia
  ├── Mostrar resumen (cursos, prereqs, coreqs)
  └── Retornar graph
```

## 6. Seguimiento Multi-periodo y Electivas (tracker.py)

### StudentRecord

```python
@dataclass
class StudentRecord:
    completed_courses: Set[str]           # Cursos aprobados
    completed_by_semester: Dict[int, List[str]]  # Historial por semestre
    current_semester: int                 # Último semestre cursado
    total_credits: int                    # Créditos acumulados
    elective_selections: Dict[str, str]   # Mapeo grupo → curso seleccionado
```

### ElectiveGroup

```python
@dataclass
class ElectiveGroup:
    name: str                    # Nombre del grupo
    course_codes: Set[str]       # Cursos del grupo
    course_credits: Dict[str, int]  # Créditos por curso
    min_select: Optional[int]    # Mínimo de cursos a seleccionar
    max_select: Optional[int]    # Máximo de cursos a seleccionar
    min_credits: Optional[int]   # Mínimo de créditos en el grupo
    description: str             # Descripción textual
```

### ProgressTracker

| Método | Descripción |
|---|---|
| `complete_semester(courses, semester)` | Registra un semestre completado |
| `get_completed_courses()` | Retorna cursos aprobados |
| `get_completed_credits()` | Retorna créditos acumulados |
| `get_eligible_courses(semester)` | Cursos disponibles para cursar |
| `get_progress_summary()` | Resumen con métricas de avance |
| `simulate_semester(courses, semester)` | Simulación what-if |
| `select_elective(group, course, manager)` | Selecciona electiva con validación |
| `get_elective_requirements_status(manager)` | Estado de cumplimiento de electivas |

## 7. Persistencia (io.py)

### Formato JSON

```json
{
  "courses": [ { "code": "...", "name": "...", ... } ],
  "prerequisites": [ { "course": "SIS030", "prereq": "SIS013" }, ... ],
  "co_requisites": [ { "course": "SIS011", "co_req": "SIS012" }, ... ]
}
```

### Formato CSV

Cada fila es un curso. Prerrequisitos separados por punto y coma (;).

## 8. Visualización (visualization.py)

### Mapa de colores por área

| Área | Color | Hex |
|---|---|---|
| Matemáticas | Azul claro | `#8ecae6` |
| Computación / Programación | Azul medio | `#219ebc` |
| Sistemas | Naranja | `#fb8500` |
| Redes | Amarillo | `#ffb703` |
| Electrónica | Terracota | `#e76f51` |
| Gestión | Verde azulado | `#2a9d8f` |
| Física | Verde | `#52b788` |
| Humanidades | Lavanda | `#c77dff` |
| Proyecto | Púrpura | `#6a4c93` |

### Estilo de aristas

- **Prerrequisitos:** Sólidas, color `#073b4c`, con flecha (`arrows="to"`).
- **Corequisitos:** Punteadas (`dashes=True`), color `#fb8500`, bidireccionales.
