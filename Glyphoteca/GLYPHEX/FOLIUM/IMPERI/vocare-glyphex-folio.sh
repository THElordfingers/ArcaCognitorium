#!/bin/bash
#
##
###
#####
######## vocare-glyphex-folio.sh

PROFILE="FOLIUM"

nohup konsole --hold --profile "${PROFILE}" --geometry 606x645+3929+147 -e micro "/home/lordfingers/ArcaCognitorium/Glyphoteca/GLYPHEX/FOLIUM/${1}.folio"  > /dev/null 2>&1 & glyp_pid=$!
         
 glyp_sessid=$(echo 'org.kde.konsole-')$glyp_pid
 glyp_id=$(xdotool search --sync --pid $glyp_pid)
        xdotool set_window --name 'Arca Cognitorium - Glyphex Folio' $glyp_id
        xdotool set_window --class 'folium' $glyp_id
        xdotool set_window --classname 'glyphex' $glyp_id


qdbus6 org.kde.konsole-$glyp_pid /Sessions/1 org.kde.konsole.Session.setProfile "${PROFILE}"


echo "WINDOW_ID: " + "${glyp_id}"
echo "WINDOW_PID: " + "${glyp_pid}"
echo "SESSION_ID: " + $(echo 'org.kde.konsole-')$glyp_pid
