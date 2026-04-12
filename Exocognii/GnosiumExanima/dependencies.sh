#!/usr/bin/env bash
# GNOSIUM EXANIMA — dependencies.sh
# Create venv-GNOSIUM at the Arca root and install runtime deps.
# v1.0.0

set -euo pipefail

ARCA="${HOME}/ArcaCognitorium"
VENV="${ARCA}/venv-GNOSIUM"
REQ="${ARCA}/Exocognii/GnosiumExanima/requirements.txt"

if [[ ! -d "${VENV}" ]]; then
    python3 -m venv "${VENV}"
fi

source "${VENV}/bin/activate"
pip install --upgrade pip
pip install -r "${REQ}"
# ClaudeBox is imported by path — no separate pip install needed.

echo "GNOSIUM EXANIMA dependencies installed into ${VENV}"
