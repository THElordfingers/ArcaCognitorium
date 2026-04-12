#!/usr/bin/env python3
"""
🮈🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃▍
🮈      ARX AEDIFICARIX                                                             ▍
🭅▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃🭐
"""
# ╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌
# ⯨                                                                         ⯩
# ⯨   𝐀𝐍𝐍𝐔𝐒 🟌 ＭＭＸＸＶＩ                        core/response_parser.py   ⯩
# ⯨                                                                         ⯩
# ╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌

import logging
import re
from dataclasses import dataclass

logger = logging.getLogger("arx.response_parser")

# ---------------------------------------------------------------------------
# Patterns
# ---------------------------------------------------------------------------

# %%FILE block — captures filename, language, description, and body.
# DOTALL so content spans multiple lines. Non-greedy to handle multiple blocks.
_FILE_BLOCK = re.compile(
    r"%%FILE:\s*(?P<filename>[^\n]+)\n"
    r"%%LANG:\s*(?P<language>[^\n]+)\n"
    r"%%DESC:\s*(?P<description>[^\n]+)\n"
    r"(?P<content>.*?)"
    r"%%END",
    re.DOTALL,
)

# %%PHASE token — must appear anywhere in the response.
_PHASE = re.compile(r"%%PHASE:\s*(?P<phase>\w+)")


# ---------------------------------------------------------------------------
# Dataclass
# ---------------------------------------------------------------------------

@dataclass
class OutputFile:
    filename: str
    language: str
    description: str
    content: str


# ---------------------------------------------------------------------------
# Parser
# ---------------------------------------------------------------------------

class ResponseParser:
    """
    Extracts structured content from a Builder response string.

    Returns a 3-tuple: (prose | None, list[OutputFile], phase | None)

    Rules:
        - File blocks (%%FILE…%%END) are extracted and removed from prose.
        - Phase token (%%PHASE: X) is extracted and removed from prose.
        - Malformed file blocks (missing required header lines) are skipped
          with a warning; surrounding prose is preserved.
        - Prose is None if the remaining text is empty or whitespace only.
        - Phase is uppercased.
    """

    @classmethod
    def parse(
        cls, response_text: str
    ) -> tuple[str | None, list[OutputFile], str | None]:
        """
        Parse response_text into (prose, files, phase).

        Parameters
        ----------
        response_text : str
            Raw text from a Builder API response.

        Returns
        -------
        prose : str | None
            Remaining text after all blocks and tokens stripped.
            None if empty/whitespace.
        files : list[OutputFile]
            All successfully parsed file blocks, in order of appearance.
        phase : str | None
            Uppercased phase token value, or None if absent.
        """
        if not response_text:
            return None, [], None

        files: list[OutputFile] = []
        text = response_text

        # --- extract file blocks ---
        for match in _FILE_BLOCK.finditer(text):
            filename    = match.group("filename").strip()
            language    = match.group("language").strip()
            description = match.group("description").strip()
            content     = match.group("content").strip()

            if not filename:
                logger.warning(
                    "ResponseParser: skipping file block with empty filename."
                )
                continue

            files.append(OutputFile(
                filename=filename,
                language=language,
                description=description,
                content=content,
            ))

        # Remove all file blocks from text (even malformed ones that produced
        # no OutputFile — they should not appear in prose).
        text = _FILE_BLOCK.sub("", text)

        # --- extract phase token ---
        phase: str | None = None
        phase_match = _PHASE.search(text)
        if phase_match:
            phase = phase_match.group("phase").strip().upper()
        text = _PHASE.sub("", text)

        # --- normalise prose ---
        prose = text.strip() or None

        if files:
            logger.debug(
                "ResponseParser: %d file block(s) extracted, phase=%r",
                len(files), phase,
            )

        return prose, files, phase

    @classmethod
    def extract_files_only(cls, response_text: str) -> list[OutputFile]:
        """Convenience: return only the file list."""
        _, files, _ = cls.parse(response_text)
        return files

    @classmethod
    def extract_phase_only(cls, response_text: str) -> str | None:
        """Convenience: return only the phase token."""
        _, _, phase = cls.parse(response_text)
        return phase
