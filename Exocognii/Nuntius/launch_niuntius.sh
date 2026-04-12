#!/bin/bash
#
##
###
#####
######## launch_niuntius.sh
# NUNTIUS — launch_niuntius.sh
# v1.1

set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ARCA_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

source "$SCRIPT_DIR/venv-NUNTIUS/bin/activate"
cd "$ARCA_ROOT"
exec env PYTHONPATH="$ARCA_ROOT/Exocognii" python -m Nuntius
