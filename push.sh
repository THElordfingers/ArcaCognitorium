#!/bin/bash
#
##
###
#####
######## push.sh
# push.sh — Push ArcaCognitorium to GitHub
# v1.0


cd /home/lordfingers/ArcaCognitorium

git add -A
git status

echo ""
read -p "Commit message: " msg
git commit -m "$msg"
git pushconfig.json for the repo path.
