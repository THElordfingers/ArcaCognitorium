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
# Title        :ArcaCognitorium-WireFrame-Menu.FC.Index
# Profile      :ArcaCognitorium.TRANSPARENT
# Class        :ArcaCognit-WF
# Classname    :Menu.FC.Index

nohup konsole --hold --profile 'ArcaCognitorium.TRANSPARENT' --qwindowgeometry 599x199+3840+0 --workdir "/home/lordfingers/ArcaCognitorium/Referentia/WireFrames/menus-WF/flow-charts/"  > /dev/null 2>&1 & Menu_pid=$!
         
 Menu_sessid=$(echo 'org.kde.konsole-')$Menu_pid
 Menu_id=$(xdotool search --sync --pid $Menu_pid)
        xdotool set_window --name 'ArcaCognitorium-WireFrame-Menu.FC.Index' $Menu_id
        xdotool set_window --class 'ArcaCognit-WF' $Menu_id
        xdotool set_window --classname 'Menu.FC.Index' $Menu_id






#########################
# Title        :ArcaCognitorium-WireFrame-Menu.WF.Index
# Profile      :ArcaCognitorium.TRANSPARENT
# Class        :ArcaCognit-WF
# Classname    :Menu.WF.Index

nohup konsole --hold --profile 'ArcaCognitorium.TRANSPARENT' --qwindowgeometry '599x881+3840+199' --workdir "/home/lordfingers/ArcaCognitorium/Referentia/WireFrames/menus-WF/" > /dev/null 2>&1 & Menu_pid=$!
         
 Menu_sessid=$(echo 'org.kde.konsole-')$Menu_pid
 Menu_id=$(xdotool search --sync --pid $Menu_pid)
        xdotool set_window --name 'ArcaCognitorium-WireFrame-Menu.FlowChart' $Menu_id
        xdotool set_window --class 'ArcaCognit-WF' $Menu_id
        xdotool set_window --classname 'Menu.FC' $Menu_id





#########################
# Title        :ArcaCognitorium-WireFrame-Menu.FlowChart
# Profile      :ArcaCognitorium
# Class        :ArcaCognit-WF
# Classname    :Menu.FC

nohup konsole --hold --profile 'ArcaCognitorium' --qwindowgeometry 599x881+3840+199 --workdir "/home/lordfingers/ArcaCognitorium/Referentia/WireFrames/menus-WF/flow-charts/" -e micro "/home/lordfingers/ArcaCognitorium/Referentia/WireFrames/menus-WF/flow-charts/01-filum------------menu-FC.txt"  > /dev/null 2>&1 & Menu_pid=$!
         
 Menu_sessid=$(echo 'org.kde.konsole-')$Menu_pid
 Menu_id=$(xdotool search --sync --pid $Menu_pid)
        xdotool set_window --name 'ArcaCognitorium-WireFrame-Menu.FlowChart' $Menu_id
        xdotool set_window --class 'ArcaCognit-WF' $Menu_id
        xdotool set_window --classname 'Menu.FC' $Menu_id




#########################
# Title        :ArcaCognitorium-WireFrame-Menu.WireFrame
# Profile      :ArcaCognitorium
# Class        :ArcaCognit-WF
# Classname    :Menu.WF

nohup konsole --hold --profile 'ArcaCognitorium' --qwindowgeometry 531x881+4439+199 --workdir "/home/lordfingers/ArcaCognitorium/Referentia/WireFrames/menus-WF/" -e micro "/home/lordfingers/ArcaCognitorium/Referentia/WireFrames/menus-WF/01-filum------------menu-WF.txt"  > /dev/null 2>&1 & Menu_pid=$!
         
 Menu_sessid=$(echo 'org.kde.konsole-')$Menu_pid
 Menu_id=$(xdotool search --sync --pid $Menu_pid)
        xdotool set_window --name 'ArcaCognitorium-WireFrame-Menu.WireFrame' $Menu_id
        xdotool set_window --class 'ArcaCognit-WF' $Menu_id
        xdotool set_window --classname 'Menu.WF' $Menu_id



#########################
# Title        :ArcaCognitorium-WireFrame-Menu.AlphaVert
# Profile      :ArcaCognitorium
# Class        :ArcaCognit-WF
# Classname    :Menu.AV

nohup konsole --hold --profile "ArcaCognitorium" --qwindowgeometry 31x450+4970+0 --workdir "/home/lordfingers/ArcaCognitorium/glyphs" -e micro "/home/lordfingers/ArcaCognitorium/glyphs/fullwidth-latin-capitals-vertical.txt" > /dev/null 2>&1 & Menu_pid=$!
         
 Menu_sessid=$(echo 'org.kde.konsole-')$Menu_pid
 Menu_id=$(xdotool search --sync --pid $Menu_pid)
        xdotool set_window --name 'ArcaCognitorium-WireFrame-Menu.AlphaVert' $Menu_id
        xdotool set_window --class 'ArcaCognit-WF' $Menu_id
        xdotool set_window --classname 'Menu.AV' $Menu_id



#########################
# Title        :ArcaCognitorium-WireFrame-Menu.AlphaMain
# Profile      :ArcaCognitorium
# Class        :ArcaCognit-WF
# Classname    :Menu.AM

nohup konsole --hold --profile "ArcaCognitorium" --qwindowgeometry 759x450+5001+0 --workdir "/home/lordfingers/ArcaCognitorium/glyphs" -e micro "/home/lordfingers/ArcaCognitorium/glyphs/menu-font.txt" > /dev/null 2>&1 & Menu_pid=$!
         
 Menu_sessid=$(echo 'org.kde.konsole-')$Menu_pid
 Menu_id=$(xdotool search --sync --pid $Menu_pid)
        xdotool set_window --name 'ArcaCognitorium-WireFrame-Menu.AlphaMain' $Menu_id
        xdotool set_window --class 'ArcaCognit-WF' $Menu_id
        xdotool set_window --classname 'Menu.AM' $Menu_id



#########################
# Title        :ArcaCognitorium-WireFrame-Menu.Glyphs
# Profile      :ArcaCognitorium
# Class        :ArcaCognit-WF
# Classname    :Menu.Glyphs

nohup konsole --hold --profile "ArcaCognitorium" --qwindowgeometry 790x630+4970+450 --workdir "/home/lordfingers/ArcaCognitorium/glyphs" -e micro "/home/lordfingers/ArcaCognitorium/glyphs/glyphs.txt" > /dev/null 2>&1 & Menu_pid=$!
         
 Menu_sessid=$(echo 'org.kde.konsole-')$Menu_pid
 Menu_id=$(xdotool search --sync --pid $Menu_pid)
        xdotool set_window --name 'ArcaCognitorium-WireFrame-Menu.Glyphs' $Menu_id
        xdotool set_window --class 'ArcaCognit-WF' $Menu_id
        xdotool set_window --classname 'Menu.Glyphs' $Menu_id
