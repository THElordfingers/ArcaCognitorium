#!/bin/bash
#
##
###
#####
######## Mythotex.sh


MYTHX_DIR="/home/lordfingers/Mythotex"
VENV_DIR="$MYTHX_DIR/venv-Mythotex"
MYTHX="$MYTHX_DIR/Mythotex.py"


exec "$VENV_DIR/bin/python3" "$MYTHX"
