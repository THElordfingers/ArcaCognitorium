#!/bin/bash
#
##
###
#####
######## Entitex.sh


APP="Entitex"
VENV=echo "${APP}" | tr '[:lower:]' '[:upper:]'

cd ~/ArcaCognitorium/Exocognii/${APP}
source venv-${VENV}/bin/activate
python3 ${APP}.py
