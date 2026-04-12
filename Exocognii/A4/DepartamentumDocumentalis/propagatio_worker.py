# Departamentum Documentalis · propagatio_worker.py · v1.2
import uuid, json
from PyQt6.QtCore import QRunnable, QObject, pyqtSignal, pyqtSlot
import DepartamentumDocumentalis.db as db
from DepartamentumDocumentalis.nuntius_emit import emit_event
from DepartamentumDocumentalis.scriptura_parser import parse
from DepartamentumDocumentalis.md_renderer import render as md_render

class PropagatiSignals(QObject):
    progress  = pyqtSignal(int, int)
    item_done = pyqtSignal(str, bool)
    finished  = pyqtSignal(int, int)

class PropagatioBatchWorker(QRunnable):
    def __init__(self):
        super().__init__()
        self.signals = PropagatiSignals()

    @pyqtSlot()
    def run(self):
        queue = db.get_propagatio_queue("PENDING")
        total = len(queue)
        ok_count = fail_count = 0
        for i, item in enumerate(queue):
            ok = migrate_document(item["queue_id"])
            if ok: ok_count += 1
            else:  fail_count += 1
            self.signals.item_done.emit(item["queue_id"], ok)
            self.signals.progress.emit(i + 1, total)
        self.signals.finished.emit(ok_count, fail_count)

def migrate_document(queue_id: str) -> bool:
    try:
        item    = db.fetch_one("SELECT * FROM propagatio_queue WHERE queue_id = ?", (queue_id,))
        if not item: return False
        archive = db.fetch_one("SELECT * FROM archive WHERE archive_id = ?", (item["archive_id"],))
        doc     = db.fetch_one("SELECT * FROM documents WHERE doc_id = ?", (archive["doc_id"],))
        new_forma  = db.get_forma(item["target_forma_id"])
        new_fields = db.get_forma_fields(item["target_forma_id"])

        pr = parse(doc["source_text"])
        if not pr.ok:
            _fail(queue_id, f"Parse errors: {pr.errors}")
            return False

        fixed = {f["name"]: f["fixed_value"] for f in new_fields
                 if f["field_type"] == "FIXED" and f["fixed_value"]}
        known   = {f["name"] for f in new_fields}
        orphaned = {k: pr.ast.fields[k] for k in set(pr.ast.fields) - known}

        db.execute("UPDATE archive SET status = 'VERSIO PRIOR' WHERE archive_id = ?",
                   (item["archive_id"],))

        new_id = str(uuid.uuid4())
        db.execute(
            "INSERT INTO archive (archive_id, doc_id, forma_id, forma_version, status, "
            "bureau_marker, chromaticum_name, orphaned_corpus, emitted_at) "
            "VALUES (?,?,?,?,'CURRENT','III-DD',?,?,datetime('now'))",
            (new_id, archive["doc_id"], new_forma["forma_id"], new_forma["version"],
             new_forma["chromaticum_name"],
             json.dumps(orphaned) if orphaned else None))

        db.execute(
            "UPDATE propagatio_queue SET status='DONE', processed_at=datetime('now') "
            "WHERE queue_id = ?", (queue_id,))

        emit_event("propagatio_migration", {
            "queue_id": queue_id, "new_archive_id": new_id})
        return True
    except Exception as e:
        _fail(queue_id, str(e))
        return False

def _fail(queue_id, msg):
    db.execute(
        "UPDATE propagatio_queue SET status='ERROR', error_msg=?, "
        "processed_at=datetime('now') WHERE queue_id = ?", (msg, queue_id))
