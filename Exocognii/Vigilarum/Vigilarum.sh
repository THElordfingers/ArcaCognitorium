#!/bin/bash
#
##
###
#####
######## Vigilarum.sh


APP="Vigilarum"
VENV=$(echo "${APP}" | tr '[:lower:]' '[:upper:]')

cd ~/ArcaCognitorium/Exocognii/${APP}
source venv-${VENV}/bin/activate
python3 control.py
