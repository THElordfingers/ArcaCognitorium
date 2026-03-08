#!/bin/bash
#
##
###
#####
######## ArcaCognitorium.sh


ARCA_DIR="/home/lordfingers/ArcaCognitorium"
VENV_DIR="$ARCA_DIR/venv-OpenAI"
ARCA="$ARCA_DIR/main.py"


exec "$VENV_DIR/bin/python3" "$ARCA"
