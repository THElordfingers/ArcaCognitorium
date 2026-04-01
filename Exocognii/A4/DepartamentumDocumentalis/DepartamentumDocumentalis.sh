#!/bin/bash
#
##
###
#####
######## DepartamentumDocumentalis.sh


APP="DepartamentumDocumentalis"
VENV="DOCUMENTALIS"

cd ~/ArcaCognitorium/Exocognii/A4/
source ${APP}/venv-${VENV}/bin/activate
python3 -m ${APP}
