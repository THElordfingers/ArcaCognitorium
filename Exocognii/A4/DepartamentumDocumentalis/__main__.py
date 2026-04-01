# Departamentum Documentalis — Entry Point
# v1.0.0
"""Launch GUI or dispatch CLI commands."""
import sys

if len(sys.argv) > 1:
    from .cli import main as cli_main
    sys.exit(cli_main())
else:
    from .app import main as gui_main
    sys.exit(gui_main())
