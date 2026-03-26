#!/bin/bash
#
##
###
#####
######## json-ripper.sh


#!/usr/bin/env bash

INPUT="$1"
OUTPUT_DIR="conversations"

mkdir -p "$OUTPUT_DIR"

jq -c '.[]' "$INPUT" | while read -r convo; do
    name=$(echo "$convo" | jq -r '.name')

    # cleaner filename
    safe_name=$(echo "$name" \
        | tr '[:upper:]' '[:lower:]' \
        | sed 's/[^a-z0-9]+/-/g' \
        | sed 's/^-//;s/-$//')

    outfile="$OUTPUT_DIR/${safe_name}.txt"
    > "$outfile"

    echo "$convo" | jq -c '.chat_messages[]' | while read -r msg; do
        sender=$(echo "$msg" | jq -r '.sender')
        text=$(echo "$msg" | jq -r '.text')

        # skip null text
        [[ "$text" == "null" ]] && continue

        case "$sender" in
            human) sender="LordFingers" ;;
            assistant) sender="Claude" ;;
        esac

        # Wrap to 80 chars, preserve words (-s)
        printf "%s: " "$sender" >> "$outfile"
        echo "$text" | fold -s -w 80 >> "$outfile"
        echo "" >> "$outfile"
    done

done
