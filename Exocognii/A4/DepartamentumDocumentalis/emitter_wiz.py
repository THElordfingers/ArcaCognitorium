# Departamentum Documentalis — emitter_wiz.py
# v1.0.0
"""Python wrapper for the Node.js .wiz emitter."""

import json
import subprocess
import tempfile
from pathlib import Path
from dataclasses import asdict

from .schema import BureauDocument


def _get_emitter_script() -> Path:
    """Locate the Node.js emitter script."""
    return Path(__file__).resolve().parent / 'emitter_wiz.js'


def _doc_to_json(doc: BureauDocument) -> str:
    """Serialize a BureauDocument to JSON for the Node emitter."""
    data = asdict(doc)
    return json.dumps(data, indent=2, ensure_ascii=False)


def emit_wiz(doc: BureauDocument, output_path: Path):
    """Emit a .wiz file by invoking the Node.js emitter.

    Raises RuntimeError if Node is not available or emitter fails.
    """
    script = _get_emitter_script()
    if not script.exists():
        raise RuntimeError(f"Emitter script not found: {script}")

    with tempfile.NamedTemporaryFile(
        mode='w', suffix='.json', delete=False, encoding='utf-8'
    ) as f:
        f.write(_doc_to_json(doc))
        ast_path = f.name

    try:
        result = subprocess.run(
            ['node', str(script), ast_path, str(output_path)],
            capture_output=True, text=True, timeout=30,
        )
        if result.returncode != 0:
            raise RuntimeError(
                f"emitter_wiz.js failed: {result.stderr.strip()}"
            )
    except FileNotFoundError:
        raise RuntimeError(
            "Node.js not found. Install Node.js to emit .wiz files."
        )
    finally:
        Path(ast_path).unlink(missing_ok=True)
