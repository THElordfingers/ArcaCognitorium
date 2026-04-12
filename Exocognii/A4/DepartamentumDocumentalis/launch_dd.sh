#!/usr/bin/env bash
# Departamentum Documentalis · launcher · v1.1
# Run from anywhere — resolves paths relative to this script.
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
A4_DIR="$(dirname "$SCRIPT_DIR")"
cd "$A4_DIR"
source "$SCRIPT_DIR/venv-DOC/bin/activate"
PYTHONPATH="$A4_DIR" python3 -m DepartamentumDocumentalis "$@"
