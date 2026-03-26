#!/bin/bash
#
##
###
#####
######## gen_init_urls.sh 
#
# gen_init_urls.sh — Generate raw GitHub URLs for all Tower source files
# v1.1 — excludes venvs, caches, build artifacts
#

REPO_PATH="/home/lordfingers/ArcaCognitorium"
GITHUB_USER="THElordfingers"
REPO_NAME="ArcaCognitorium"
BRANCH="main"
BASE_URL="https://raw.githubusercontent.com/${GITHUB_USER}/${REPO_NAME}/${BRANCH}"

echo "# INIT FILE LIST — ArcaCognitorium"
echo "# Generated: $(date)"
echo "# Branch: ${BRANCH}"
echo ""

find "$REPO_PATH" -type f \
    -not -path "*/.git/*" \
    -not -path "*/__pycache__/*" \
    -not -path "*/.mypy_cache/*" \
    -not -path "*/venv*/*" \
    -not -path "*/node_modules/*" \
    -not -path "*/.egg-info/*" \
    -not -name "*.pyc" \
    -not -name "*.pyo" \
    -not -name ".DS_Store" \
    -not -name "*.dist-info" \
    | sort | while read -r filepath; do
        relative="${filepath#$REPO_PATH/}"
        echo "${BASE_URL}/${relative}"
    done
