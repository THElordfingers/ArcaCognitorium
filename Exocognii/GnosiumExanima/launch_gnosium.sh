#!/usr/bin/env bash
# GNOSIUM EXANIMA — launch_gnosium.sh
# v1.0.0
set -euo pipefail

ARCA="${HOME}/ArcaCognitorium"
cd "${ARCA}"
source "${ARCA}/Exocognii/GnosiumExanima/venv-GNOSIUM/bin/activate"
PYTHONPATH="${ARCA}" python3 -m Exocognii.GnosiumExanima "$@"
