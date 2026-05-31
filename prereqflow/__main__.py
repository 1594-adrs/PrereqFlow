"""Entry point para ``python -m prereqflow``.

Inicia la aplicación Streamlit de PrereqFlow.
"""

import sys
from pathlib import Path


def main() -> None:
    """Ejecuta ``streamlit run main.py`` desde el directorio raíz del proyecto."""
    project_root = Path(__file__).resolve().parent.parent
    main_py = project_root / "main.py"

    if not main_py.exists():
        print(f"Error: no se encontró {main_py}", file=sys.stderr)
        sys.exit(1)

    import streamlit.web.cli as st_cli
    sys.argv = ["streamlit", "run", str(main_py)]
    st_cli.main()


if __name__ == "__main__":
    main()
