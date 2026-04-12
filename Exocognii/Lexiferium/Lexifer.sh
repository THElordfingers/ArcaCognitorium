#!/bin/bash
#
##
###
#####
######## Lexifer.sh

PROF="LEXIFER"


nohup konsole --hold --profile ${PROF} --geometry 960x1080+1920+0 > /dev/null 2>&1 & Lexi_pid=$!
         
 Lexi_sessid=$(echo 'org.kde.konsole-')$Lexi_pid
 Lexi_id=$(xdotool search --sync --pid $Lexi_pid)
        xdotool set_window --name 'Lexiferium' $Lexi_id
        xdotool set_window --class 'Arca-Cognitorium' $Lexi_id
        xdotool set_window --classname 'Lexiferium' $Lexi_id

echo "Lexiferium Session ID:"  "${Lexi_sessid}"
echo "Lexiferium ID:"  $Lexi_id
echo "Lexiferium Process ID:" $Lexi_pid
echo "KONSOLE_DBUS_SERVICE:" $KONSOLE_DBUS_SERVICE 
echo "KONSOLE_DBUS_SESSION:"  $KONSOLE_DBUS_SESSION 
echo "LEXIFER_DBUS_SERVICE:" $LEXI_KDB_SERV
echo "LEXIFER_DBUS_SESSION:" $LEXI_KDB_SESS






qdbus6 "${Lexi_sessid}" /Sessions/1 org.kde.konsole.Session.runCommand "cd ~/ArcaCognitorium/Exocognii/Lexiferium"
qdbus6 "${Lexi_sessid}" /Sessions/1 org.kde.konsole.Session.runCommand "source venv-LEXIFER/bin/activate"
qdbus6 "${Lexi_sessid}" /Sessions/1 org.kde.konsole.Session.sendText $'python3 Lexiferium.py\n' 
sleep 0.5
WIN_ID=$(wmctrl -lp | awk -v pid="$Lexi_pid" '$3==pid{print $1}')
wmctrl -i -r "$WIN_ID" -e 0,1920,0,960,1080







#LEXI_KDB_SERV=$(qdbus6 "${Lexi_sessid}" /Sessions/1 org.kde.konsole.Session.runCommand "echo ${KONSOLE_DBUS_SERVICE}")
#LEXI_KDB_SESS=$(qdbus6 "${Lexi_sessid}" /Sessions/1 org.kde.konsole.Session.runCommand "echo ${KONSOLE_DBUS_SESSION}")
#qdbus6 $LEXI_KDB_SERV $LEXI_KDB_SES org.kde.konsole.Session.sendText "python3 Lexiferium.py"
#qdbus6 ${Lexisessid} /Sessions/1 org.kde.konsole.Session.runCommand "python3 Lexiferium.py"
#qdbus6 "${Lexi_sessid}" /Sessions/1 org.kde.konsole.Session.setProfile ${PROF}
