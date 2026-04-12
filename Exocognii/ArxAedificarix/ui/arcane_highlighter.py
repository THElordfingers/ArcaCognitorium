#!/usr/bin/env python3
"""
🮈🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃▍
🮈      ARX AEDIFICARIX                                                             ▍
🭅▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃🭐
"""
# ╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌
# ⯨                                                                         ⯩
# ⯨   𝐀𝐍𝐍𝐔𝐒 🟌 ＭＭＸＸＶＩ                      ui/arcane_highlighter.py   ⯩
# ⯨                                                                         ⯩
# ╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌

import re

from PyQt6.QtGui import QColor, QFont, QSyntaxHighlighter, QTextCharFormat


class ArcaneHighlighter(QSyntaxHighlighter):
    """
    QSyntaxHighlighter for Python, JSON, YAML, Markdown, and plain text.
    Language is determined from the OutputFile.language field at construction.
    Reapply by constructing a new instance on a new document.

    Colour palette follows ModusArcanus Chromata Arcana.
    """

    # (pattern_string, hex_colour) pairs per language
    _RULES: dict[str, list[tuple[str, str]]] = {
        "python": [
            # Keywords
            (
                r"\b(def|class|import|from|return|if|elif|else|for|while|"
                r"in|not|and|or|True|False|None|with|as|try|except|finally|"
                r"raise|pass|break|continue|lambda|yield|async|await|"
                r"global|nonlocal|del|assert|is)\b",
                "#d4af37",   # C_GOLD
            ),
            # Decorators
            (r"@\w+", "#c87941"),
            # Single-line comments
            (r"#[^\n]*", "#7a6a2a"),           # C_GOLD_DIM
            # Triple-quoted strings (docstrings)
            (r'"""[\s\S]*?"""|\'\'\'[\s\S]*?\'\'\'', "#1a5a5a"),   # C_TEAL
            # Single/double-quoted strings
            (r"'[^'\\]*(?:\\.[^'\\]*)*'|\"[^\"\\]*(?:\\.[^\"\\]*)*\"", "#c8b88a"),  # C_TEXT
            # Numbers
            (r"\b\d+(\.\d+)?\b", "#c87941"),
            # Built-ins
            (
                r"\b(print|len|range|enumerate|zip|map|filter|list|dict|"
                r"set|tuple|str|int|float|bool|type|isinstance|hasattr|"
                r"getattr|setattr|super|object|property|staticmethod|"
                r"classmethod|open|Path)\b",
                "#c8b88a",
            ),
        ],
        "json": [
            # Object keys
            (r'"[^"\\]*"(?=\s*:)', "#d4af37"),
            # String values
            (r':\s*"[^"\\]*"', "#c8b88a"),
            # Booleans and null
            (r'\b(true|false|null)\b', "#1a5a5a"),
            # Numbers
            (r'\b\d+(\.\d+)?\b', "#c87941"),
        ],
        "yaml": [
            # Keys
            (r'^[\w\-]+(?=\s*:)', "#d4af37"),
            # Comments
            (r'#[^\n]*', "#7a6a2a"),
            # Quoted strings
            (r'"[^"]*"|\'[^\']*\'', "#c8b88a"),
            # Booleans / null
            (r'\b(true|false|null|yes|no|on|off)\b', "#1a5a5a"),
            # Numbers
            (r'\b\d+(\.\d+)?\b', "#c87941"),
        ],
        "markdown": [
            # ATX headings
            (r'^#{1,6}\s+.*', "#d4af37"),
            # Bold
            (r'\*\*[^*]+\*\*|__[^_]+__', "#c8b88a"),
            # Inline code
            (r'`[^`]+`', "#1a5a5a"),
            # Fenced code blocks (opening/closing fence line)
            (r'^```\w*', "#7a6a2a"),
            # Links
            (r'\[.*?\]\(.*?\)', "#c87941"),
        ],
        "bash": [
            # Keywords
            (r'\b(if|then|else|elif|fi|for|while|do|done|case|esac|function|'
             r'return|export|local|readonly|source|echo|exit)\b', "#d4af37"),
            # Comments
            (r'#[^\n]*', "#7a6a2a"),
            # Strings
            (r'"[^"\\]*(?:\\.[^"\\]*)*"|\'[^\']*\'', "#c8b88a"),
            # Variables
            (r'\$\{?\w+\}?', "#c87941"),
        ],
        "plain": [],
    }

    def __init__(self, language: str, document) -> None:
        super().__init__(document)
        lang_key = language.lower()
        rules = self._RULES.get(lang_key, self._RULES["plain"])
        self._compiled = self._compile(rules)

    @staticmethod
    def _compile(
        rules: list[tuple[str, str]],
    ) -> list[tuple[re.Pattern, QTextCharFormat]]:
        compiled = []
        for pattern, colour in rules:
            fmt = QTextCharFormat()
            fmt.setForeground(QColor(colour))
            compiled.append((re.compile(pattern, re.MULTILINE), fmt))
        return compiled

    def highlightBlock(self, text: str) -> None:
        for pattern, fmt in self._compiled:
            for match in pattern.finditer(text):
                self.setFormat(match.start(), match.end() - match.start(), fmt)
