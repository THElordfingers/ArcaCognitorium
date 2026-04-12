#!/bin/bash
#
##
###
#####
######## touch-py.sh


Touchpy() {
  while true; do
    read -p "Enter a filename (or 'exit'): " PYFILE

    if [[ "$PYFILE" == "exit" ]]; then
      echo "Py'd out."
      break
    fi

    touch "${PYFILE}.py"
    echo "Touched ${PYFILE}.py"
  done
}

Touchpy
