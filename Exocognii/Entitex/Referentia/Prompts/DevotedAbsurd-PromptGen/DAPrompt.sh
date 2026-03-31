#!/bin/bash
#
##
###
#####
######## DAPrompt.sh



nohup konsole --hold --profile "ArcaCognitorium" --geometry 423x276+5119+336 > /dev/null 2>&1 & kons_pid=$!
         
 kons_sessid=$(echo 'org.kde.konsole-')$kons_pid
 kons_id=$(xdotool search --sync --pid $kons_pid)
        xdotool set_window --name 'lordfingers@CastrumDigitos: ~/ArcaCognitorium — Konsole' $kons_id
        xdotool set_window --class 'konsole' $kons_id
        xdotool set_window --classname 'konsole' $kons_id




qdbus6 "${kons_sessid}" /Sessions/1 org.kde.konsole.Session.runCommand "cd /home/lordfingers/ArcaCognitorium/Exocognii/Entitex/Referentia/Prompts/DevotedAbsurd-PromptGen/"
qdbus6 "${kons_sessid}" /Sessions/1 org.kde.konsole.Session.runCommand "source venv-DEVOTED_ABSURD/bin/activate"
qdbus6 "${kons_sessid}" /Sessions/1 org.kde.konsole.Session.runCommand "python3 __main__.py"
