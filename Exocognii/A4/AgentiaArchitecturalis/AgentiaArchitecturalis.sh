#!/bin/bash
#
##
###
#####
######## AgentiaArchitecturalis.sh


APP="AgentiaArchitecturalis"
VENV="ARCHITECTURALIS"

cd ~/ArcaCognitorium/Exocognii/A4/
source ${APP}/venv-${VENV}/bin/activate
python3 -m ${APP}
