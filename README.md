# PrereqFlow

![Python](https://img.shields.io/badge/Python-3.14-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.27+-red)
![PyVis](https://img.shields.io/badge/PyVis-0.3.1+-green)
![Tests](https://img.shields.io/badge/tests-50/50-passing-brightgreen)
![License](https://img.shields.io/badge/license-MIT-yellow)
![GitHub](https://img.shields.io/badge/github-1594--adrs/PrereqFlow-blue)

**Plataforma web para la exploración visual interactiva y gestión dinámica de rutas curriculares.** PrereqFlow modela planes de estudio universitarios como grafos acíclicos dirigidos (DAG) y ofrece un entorno completo para visualizar, editar, planificar y dar seguimiento al progreso académico.

---

## 🚀 Características principales

| Característica | Descripción |
|---|---|
| **Visualización interactiva** | Grafo dirigido con física de nodos, zoom, paneo y colores por área académica |
| **Planificador semestral** | 3 modos: balanceado, rápido, bajo riesgo |
| **Edición en caliente** | Agregar, modificar y eliminar cursos y dependencias en tiempo real |
| **Carga Drag & Drop** | Arrastrar y soltar archivos JSON para cargar currículos personalizados |
| **Seguimiento multi-periodo** | Registro de progreso semestre a semestre con métricas de avance |
| **Electivas inteligentes** | Grupos electivos con reglas de selección configurables |
| **Simulador what-if** | Exploración de rutas alternativas sin modificar el registro real |
| **Persistencia** | Carga/guardado en JSON |
| **Interfaz web** | Construida con Streamlit, sin instalación de servidores adicionales |
| **Caso de estudio** | Currículo de Ingeniería de Sistemas UTP (64 asignaturas, 10 semestres) |

## 🧰 Tecnologías

| Tecnología | Propósito |
|---|---|
| Python 3.14 | Lenguaje principal |
| Streamlit 1.24+ | Framework de interfaz web reactiva |
| PyVis 0.3.1+ / vis-network 9.1.2 | Visualización interactiva de grafos |
| pytest 8.0+ | Pruebas unitarias |

## 📋 Requisitos del sistema

- Python 3.12 o superior
- pip (gestor de paquetes)
- Navegador web moderno

## ⚙️ Instalación y ejecución

```bash
# 1. Clonar el repositorio
git clone https://github.com/1594-adrs/PrereqFlow
cd PrereqFlow

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Ejecutar la aplicación
streamlit run main.py
```

La aplicación se abrirá automáticamente en `http://localhost:8501`.

> **Nota:** En la primera ejecución se genera automáticamente `data/utp_sistemas.json`.

## 📖 Guía de uso

### Modo Planificador

El modo principal permite visualizar el grafo de prerrequisitos y generar planes de estudio.

1. **Panel lateral:** configure créditos máximos, semestres, tipo de plan y cursos ya cursados.
2. **Grafo interactivo:** use zoom (rueda), paneo (arrastrar fondo), y arrastre nodos para explorar.
3. **Plan generado:** revise la distribución semestral con cursos, créditos y áreas.
4. **Selector de materia:** haga clic en cualquier nodo o selecciónelo del menú para ver detalles.

### Modo Editor

Cambie a "Editor de cursos" en la barra lateral para modificar el plan en tiempo real.

- **Agregar curso:** complete el formulario con código, nombre, créditos, semestre y área.
- **Editar curso:** seleccione un curso existente y modifique sus propiedades.
- **Prerrequisitos:** agregue o elimine dependencias mediante selectores.
- **Corequisitos:** gestione relaciones simétricas entre cursos.
- **Eliminar:** remueva cursos y relaciones con un solo clic.
- **Guardar:** persista los cambios a JSON con el botón en la barra lateral.

### Modo Carga (Drag & Drop)

Cambie a "Cargar archivo" para importar currículos personalizados.

1. Arrastre un archivo **JSON** al área de carga.
2. Espere la validación automática (estructura, ciclos, referencias).
3. Revise la vista previa con todos los cursos cargados.
4. Cambie al modo Planificador para visualizar y planificar el nuevo currículo.

**Formato JSON esperado:**
```json
{
  "courses": [
    { "code": "SIS001", "name": "Matemáticas I", "credits": 4, "semester": 1 }
  ],
  "prerequisites": [
    { "course": "SIS005", "prereq": "SIS004" }
  ],
  "co_requisites": [
    { "course": "SIS011", "co_req": "SIS012" }
  ]
}
```

### Modo Seguimiento

Cambie a "Seguimiento" para gestionar el progreso académico.

- **Progreso:** métricas de cursos aprobados, créditos acumulados y porcentaje de avance.
- **Registrar semestre:** seleccione los cursos aprobados y regístrelos.
- **Electivas:** explore grupos electivos disponibles y realice selecciones.
- **Simulador what-if:** pruebe diferentes combinaciones de cursos para ver cómo cambiaría su progreso.

## 🧪 Ejecutar pruebas

```bash
pytest              # Ejecuta las 50 pruebas unitarias
pytest -v           # Modo verbose
pytest tests/       # Pruebas de un directorio específico
```

## 📁 Estructura del proyecto

```
PrereqFlow/
├── main.py                          # Punto de entrada (Streamlit)
├── prereqflow/                      # Paquete principal
│   ├── __init__.py                  # Exportaciones
│   ├── __main__.py                  # Ejecución como módulo
│   ├── models.py                    # Modelo Course (dataclass)
│   ├── graph.py                     # PrereqGraph (DAG)
│   ├── planner.py                   # SemesterPlanner
│   ├── editor.py                    # Editor interactivo
│   ├── uploader.py                  # Carga Drag & Drop
│   ├── tracker.py                   # Seguimiento + electivas
│   ├── visualization.py             # Renderizado PyVis
│   ├── io.py                        # Persistencia JSON
│   ├── utils.py                     # Utilidades de interfaz
│   └── modes/                       # Componentes de interfaz por modo
│       ├── planner_ui.py            # Interfaz del Planificador
│       ├── editor_ui.py             # Interfaz del Editor
│       ├── uploader_ui.py           # Interfaz de Carga
│       └── tracker_ui.py            # Interfaz de Seguimiento
├── tests/                           # Pruebas unitarias (50 tests)
│   ├── test_graph.py                # Pruebas de PrereqGraph
│   ├── test_planner.py              # Pruebas del planificador
│   ├── test_io.py                   # Pruebas de persistencia
│   ├── test_editor.py               # Pruebas del editor
│   ├── test_uploader.py             # Pruebas del cargador
│   └── test_tracker.py              # Pruebas del seguidor
├── data/
│   ├── utp_sistemas.json            # Currículo UTP serializado
│   └── user_data.json               # Datos de usuario (generado)
├── examples/                        # 12 currículos JSON de ejemplo
├── docs/                            # Documentación técnica
├── lib/                             # Librerías frontend
├── Trabajo escrito/                 # Documento LaTeX (APA 7)
├── pyproject.toml                   # Configuración del proyecto
├── requirements.txt                 # Dependencias
└── README.md                        # Esta documentación
```

## 📄 Licencia

Proyecto **Open Source** distribuido bajo la **licencia MIT**.

**Autor:** Andrés David Rincón Salazar — andres.rincon2@utp.edu.co  
**Materia:** Estructuras de Datos — Proyecto Final  
**Universidad Tecnológica de Pereira — Mayo 2026**

**Repositorio:** [https://github.com/1594-adrs/PrereqFlow](https://github.com/1594-adrs/PrereqFlow)
