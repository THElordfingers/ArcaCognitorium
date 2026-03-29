# CLAUDEBOX — WIRING REFERENCE
### Exocognii Suite · Import Pattern & Init

---

## The Rule

`sys.path` needs the repo root — `ArcaCognitorium/` — not the `claudebox/`
subdirectory. Python resolves `from claudebox import ClaudeBox` by finding
the `claudebox/` package beneath whatever is on the path.

---

## The Block

Drop this at the top of any file that imports ClaudeBox, before the import.
If `sys`, `json`, or `pathlib` are already imported in the file, fold the
path block in — do not duplicate the imports.

```python
import sys
import json
from pathlib import Path

_config_file = Path.home() / '.arca' / 'config.json'
_repo_path   = str(Path.home() / 'ArcaCognitorium')  # fallback
try:
    with _config_file.open() as _f:
        _arca_cfg = json.load(_f)
    _repo_path = _arca_cfg.get('arca_repo_path', _repo_path)
except (OSError, json.JSONDecodeError):
    pass
if _repo_path not in sys.path:
    sys.path.insert(0, _repo_path)

from claudebox import ClaudeBox
```

---

## Init

```python
ClaudeBox(
    system_prompt = ...,
    api_key       = os.environ.get('CLAUDE_API_KEY'),
)
```

API key is always `CLAUDE_API_KEY` — never `ANTHROPIC_API_KEY`.

---

## Notes

╭─────────────────────────────────────────────────────────────╮
│  Config source  : ~/.arca/config.json                       │
│  Key            : arca_repo_path                            │
│  Fallback       : ~/ArcaCognitorium                         │
│  Package lives  : ArcaCognitorium/claudebox/__init__.py     │
│  Never copy     : claudebox/ into tool directories          │
╰─────────────────────────────────────────────────────────────╯
