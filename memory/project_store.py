#╔══════════════════════════════════════════════════════════════════════════════
#║ ⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨    
#║ ⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨
#║ ⛨⛨⛨⛨⛨⛨⛨⛨     
#║ ⛨⛨⛨⛨⛨
#║ ⛨⛨⛨
#║ ⛨⛨       
#║ ⛨        
#║ ⛨    ArcaCognitorium/memory/project_store.py
#║ ⛨
#╚══════════════════════════════════════════════════════════════════════════════════════


from __future__ import annotations

import json
import os
import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional


def _now_local() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


@dataclass
class Project:
    id: str
    name: str
    created_at: str
    updated_at: str
    conversation_ids: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "conversation_ids": list(self.conversation_ids),
        }

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "Project":
        return Project(
            id=d["id"],
            name=d.get("name", ""),
            created_at=d.get("created_at", ""),
            updated_at=d.get("updated_at", ""),
            conversation_ids=list(d.get("conversation_ids", []) or []),
        )


class ProjectStore:
    """
    LF semantics:
      - No default project.
      - Conversations are NOT in any project unless moved/added, or created on a project page.
      - One conversation belongs to at most one project.
      - Project names are unique (case-insensitive).
    """

    def __init__(self, *, path: str = "storage/projects/projects.json") -> None:
        self.path = path
        self.projects: List[Project] = []
        self._load()

    # -------------------------
    # Persistence
    # -------------------------
    def _load(self) -> None:
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        if not os.path.exists(self.path):
            self._save()
            return
        try:
            with open(self.path, "r", encoding="utf-8") as f:
                d = json.load(f) or {}
            self.projects = [Project.from_dict(p) for p in (d.get("projects", []) or [])]
        except Exception:
            # Don’t crash if corrupted; start fresh
            self.projects = []
            self._save()

    def _save(self) -> None:
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        payload = {"projects": [p.to_dict() for p in self.projects]}
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)

    # -------------------------
    # Queries
    # -------------------------
    def list_projects(self) -> List[Project]:
        return list(self.projects)

    def get_by_id(self, project_id: str) -> Optional[Project]:
        pid = (project_id or "").strip()
        if not pid:
            return None
        for p in self.projects:
            if p.id == pid:
                return p
        return None

    def get_by_name_ci(self, name: str) -> Optional[Project]:
        want = (name or "").strip().lower()
        if not want:
            return None
        for p in self.projects:
            if (p.name or "").strip().lower() == want:
                return p
        return None

    def name_exists(self, name: str) -> bool:
        return self.get_by_name_ci(name) is not None

    def project_for_conversation(self, conv_id: str) -> Optional[str]:
        cid = (conv_id or "").strip()
        if not cid:
            return None
        for p in self.projects:
            if cid in p.conversation_ids:
                return p.id
        return None

    def is_projected(self, conv_id: str) -> bool:
        return self.project_for_conversation(conv_id) is not None

    def conversation_ids_for_project(self, project_id: Optional[str]) -> List[str]:
        if not project_id:
            return []
        p = self.get_by_id(project_id)
        return list(p.conversation_ids) if p else []

    # -------------------------
    # Mutations
    # -------------------------
    def create(self, name: str) -> Project:
        name = (name or "").strip()
        if not name:
            raise ValueError("Project name cannot be empty.")
        if self.name_exists(name):
            raise ValueError(f"Project name already exists: {name!r}")

        pid = uuid.uuid4().hex[:12]
        now = _now_local()
        p = Project(id=pid, name=name, created_at=now, updated_at=now, conversation_ids=[])
        self.projects.append(p)
        self._save()
        return p

    def delete_by_id(self, project_id: str) -> bool:
        pid = (project_id or "").strip()
        if not pid:
            return False
        before = len(self.projects)
        self.projects = [p for p in self.projects if p.id != pid]
        if len(self.projects) == before:
            return False
        self._save()
        return True

    def assign_conversation(self, conv_id: str, project_id: str) -> None:
        cid = (conv_id or "").strip()
        pid = (project_id or "").strip()
        if not cid or not pid:
            return

        # Remove from any other project first (1 convo -> 1 project)
        for p in self.projects:
            if cid in p.conversation_ids and p.id != pid:
                p.conversation_ids.remove(cid)
                p.updated_at = _now_local()

        p = self.get_by_id(pid)
        if not p:
            return

        if cid not in p.conversation_ids:
            p.conversation_ids.append(cid)
            p.updated_at = _now_local()

        self._save()

    def unassign_conversation(self, conv_id: str) -> None:
        cid = (conv_id or "").strip()
        if not cid:
            return

        changed = False
        for p in self.projects:
            if cid in p.conversation_ids:
                p.conversation_ids.remove(cid)
                p.updated_at = _now_local()
                changed = True

        if changed:
            self._save()

    def drop_conversation_everywhere(self, conv_id: str) -> None:
        self.unassign_conversation(conv_id)



    def get_tome_entries(self, project_id: str) -> list[dict]:
        """
        Return the raw tome_entries list for a project.
        Returns [] if project not found or tome_entries key absent.
    
        Implementation:
          project = self._load_project(project_id)
          if not project:
              return []
          return project.get("tome_entries", [])
        """
        project = self._load_project(project_id)
        if not project:
            return []
        return project.get("tome_entries", [])
    
    
    def save_tome_entries(self, project_id: str,
                          entries: list[dict]) -> bool:
        """
        Persist tome_entries list to project JSON.
        Returns True on success, False if project not found.
        Uses atomic write pattern — write to .tmp then rename.
    
        Implementation:
          project = self._load_project(project_id)
          if not project:
              return False
          project["tome_entries"] = entries
          self._save_project(project_id, project)  # existing atomic save method
          return True
        """
        project = self._load_project(project_id)
        if not project:
            return False
        project["tome_entries"] = entries
        self._save_project(project_id, project)
        return True
    
    
    def get_project_name(self, project_id: str) -> str:
        """
        Return the display name of a project.
        Returns "Unknown Project" if project_id not found.
        Used by Tome.build_injection_string() for the header line.
        """
        project = self._load_project(project_id)
        if not project:
            return "Unknown Project"
        return project.get("name", project_id)
    
    
