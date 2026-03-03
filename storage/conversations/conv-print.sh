#!/bin/bash
#
##
###
#####
######## conv-print.sh


title="$1"
dir="${2:-.}"

if [[ -z "$title" ]]; then
  echo "Usage: $0 'Title string' [directory]"
    exit 1
    fi

    found=0
    while IFS= read -r -d '' f; do
      out=$(jq -r --arg t "$title" 'if type=="array" then .[] else . end
          | select(.title == $t)
              | .content' "$f" 2>/dev/null)
                if [[ -n "$out" ]]; then
                    ((found++))
                        printf '----- %s -----\n' "$f"
                            printf '%s\n\n' "$out"
                              fi
                              done < <(find "$dir" -type f -name '*.json' -print0)

                              if (( found == 0 )); then
                                echo "No match found for title: $title"
                                  exit 2
                                  fi

