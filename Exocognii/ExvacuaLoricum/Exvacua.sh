#!/bin/bash
#
##
###
#####
######## Exvacua.sh


APP="Exvacua"
VENV=$(echo "${APP}" | tr '[:lower:]' '[:upper:]')

cd ~/ArcaCognitorium/Exocognii/${APP}
source venv-${VENV}/bin/activate
python3 main.py
