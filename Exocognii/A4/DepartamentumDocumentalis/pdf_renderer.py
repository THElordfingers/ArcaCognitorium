# Departamentum Documentalis · pdf_renderer.py · v1.1
import subprocess, tempfile, os
from DepartamentumDocumentalis.config import CFG

class PdfRenderError(Exception):
    pass

def render(md_content: str, output_path: str) -> str:
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write(md_content)
        tmp = f.name
    try:
        r = subprocess.run(
            [CFG["pandoc_path"], tmp, "-o", output_path, "-V", "geometry:margin=2cm"],
            capture_output=True, text=True, timeout=60)
        if r.returncode != 0:
            raise PdfRenderError(f"Pandoc error: {r.stderr.strip()}")
        return output_path
    finally:
        os.unlink(tmp)
