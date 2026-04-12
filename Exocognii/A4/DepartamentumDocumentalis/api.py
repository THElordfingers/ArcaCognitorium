# Departamentum Documentalis · api.py · v1.2
import json, uuid
from pathlib import Path
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import DepartamentumDocumentalis.db as db
from DepartamentumDocumentalis.config import CFG
from DepartamentumDocumentalis.scriptura_parser import parse
from DepartamentumDocumentalis.md_renderer import render as md_render
from DepartamentumDocumentalis.wiz_renderer import render as wiz_render, WizRenderError
from DepartamentumDocumentalis.pdf_renderer import render as pdf_render, PdfRenderError
from DepartamentumDocumentalis.chromaticum_bridge import get_theme_snapshot, get_chromatica_list
from DepartamentumDocumentalis.nuntius_emit import emit_event

app = FastAPI(title="Departamentum Documentalis", version="1.2")

class ComposeRequest(BaseModel):
    doc_type: str
    content_data: dict
    bureau_marker: str = "III-DD"
    title: str = "Untitled"
    targets: list = ["md"]

class ComposeResponse(BaseModel):
    archive_id: str
    output_paths: dict
    warnings: list = []
    orphaned_corpus: dict = {}

@app.post("/compose", response_model=ComposeResponse)
def compose(req: ComposeRequest):
    forma = db.get_mandated_forma(req.doc_type)
    if not forma:
        raise HTTPException(404, f"No mandated Forma for: {req.doc_type}")
    fields = db.get_forma_fields(forma["forma_id"])
    warnings, orphaned = [], {}

    for f in fields:
        if f["field_type"] == "PERMISSIVE" and f["required"]:
            if f["name"] not in req.content_data:
                raise HTTPException(422, {"error": "SCHEMA_MISMATCH",
                                          "missing_field": f["name"], "label": f["label"]})

    fixed = {f["name"]: f["fixed_value"] for f in fields
             if f["field_type"] == "FIXED" and f["fixed_value"]}
    known = {f["name"] for f in fields}
    for k in req.content_data:
        if k not in known:
            orphaned[k] = req.content_data[k]
    if orphaned:
        warnings.append(f"Orphaned keys: {list(orphaned.keys())}")

    parts = []
    for f in sorted(fields, key=lambda x: x["position"]):
        if f["field_type"] == "FIXED":
            parts.append(f"|FIXED:{f['name']}|{fixed.get(f['name'], '')}|END|")
        else:
            parts.append(f"|FIELD:{f['name']}|{req.content_data.get(f['name'], '')}|END|")
    source_text = "\n".join(parts)

    pr = parse(source_text)
    if not pr.ok:
        raise HTTPException(422, {"error": "PARSE_ERROR",
                                   "errors": [str(e) for e in pr.errors]})

    chrom    = forma["chromaticum_name"] or "ModusArcanus"
    snapshot = get_theme_snapshot(chrom)
    out_dir  = Path(CFG["output_dir"])
    out_dir.mkdir(parents=True, exist_ok=True)
    archive_id   = str(uuid.uuid4())
    output_paths = {}

    if "md" in req.targets:
        p = str(out_dir / f"{archive_id}.md")
        Path(p).write_text(md_render(pr.ast, fields, fixed), encoding="utf-8")
        output_paths["md"] = p

    if "wiz" in req.targets:
        p = str(out_dir / f"{archive_id}.docx")
        try:
            wiz_render(pr.ast, fields, fixed, p)
            output_paths["wiz"] = p
        except WizRenderError as e:
            warnings.append(f"wiz failed: {e}")

    if "pdf" in req.targets:
        md_txt = Path(output_paths["md"]).read_text() if "md" in output_paths \
                 else md_render(pr.ast, fields, fixed)
        p = str(out_dir / f"{archive_id}.pdf")
        try:
            pdf_render(md_txt, p)
            output_paths["pdf"] = p
        except PdfRenderError as e:
            warnings.append(f"pdf failed: {e}")

    doc_id = str(uuid.uuid4())
    db.execute(
        "INSERT INTO documents (doc_id, forma_id, title, source_text) VALUES (?,?,?,?)",
        (doc_id, forma["forma_id"], req.title, source_text))
    db.execute(
        "INSERT INTO archive (archive_id, doc_id, forma_id, forma_version, status, "
        "bureau_marker, chromaticum_name, theme_snapshot, output_paths, orphaned_corpus) "
        "VALUES (?,?,?,?,'CURRENT',?,?,?,?,?)",
        (archive_id, doc_id, forma["forma_id"], forma["version"],
         req.bureau_marker, chrom, json.dumps(snapshot),
         json.dumps(output_paths), json.dumps(orphaned) if orphaned else None))
    db.execute(
        "INSERT INTO emission_log (log_id, archive_id, event, detail) VALUES (?,?,?,?)",
        (str(uuid.uuid4()), archive_id, "compose", json.dumps({"targets": req.targets})))
    emit_event("document_composed", {
        "archive_id": archive_id, "doc_type": req.doc_type,
        "bureau_marker": req.bureau_marker, "targets": req.targets})

    return ComposeResponse(archive_id=archive_id, output_paths=output_paths,
                           warnings=warnings, orphaned_corpus=orphaned)

@app.get("/forma/mandated/{doc_type}")
def get_mandated(doc_type: str):
    f = db.get_mandated_forma(doc_type)
    if not f: raise HTTPException(404)
    return dict(f)

@app.get("/archive")
def list_archive(limit: int = 100):
    return [dict(r) for r in db.get_archive(limit)]

@app.post("/archive/register")
def register_archive(payload: dict):
    aid = str(uuid.uuid4())
    db.execute(
        "INSERT INTO archive (archive_id, doc_id, forma_id, forma_version, status, bureau_marker) "
        "VALUES (?,?,?,?,?,?)",
        (aid, payload.get("doc_id",""), payload.get("forma_id",""),
         payload.get("forma_version", 1), "CURRENT", payload.get("bureau_marker","EXT")))
    return {"archive_id": aid}

@app.get("/chromatica")
def list_chromatica():
    return {"names": get_chromatica_list()}
