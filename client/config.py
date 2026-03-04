#╔══════════════════════════════════════════════════════════════════════════════   
#║ ⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨    
#║ ⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨
#║ ⛨⛨⛨⛨⛨⛨⛨⛨     
#║ ⛨⛨⛨⛨⛨
#║ ⛨⛨⛨
#║ ⛨⛨       
#║ ⛨        
#║ ⛨    gpt-client/client/config.py
#║ ⛨
#╚══════════════════════════════════════════════════════════


from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict
import os
import yaml


def _deep_merge(a: Dict[str, Any], b: Dict[str, Any]) -> Dict[str, Any]:
    out = dict(a)
    for k, v in b.items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = _deep_merge(out[k], v)
        else:
            out[k] = v
    return out


@dataclass(frozen=True)
class Namespace:
    _data: Dict[str, Any]

    def __getattr__(self, item: str) -> Any:
        if item not in self._data:
            raise AttributeError(item)
        v = self._data[item]
        if isinstance(v, dict):
            return Namespace(v)
        return v

    def get(self, key: str, default: Any = None) -> Any:
        return self._data.get(key, default)

    def as_dict(self) -> Dict[str, Any]:
        return self._data


@dataclass(frozen=True)
class AppConfig:
    raw: Dict[str, Any]
    app: Namespace
    api: Namespace
    ui: Namespace
    keys: Namespace
    models: Namespace
    routing: Namespace
    memory: Namespace
    storage: Namespace
    logging: Namespace
    reflection: Namespace

    @staticmethod
    def load(path: str) -> "AppConfig":
        with open(path, "r", encoding="utf-8") as f:
            user_cfg = yaml.safe_load(f) or {}

        defaults = {
            "api": {"api_key": None, "timeout_seconds": 120},
            "logging": {"enabled": True, "log_user_messages": True, "log_assistant_messages": True},
            "keys": {
                "submit_message": "f2",
                # Konsole-safe focus keys (avoid ctrl/alt + digits).
                "focus_left": "f6",
                "focus_middle": "f7",
                "focus_right": "f8",
                "copy_last": "ctrl+y",
            },
        }
        merged = _deep_merge(defaults, user_cfg)

        storage = merged.get("storage", {})
        conv_dir = storage.get("conversations_dir", "storage/conversations")
        os.makedirs(conv_dir, exist_ok=True)
        os.makedirs(os.path.dirname(storage.get("immutable_log_path", "storage/logs/immutable.jsonl")), exist_ok=True)
        os.makedirs(os.path.dirname(storage.get("reflection_log_path", "storage/logs/reflections.jsonl")), exist_ok=True)
        os.makedirs(os.path.dirname(storage.get("vectors_path", "storage/vectors/vectors.pkl")), exist_ok=True)

        return AppConfig(
            raw=merged,
            app=Namespace(merged.get("app", {})),
            api=Namespace(merged.get("api", {})),
            ui=Namespace(merged.get("ui", {})),
            keys=Namespace(merged.get("keys", {})),
            models=Namespace(merged.get("models", {})),
            routing=Namespace(merged.get("routing", {})),
            memory=Namespace(merged.get("memory", {})),
            storage=Namespace(merged.get("storage", {})),
            logging=Namespace(merged.get("logging", {})),
            reflection=Namespace(merged.get("reflection", {})),
        )
