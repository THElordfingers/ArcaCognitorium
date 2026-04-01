#!/bin/bash
#
##
###
#####
######## AuctoritasSpectralis.sh


APP="AuctoritasSpectralis"
VENV="SPECTRALIS"

cd ~/ArcaCognitorium/Exocognii/A4/
source ${APP}/venv-${VENV}/bin/activate
python3 -m ${APP}
