#!/bin/bash
#
##
###
#####
######## Perpetuum.sh


APP="Perpetuum"
VENV=$(echo "${APP}" | tr '[:lower:]' '[:upper:]')

cd ~/ArcaCognitorium/Exocognii/${APP}
source venv-${VENV}/bin/activate
python3 main.py
