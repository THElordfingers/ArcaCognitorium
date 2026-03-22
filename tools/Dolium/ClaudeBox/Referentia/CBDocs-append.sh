#!/bin/bash
#
##
###
#####
######## CBDocs-append.sh

DIR=$(pwd)
DOCS="$DIR/CBDocs.txt"

#for file in ~/Anthropic/ClaudeBox/Referentia/*; do
#	filename=$(basename "$file")
#	echo "---------| $filename |-----------------------------------------------------------------------------------" | tee > "$DOCS"
#	cat "$file" | tee > "$DOCS"
#done


for file in $DIR/*.md; do
	filename=$(basename "$file")
	echo "" | tee >> "$DOCS"
	echo "" | tee >> "$DOCS"
	echo "---------| $filename |-----------------------------------------------------------------------------------" | tee >> "$DOCS"
	echo "" | tee >> "$DOCS"
	echo "" | tee >> "$DOCS"
	cat "$file" | tee >> "$DOCS"
	
done



