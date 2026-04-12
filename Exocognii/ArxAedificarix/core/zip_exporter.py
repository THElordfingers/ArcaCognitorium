#!/usr/bin/env python3
"""
🮈🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃▍
🮈      ARX AEDIFICARIX                                                             ▍
🭅▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃🭐
"""
# ╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌
# ⯨                                                                         ⯩
# ⯨   𝐀𝐍𝐍𝐔𝐒 🟌 ＭＭＸＸＶＩ                           core/zip_exporter.py   ⯩
# ⯨                                                                         ⯩
# ╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌

import json
import logging
import zipfile
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from core.session_store import OutputFile, SessionStore

logger = logging.getLogger("arx.zip_exporter")


class ExportError(Exception):
    """Raised when export cannot proceed. Caller surfaces to UI."""


@dataclass
class ExportManifest:
    version: str
    conversation_id: str
    conversation_title: str
    project_id: str | None
    generated_at: str
    files: list[dict]


class ZipExporter:
    """
    Assembles a zip package from the output_files table for a conversation.

    The destination path is always provided by the caller (from QFileDialog).
    No silent writes. No assumed output directories.

    Package contents:
        - One file per OutputFile row, written at the root of the zip.
        - manifest.json describing the package.

    After a successful write, all included files are marked 'exported'
    in SQLite. The zip is written atomically — dest_path is only created
    on success; partial writes do not leave a corrupt file.
    """

    def __init__(self, store: SessionStore) -> None:
        self._store = store

    # -----------------------------------------------------------------------
    # Public API
    # -----------------------------------------------------------------------

    def assemble_package(
        self,
        conversation_id: str,
        dest_path: Path,
    ) -> Path:
        """
        Write all output_files for conversation to a zip at dest_path.
        Includes manifest.json. Marks files as exported in SQLite.

        Parameters
        ----------
        conversation_id : str
        dest_path       : Full path to the output .zip file. Must be writable.
                          Parent directory must exist.

        Returns
        -------
        Path — the dest_path written, confirmed present.

        Raises
        ------
        ExportError : No files to export, or write permission denied.
        """
        conversation = self._store.get_conversation(conversation_id)
        if conversation is None:
            raise ExportError(
                f"ZipExporter: conversation {conversation_id!r} not found."
            )

        files = self._store.get_output_files(conversation_id)
        if not files:
            raise ExportError(
                "ZipExporter: no output files to package. "
                "The Builder has not yet produced any files in this conversation."
            )

        manifest = self._build_manifest(conversation, files)

        # Write to a temp name in the same directory, then rename — ensures
        # dest_path only appears on successful completion.
        tmp_path = dest_path.with_suffix(".tmp.zip")
        try:
            self._write_zip(tmp_path, files, manifest)
            tmp_path.rename(dest_path)
        except OSError as exc:
            # Clean up temp file if it exists.
            try:
                tmp_path.unlink(missing_ok=True)
            except OSError:
                pass
            raise ExportError(
                f"ZipExporter: write failed at {dest_path}: {exc}"
            ) from exc

        # Mark exported in SQLite — non-fatal if this fails; the zip exists.
        try:
            self._store.mark_files_exported([f.id for f in files])
        except Exception as exc:
            logger.warning(
                "ZipExporter: SQLite mark-exported failed (zip written OK): %s",
                exc,
            )

        logger.info(
            "ZipExporter: package written to %s (%d files)",
            dest_path, len(files),
        )
        return dest_path

    def can_export(self, conversation_id: str) -> bool:
        """
        Return True if there are pending output files to export.
        Used by MainWindow to enable/disable the Export button.
        """
        files = self._store.get_output_files(conversation_id)
        return any(f.export_status == "pending" for f in files)

    # -----------------------------------------------------------------------
    # Private helpers
    # -----------------------------------------------------------------------

    def _build_manifest(
        self,
        conversation,
        files: list[OutputFile],
    ) -> ExportManifest:
        return ExportManifest(
            version="1.0",
            conversation_id=conversation.id,
            conversation_title=conversation.title,
            project_id=conversation.project_id,
            generated_at=datetime.now(timezone.utc).isoformat(),
            files=[
                {
                    "filename": f.filename,
                    "language": f.language,
                    "description": f.description,
                    "size_bytes": len(f.content.encode("utf-8")),
                }
                for f in files
            ],
        )

    @staticmethod
    def _write_zip(
        path: Path,
        files: list[OutputFile],
        manifest: ExportManifest,
    ) -> None:
        with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as zf:
            for f in files:
                zf.writestr(f.filename, f.content)
            zf.writestr(
                "manifest.json",
                json.dumps(
                    {
                        "version": manifest.version,
                        "conversation_id": manifest.conversation_id,
                        "conversation_title": manifest.conversation_title,
                        "project_id": manifest.project_id,
                        "generated_at": manifest.generated_at,
                        "files": manifest.files,
                    },
                    indent=2,
                ),
            )
