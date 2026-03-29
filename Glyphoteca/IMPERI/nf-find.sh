#!/bin/bash
#
##
###
#####
######## gf-find.sh




#!/usr/bin/env bash
# Search Nerd Fonts glyph names and display results in a formatted table
# Usage: nf-search <term>

TERM="${1:?Usage: nf-search <search-term>}"

curl -s https://raw.githubusercontent.com/ryanoasis/nerd-fonts/master/glyphnames.json | \
jq -r --arg term "$TERM" '
  to_entries[]
  | select(.key | contains($term))
  | [.value.char, .value.code, .key]
  | @tsv
' | awk '
BEGIN {
    W_CHAR = 8
    W_CODE = 8
    W_NAME = 30

    TOP    = "╭" rep("─", W_CHAR) "┬" rep("─", W_CODE) "┬" rep("─", W_NAME) "╮"
    HEADER = "│" pad("char", W_CHAR) "│" pad("code", W_CODE) "│" pad("name", W_NAME) "│"
    HLINE  = "├" rep("─", W_CHAR) "┼" rep("─", W_CODE) "┼" rep("─", W_NAME) "┤"
    DLINE  = "├" rep("┈", W_CHAR) "┼" rep("┈", W_CODE) "┼" rep("┈", W_NAME) "┤"
    BOT    = "╰" rep("─", W_CHAR) "┴" rep("─", W_CODE) "┴" rep("─", W_NAME) "╯"

    print TOP
    print HEADER
    print HLINE
    first = 1
}

function rep(c, n,    s, i) {
    s = ""
    for (i = 0; i < n; i++) s = s c
    return s
}

function pad(s, w,    out) {
    out = sprintf("  %-*s", w - 2, s)
    return substr(out, 1, w)
}

{
    if (!first) print DLINE
    first = 0
    printf "│%s┊%s┊%s│\n", pad($1, W_CHAR), pad($2, W_CODE), pad($3, W_NAME)
}

END {
    print DLINE
    print BOT
}
'
