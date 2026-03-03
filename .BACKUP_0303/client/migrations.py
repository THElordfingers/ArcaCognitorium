#╔═════════════════════════════════════════════════════════════════════════════════════════════
#║ ⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨    
#║ ⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨
#║ ⛨⛨⛨⛨⛨⛨⛨⛨
#║ ⛨⛨⛨⛨⛨
#║ ⛨⛨⛨
#║ ⛨⛨
#║ ⛨
#║ ⛨    gpt-client/client/migrations.py  
#║ ⛨
#╚═════════════════════════════════════════════════════════════════════════════════════════════


from __future__ import annotations

import json
import os
import shutil
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple


def _now_stamp() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def _is_thread_schema(d: Dict[str, Any]) -> bool:
    return isinstance(d.get("threads"), list) and isinstance(d.get("active_thread_id"), str)


@dataclass
class MigrationResult:
    migrated_count: int
    backup_dir: Optional[str]


class ConversationMigrator:
    """
    Phase 3 migrator:
      - Old schema: {summary, messages:[{role,content,ts}]}
      - New schema: {threads:[{id,name,summary,messages:...}], active_thread_id, schema_version:2}

    Backups:
      - Copies original JSON files into: <conversations_dir>/.backups/phase3_<stamp>/
      - Only created if at least one file needs migration.
    """

    def __init__(self, conversations_dir: str) -> None:
        self.conversations_dir = conversations_dir

    def _backup_root(self) -> str:
        return os.path.join(self.conversations_dir, ".backups")

    def _make_backup_dir(self) -> str:
        d = os.path.join(self._backup_root(), f"phase3_{_now_stamp()}")
        os.makedirs(d, exist_ok=True)
        return d

    def _iter_conversation_files(self) -> List[str]:
        if not os.path.exists(self.conversations_dir):
            return []
        out: List[str] = []
        for name in os.listdir(self.conversations_dir):
            # Only top-level JSON files; ignore .backups/ etc (no recursion)
            if not name.endswith(".json"):
                continue
            out.append(os.path.join(self.conversations_dir, name))
        return out

    def _load_json(self, path: str) -> Optional[Dict[str, Any]]:
        try:
            with open(path, "r", encoding="utf-8") as f:
                d = json.load(f)
            return d if isinstance(d, dict) else None
        except Exception:
            return None

    def _save_json(self, path: str, d: Dict[str, Any]) -> None:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(d, f, ensure_ascii=False, indent=2)

    def _migrate_dict(self, d: Dict[str, Any]) -> Dict[str, Any]:
        # If already migrated, return unchanged
        if _is_thread_schema(d):
            return d

        # Minimal safe mapping
        conv_id = d.get("id", "")
        title = d.get("title", "")
        created_at = d.get("created_at", "")
        updated_at = d.get("updated_at", "")
        summary = d.get("summary", "")
        messages = d.get("messages", []) or []
        if not isinstance(messages, list):
            messages = []

        # New schema: main thread holds old summary + messages
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        migrated = {
            "schema_version": 2,
            "id": conv_id,
            "title": title,
            "created_at": created_at,
            "updated_at": updated_at or now,
            "active_thread_id": "main",
            "threads": [
                {
                    "id": "main",
                    "name": "main",
                    "created_at": created_at or now,
                    "updated_at": updated_at or now,
                    "summary": summary or "",
                    "messages": messages,
                }
            ],
        }
        return migrated

    def migrate_all_if_needed(self) -> MigrationResult:
        files = self._iter_conversation_files()
        if not files:
            return MigrationResult(migrated_count=0, backup_dir=None)

        need: List[Tuple[str, Dict[str, Any]]] = []
        for path in files:
            d = self._load_json(path)
            if not d:
                continue
            if not _is_thread_schema(d):
                need.append((path, d))

        if not need:
            return MigrationResult(migrated_count=0, backup_dir=None)

        backup_dir = self._make_backup_dir()

        migrated_count = 0
        for path, original in need:
            # backup first
            try:
                shutil.copy2(path, os.path.join(backup_dir, os.path.basename(path)))
            except Exception:
                # If backup fails, do not migrate this file.
                continue

            migrated = self._migrate_dict(original)
            try:
                self._save_json(path, migrated)
                migrated_count += 1
            except Exception:
                # Restore from backup if save failed
                try:
                    shutil.copy2(
                        os.path.join(backup_dir, os.path.basename(path)),
                        path,
                    )
                except Exception:
                    pass

        return MigrationResult(migrated_count=migrated_count, backup_dir=backup_dir)
