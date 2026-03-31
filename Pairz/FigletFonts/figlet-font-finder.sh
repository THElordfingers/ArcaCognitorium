#!/bin/bash
#
##
###
#####
######## figlet-font-finder.sh


PROJECT_DIR="$HOME/Colours/Pairz/SampleText/FigletFonts"
SYSTEM_DIR="/usr/share/figlet"
FONT_LIST="$PROJECT_DIR/figlet-font-master-list.txt"

if [[ ! -f "$FONT_LIST" ]]; then
    echo "Error: Font list not found at $FONT_LIST"
    exit 1
fi

# Build a lowercase lookup map of all available system fonts
declare -A font_map
while IFS= read -r sysfile; do
    base=$(basename "$sysfile")
    lower=$(echo "$base" | tr '[:upper:]' '[:lower:]')
    font_map["$lower"]="$sysfile"
done < <(find "$SYSTEM_DIR" -maxdepth 1 -type f \( -name "*.flf" -o -name "*.tlf" \))

copied=0
missing=0

while IFS= read -r line; do
    # Strip surrounding quotes, whitespace, and carriage returns
    font=$(echo "$line" | tr -d '\r' | sed 's/^[[:space:]"]*//;s/[[:space:]"]*$//')
    [[ -z "$font" ]] && continue

    # Try matching case-insensitively against available fonts
    found=""
    for ext in flf tlf; do
        key=$(echo "$font.$ext" | tr '[:upper:]' '[:lower:]')
        if [[ -n "${font_map[$key]}" ]]; then
            found="${font_map[$key]}"
            break
        fi
    done

    if [[ -n "$found" ]]; then
        cp "$found" "$PROJECT_DIR/"
        echo "Copied: $(basename "$found")"
        ((copied++))
    else
        echo "Missing: $font"
        ((missing++))
    fi

done < "$FONT_LIST"

echo ""
echo "Done. $copied copied, $missing not found."
echo ""

if (( missing > 0 )); then
    echo "Tip: run this to search for close matches:"
    echo "  ls $SYSTEM_DIR | grep -i '<fontname>'"
fi
