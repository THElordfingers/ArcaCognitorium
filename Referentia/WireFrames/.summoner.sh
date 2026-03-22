#!/bin/bash
#
##
###
#####
######## .summoner.sh
#
#
#### Nomenclator		#  
   # ClassisMutator		#
   # Vinculum			#




#########################
#
# Title        :ArcaCognitorium-WireFrame-SigilMIDGUI
# Profile      :ArcaCognitorium.SIGIL
# Class        :ArcaCognit-WF
# Classname    :SigilMIDGUI

nohup konsole --hold --profile 'ArcaCognitorium.SIGIL' --geometry 881x1080+2519+0 -e micro "ArcaCognitorium-WF-Sigil.txt" > /dev/null 2>&1 & Sigi_pid=$!
         
 Sigi_sessid=$(echo 'org.kde.konsole-')$Sigi_pid
 Sigi_id=$(xdotool search --sync --pid $Sigi_pid)
        xdotool set_window --name 'ArcaCognitorium-WireFrame-SigilMIDGUI' $Sigi_id
        xdotool set_window --class 'ArcaCognit-WF' $Sigi_id
        xdotool set_window --classname 'SigilMIDGUI' $Sigi_id

sleep 1
#########################
#
# Title        :ArcaCognitorium-WireFrame-SigilLGUI
# Profile      :ArcaCognitorium
# Class        :ArcaCognit-WF
# Classname    :SigilLGUI

nohup konsole --hold --profile 'ArcaCognitorium' --geometry 599x1080+1920+0 -e micro  > /dev/null 2>&1 & Sigi_pid=$!
         
 Sigi_sessid=$(echo 'org.kde.konsole-')$Sigi_pid
 Sigi_id=$(xdotool search --sync --pid $Sigi_pid)
        xdotool set_window --name 'ArcaCognitorium-WireFrame-SigilLGUI' $Sigi_id
        xdotool set_window --class 'ArcaCognit-WF' $Sigi_id
        xdotool set_window --classname 'SigilLGUI' $Sigi_id

sleep 1 
#########################
#
# Title        :ArcaCognitorium-WireFrame-SigilRGUI
# Profile      :ArcaCognitorium
# Class        :ArcaCognit-WF
# Classname    :SigilRGUI

nohup konsole --hold --profile 'ArcaCognitorium'--geometry 465x1080+3375+0 -e micro  > /dev/null 2>&1 & Sigi_pid=$!
         
 Sigi_sessid=$(echo 'org.kde.konsole-')$Sigi_pid
 Sigi_id=$(xdotool search --sync --pid $Sigi_pid)
        xdotool set_window --name 'ArcaCognitorim-WireFrame-SigilRGUI' $Sigi_id
        xdotool set_window --class 'ArcaCognit-WF' $Sigi_id
        xdotool set_window --classname 'SigilRGUI' $Sigi_id

sleep 1
#########################
#
# Title        :ArcaCognitorium-WireFrame-MainGUI
# Profile      :ArcaCognitorium
# Class        :ArcaCognit-WF
# Classname    :MainGUI


nohup konsole --hold --profile 'ArcaCognitorium.TRANSPARENT' --geometry 1920x1080+1920+0 -e micro "~/ArcaCognitorium/Referentia/WireFrames/ArcaCognitorium-WF.txt" > /dev/null 2>&1 & Main_pid=$!
         
 Main_sessid=$(echo 'org.kde.konsole-')$Main_pid
 Main_id=$(xdotool search --sync --pid $Main_pid)
        xdotool set_window --name 'ArcaCognitorium-WireFrame-MainGUI' $Main_id
        xdotool set_window --class 'ArcaCognit-WF' $Main_id
        xdotool set_window --classname 'MainGUI' $Main_id



