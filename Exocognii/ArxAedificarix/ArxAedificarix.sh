#!/bin/bash
#
##
###
#####
######## ArxAedificarix.sh



set -e

ARCA_ROOT="$HOME/ArcaCognitorium"
EXO_DIR="$ARCA_ROOT/Exocognii"
ARX_DIR="$EXO_DIR/ArxAedificarix"
VENV="$ARX_DIR/venv-ARX"
CONFIG="$HOME/.arca/config.json"

# Activate venv
source "$VENV/bin/activate"

# Load API key from environment or ~/.arca/config.json
if [ -z "$CLAUDE_API_KEY" ]; then
    export CLAUDE_API_KEY=$(python3 -c "
import json, sys
try:
    cfg = json.load(open('$CONFIG'))
    print(cfg.get('api_key', ''))
except Exception:
    print('')
")
fi

if [ -z "$CLAUDE_API_KEY" ]; then
    echo "ERROR: CLAUDE_API_KEY not found in environment or $CONFIG" >&2
    exit 1
fi

# Run
cd "$ARCA_ROOT"
python -m Exocognii.ArxAedificarix "$@"
