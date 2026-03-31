#!/bin/bash
#
##
###
#####
######## json-splitter.sh


if [[ -z "$1" ]]; then
    echo "Usage: $0 <input.json>"
    exit 1
fi

INPUT_FILE="$1"
OUTPUT_DIR="$(dirname "$INPUT_FILE")"

if [[ ! -f "$INPUT_FILE" ]]; then
    echo "Error: File '$INPUT_FILE' not found."
    exit 1
fi

python3 - "$INPUT_FILE" "$OUTPUT_DIR" <<'EOF'
import sys
import re
import json

input_file = sys.argv[1]
output_dir = sys.argv[2]

with open(input_file, 'r') as f:
    raw = f.read()

# Parse concatenated JSON objects by tracking brace depth
blocks = []
depth = 0
start = None

for i, ch in enumerate(raw):
    if ch == '{':
        if depth == 0:
            start = i
        depth += 1
    elif ch == '}':
        depth -= 1
        if depth == 0 and start is not None:
            chunk = raw[start:i+1]
            try:
                blocks.append(json.loads(chunk))
            except json.JSONDecodeError as e:
                print(f"Warning: Could not parse block at char {start}: {e}")
            start = None

if not blocks:
    print("Error: No valid JSON blocks found.")
    sys.exit(1)

created = 0
for block in blocks:
    # Find TITLE key (case-insensitive)
    title = None
    for key in block:
        if key.upper() == "TITLE":
            title = block[key]
            break

    if not title:
        print(f"Warning: Block missing TITLE, skipping: {str(block)[:60]}")
        continue

    filename = re.sub(r'\s+', '-', title.strip()) + ".json"
    filepath = f"{output_dir}/{filename}"

    with open(filepath, 'w') as out:
        out.write(json.dumps(block, indent=2))

    print(f"Created: {filepath}")
    created += 1

print(f"\nDone. {created} file(s) created.")
EOF
