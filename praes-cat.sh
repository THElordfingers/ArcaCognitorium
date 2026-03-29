#!/bin/bash
#
##
###
#####
######## praes-cat.sh


touch praes-cat.txt

this=$(cat ~/ArcaCognitorium/Exocognii/Praesidium/widget_base.py)
dog=$(cat ~/ArcaCognitorium/Exocognii/Praesidium/widget_registry.py)  
went=$(cat ~/ArcaCognitorium/Exocognii/Praesidium/praesidium_app.py)
down=$(cat ~/ArcaCognitorium/Exocognii/Praesidium/storage/layout.json)

echo $this$dog$went$down

#echo ${all} | tee praes-cat.txt
