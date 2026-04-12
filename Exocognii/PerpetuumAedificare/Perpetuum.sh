#!/bin/bash
#
##
###
#####
######## Perpetuum.sh


APP="PerpetuumAedificare"
VENV="PERPETUUM"

cd ~/ArcaCognitorium/Exocognii/${APP}
source venv-${VENV}/bin/activate
python3 main.py
