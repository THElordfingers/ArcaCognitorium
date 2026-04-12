# GNOSIUM EXANIMA — dux.tome.md
## Overseer of the Unbreathing Tower
*Arca Cognitorium · Exocognii Suite · v1.0.0*

---

## 1. Overview & Core Architecture

GNOSIUM EXANIMA is a standalone PyQt6 desktop application for
conversing with Tower entities drawn from the ENTITEX vault. It runs
independently of the Tower: it loads entity packages, assembles
system prompts, dispatches them to a single ClaudeBox instance, and
renders streaming responses into a dark, gold-accented chat surface.

It supports two conversation modes. CHAMBER mode drops multiple
entities into one composite prompt and lets personality-driven
self-selection decide who speaks; a single ClaudeBox call produces
whatever responses are warranted. SOLO mode isolates one entity in
its own thread. Switching modes, toggling active entities, or
swapping sessions all destroy and rebuild the ClaudeBox with a fresh
system prompt and reloaded history.

╭─────────────────────┬─────────────────────────────────────────────╮
│  Component          │  Responsibility                              │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│  config.py          │  Configuus bridge + gnosium.* overrides      │
│  constants.py       │  ModusArcanus palette, geometry, sentinels   │
│  entity/            │  Vault scan + EntityPackage normaliser        │
│  prompt/            │  Composite + Solo prompt assembly, tokens     │
│  claudebox_manager/ │  ClaudeBox lifecycle + distillation           │
│  session/           │  SQLite store + SessionManager                │
│  connectivity/      │  NUNTIUS, Cognosis, Mundana bridges           │
│  ui/                │  PyQt6 widgets + MainWindow orchestration     │
│  app.py             │  QApplication boot                            │
╰─────────────────────┴─────────────────────────────────────────────╯

## 2. Tech Stack

╭───────────────┬──────────┬────────────────────────────────────────╮
│  Tool         │  Version │  Justification                         │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│  Python       │  3.11    │  Suite-wide baseline                   │
│  PyQt6        │  ≥6.6    │  Exocognii GUI convention              │
│  ClaudeBox    │  0.1.x   │  Canonical API engine at arca root     │
│  SQLite       │  stdlib  │  Single-file session persistence       │
│  PyYAML       │  ≥6.0    │  Legacy Entitex package loader         │
│  Pillow       │  ≥10     │  Portrait format fallbacks             │
│  requests     │  ≥2.31   │  Cognosis HTTP calls                   │
╰───────────────┴──────────┴────────────────────────────────────────╯

## 3. Directory, File Tree & DB Schema

```
Exocognii/GnosiumExanima/
├── __init__.py
├── __main__.py
├── app.py
├── config.py
├── constants.py
├── dependencies.sh
├── requirements.txt
├── launch_gnosium.sh
├── GnosiumExanima.desktop
├── entity/
│   ├── __init__.py
│   ├── models.py            (EntityPackage dataclass)
│   ├── vault_scanner.py     (scan_vault + dual-format loaders)
│   └── portrait.py          (48x48 thumbnail cache)
├── prompt/
│   ├── __init__.py
│   ├── composite.py         (build_chamber_prompt, build_solo_prompt)
│   ├── tokens.py            (estimate_tokens)
│   └── tower_memory.py      (read_tower_memory)
├── claudebox_manager/
│   ├── __init__.py
│   ├── box_manager.py       (ClaudeBoxManager lifecycle + streaming)
│   └── distiller.py         (Distiller — lightweight compression call)
├── session/
│   ├── __init__.py
│   ├── store.py             (SessionStore — SQLite)
│   └── manager.py           (SessionManager — lifecycle + auto-title)
├── connectivity/
│   ├── __init__.py
│   ├── nuntius_emit.py      (emit_event — fire-and-forget)
│   ├── cognosis.py          (CognosisClient — on-demand GETs)
│   └── mundana.py           (MundanaWatcher — ~/.arca/mundana_state.json)
├── ui/
│   ├── __init__.py
│   ├── main_window.py       (MainWindow — orchestration)
│   ├── entity_panel.py      (EntityPanel + rows)
│   ├── conversation_view.py (ConversationView + bubbles)
│   ├── input_bar.py         (InputBar)
│   ├── status_strip.py      (StatusStrip)
│   ├── session_dialog.py    (SessionDialog)
│   └── token_warning_bar.py (TokenWarningBar)
├── storage/
│   ├── gnosium.db           (created on first boot)
│   └── window_state.json    (geometry + last mode)
├── Referentia/
│   └── GnosiumExanima_dux_tome.md
└── tests/
    ├── test_vault_scanner.py
    ├── test_store.py
    ├── test_session_manager.py
    ├── test_composite_prompt.py
    └── test_integration.py
```

**SQLite schema** (lives in `session/store.py`):

```sql
CREATE TABLE IF NOT EXISTS sessions (
    id              TEXT PRIMARY KEY,
    mode            TEXT NOT NULL,
    title           TEXT,
    created_at      TEXT NOT NULL,
    updated_at      TEXT NOT NULL,
    active_entities TEXT NOT NULL,
    is_current      INTEGER NOT NULL DEFAULT 0
);
CREATE INDEX IF NOT EXISTS ix_sessions_mode_current
    ON sessions(mode, is_current);

CREATE TABLE IF NOT EXISTS messages (
    id          TEXT PRIMARY KEY,
    session_id  TEXT NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
    role        TEXT NOT NULL,
    entity_id   TEXT,
    content     TEXT NOT NULL,
    timestamp   TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS ix_messages_session
    ON messages(session_id, timestamp);

CREATE TABLE IF NOT EXISTS distillations (
    id               TEXT PRIMARY KEY,
    session_id       TEXT NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
    summary          TEXT NOT NULL,
    from_message_id  TEXT NOT NULL,
    to_message_id    TEXT NOT NULL,
    created_at       TEXT NOT NULL,
    token_estimate   INTEGER
);
CREATE INDEX IF NOT EXISTS ix_distillations_session
    ON distillations(session_id, created_at);

CREATE TABLE IF NOT EXISTS entity_state (
    entity_id       TEXT PRIMARY KEY,
    last_loaded_at  TEXT,
    notes           TEXT
);
```

## 4. Module Breakdown

╭─────────────────────┬──────────────────────┬─────────────────┬────────────────┬────────────────────────╮
│  Module             │  Responsibility      │  Inputs         │  Outputs       │  Depends on            │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│  config             │  Paths, thresholds   │  config.json    │  typed props   │  Praesidium.configuus   │
│  entity.vault       │  Scan vault          │  vault dirs     │  EntityPackage │  pyyaml (opt)          │
│  entity.models      │  EP dataclass        │  —              │  —             │  —                     │
│  entity.portrait    │  Thumbnail cache     │  portrait path  │  QPixmap       │  PyQt6                 │
│  prompt.composite   │  Build prompts       │  entities, ctx  │  str           │  prompt.tower_memory   │
│  prompt.tokens      │  Rough token est     │  str            │  int           │  —                     │
│  prompt.tower_mem   │  Read-only seed      │  memory.json    │  str or None   │  —                     │
│  claudebox.box_mgr  │  CB lifecycle        │  prompt+history │  stream events │  claudebox             │
│  claudebox.distil   │  Compression call    │  msg list       │  summary text  │  claudebox             │
│  session.store      │  SQLite I/O          │  CRUD calls     │  rows          │  stdlib sqlite3        │
│  session.manager    │  Lifecycle rules     │  store          │  rows          │  session.store         │
│  connectivity.*     │  Ext bridges         │  config URLs    │  events/data   │  requests, PyQt6       │
│  ui.*               │  Widgets             │  signals        │  Qt widgets    │  PyQt6, model layer    │
╰─────────────────────┴──────────────────────┴─────────────────┴────────────────┴────────────────────────╯

## 5. ASCII UI Wireframe

**Chamber mode**

```
┌─ Session  View  Cognosis  About ─────────────────────────────────┐
├─────────────┬─────────────────────────────────────────────────────┤
│   CHAMBER   │                                                      │
│             │                                   ┌────────────────┐ │
│ [Chamber|S] │                                   │ Wizard text...  │ │
│             │                                   └────────────────┘ │
│ ┌───┐       │ ┌────────────────────────────────────┐                │
│ │AA │Name ☑ │ │[The Contrarian] body text here...   │                │
│ └───┘       │ │[The Socratic] additional body...    │                │
│ ┌───┐       │ └────────────────────────────────────┘                │
│ │BB │Name ☑ │                                                       │
│ └───┘       │                                   ┌────────────────┐ │
│ ┌───┐       │                                   │ Next wizard..   │ │
│ │CC │Name ☐ │                                   └────────────────┘ │
│ └───┘       │                                                       │
│             │                                                       │
│  [~1600 tk] ├─────────────────────────────────────────────────────┤
│             │  [Text input                               ] [Send]  │
├─────────────┴─────────────────────────────────────────────────────┤
│ Mundana: pal=void int=0.47 · Services: ok · Tokens: 1612          │
└────────────────────────────────────────────────────────────────────┘

Legend:
  ☑  = active entity                 AA = portrait thumbnail
  gold border on portrait = active   right-aligned = wizard
  [~1600 tk] = token warning bar     left-aligned  = entity response
```

**Solo mode**

```
┌──────────────┬──────────────────────────────────────────┐
│   SOLO       │  One entity thread — no name prefixes    │
│              │                                           │
│ [C|Solo]     │  ┌──────────────┐                        │
│              │  │ wizard text  │                        │
│ ⦿ Alpha      │  └──────────────┘                        │
│ ○ Beta       │  ┌──────────────────────┐                │
│ ○ Gamma      │  │ first-person entity  │                │
│              │  │ response             │                │
│              │  └──────────────────────┘                │
└──────────────┴──────────────────────────────────────────┘
```

## 6. Data Flow

**(a) Happy path — Chamber message**

```
Wizard types → InputBar.submitted
     ↓
MainWindow._on_wizard_submit
     ↓
SessionStore.append_message(wizard)  ← row persisted first
     ↓
ConversationView.append_wizard         ← right-aligned bubble
     ↓
NUNTIUS emit_event("conversation", ...)
     ↓
ClaudeBoxManager.send(...) → send_threaded
     ↓                         (worker thread)
ClaudeBox streams tokens → _StreamBridge.token_received.emit(text)
     ↓                          (main thread — Qt signal marshalling)
ConversationView.append_streaming_token
     ↓
on_complete → _StreamBridge.stream_complete.emit(response)
     ↓
SessionStore.append_message(entity)
ConversationView.finalise_streaming_bubble
InputBar.set_enabled(True)
     ↓
maybe_distill() → QTimer.singleShot(_run_distillation)
```

**(b) Entity toggle mid-session**

```
EntityPanel checkbox flipped
     ↓
selection_changed signal → MainWindow._on_selection_changed
     ↓
SessionStore.update_session(active_entities=...)
     ↓
_rebuild_for_current_session()
     ↓
 ┌─ build_chamber_prompt(new entity list)
 │
 ├─ load_messages(session_id)   — full history
 │
 └─ ClaudeBoxManager.rebuild(prompt, history=messages)
           ↓
    teardown → new ClaudeBox → replace_history via ConversationManager
     ↓
_check_token_budget(prompt)
     ↓
TokenWarningBar.show_warning(n, count)  (if over ceiling)
```

**(c) Cognosis query failure**

```
Wizard invokes "Lore search" menu action
     ↓
CognosisClient.lore_search(term)
     ↓
requests.get → RequestException or HTTP 4xx/5xx
     ↓
CognosisError raised
     ↓
ConversationView.append_system("Lore search failed: ...")
     ↓
(conversation continues — no retry, no exception propagated)
```

## 7. Code Stubs (public surface)

```python
# entity/vault_scanner.py
def scan_vault(*roots: Path) -> VaultScanResult:
    """Union-scan multiple vault roots; dedupe by entity_id."""

# prompt/composite.py
def build_chamber_prompt(
    entities: Iterable[EntityPackage],
    *,
    mundana_context: Optional[str] = None,
    tower_memory_root: Optional[Path] = None,
) -> str: ...

def build_solo_prompt(
    entity: EntityPackage,
    *,
    tower_memory_root: Optional[Path] = None,
) -> str: ...

# claudebox_manager/box_manager.py
class ClaudeBoxManager:
    def rebuild(
        self, system_prompt: str,
        history: Optional[list[MessageRow]] = None,
    ) -> None: ...
    def send(
        self, text: str, *,
        on_token: Callable,
        on_complete: Callable,
        on_error: Callable,
    ) -> None: ...
    def teardown(self) -> None: ...

# session/store.py
class SessionStore:
    def create_session(
        self, mode: str, entity_ids: list[str],
        title: Optional[str] = None,
    ) -> SessionRow: ...
    def append_message(
        self, session_id: str, role: str, content: str,
        entity_id: Optional[str] = None,
    ) -> MessageRow: ...
    def load_messages(self, session_id: str) -> list[MessageRow]: ...
    def write_distillation(
        self, session_id: str, summary: str,
        from_message_id: str, to_message_id: str,
        token_estimate: Optional[int] = None,
    ) -> DistillationRow: ...

# session/manager.py
class SessionManager:
    def get_or_create_current(
        self, mode: str, active_entities: list[str],
    ) -> SessionRow: ...
    def new_session(
        self, mode: str, active_entities: list[str],
    ) -> SessionRow: ...
    def switch_to(self, session_id: str) -> Optional[SessionRow]: ...
    def delete(self, session_id: str) -> None: ...
    def apply_auto_title_if_needed(
        self, session: SessionRow, first_wizard_message: str,
    ) -> Optional[str]: ...
```

**Composite prompt builder pseudocode**

```
sections = [CHAMBER_PREAMBLE, ""]
for entity in active:
    memory = read_tower_memory(root, entity.entity_id)
    sections.append(entity.prompt_section(tower_memory=memory))
if mundana_context:
    sections += ["─── AMBIENT CONTEXT ───", mundana_context, ""]
return "\n".join(sections)
```

**ClaudeBox lifecycle pseudocode**

```
rebuild(system_prompt, history):
    teardown()                                  # drop old ref
    self._box = ClaudeBox(
        api_key=os.environ["CLAUDE_API_KEY"],
        system_prompt=system_prompt,
    )
    if history:
        msgs = [_row_to_claudebox(m) for m in history]
        self._box._conversation.replace_history(msgs, session_id=SESSION_ID)
```

## 8. Error Handling

╭─────────────────────────┬──────────────────────┬────────────────────────────╮
│  Error                  │  Cause               │  Strategy                   │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│  Empty vault            │  No packages found   │  show empty state, disable  │
│                         │                      │  input bar, leave UI live   │
│  Malformed package      │  Missing role/traits │  skip + log to stderr       │
│  ClaudeBox import fail  │  claudebox missing   │  show fatal message in conv │
│  Stream failure mid-run │  Network/API error   │  preserve partial tokens,   │
│                         │                      │  persist as [partial], show │
│                         │                      │  system message, re-enable  │
│  SQLite write failure   │  Disk / perms        │  propagate; next send will  │
│                         │                      │  still function in-memory   │
│  NUNTIUS unavailable    │  Daemon down         │  silent stderr log only     │
│  Mundana file missing   │  Daemon not writing  │  status strip: disconnected │
│  Cognosis 4xx/5xx       │  Service down/error  │  inline system message      │
│  Token budget exceeded  │  Too many entities   │  yellow warning bar, do     │
│                         │                      │  NOT block sending          │
╰─────────────────────────┴──────────────────────┴────────────────────────────╯

## 9. Setup & Testing

**requirements.txt**

```
PyQt6>=6.6.0
PyYAML>=6.0
Pillow>=10.0.0
requests>=2.31.0
```

**Install**

```bash
cd ~/ArcaCognitorium
bash Exocognii/GnosiumExanima/dependencies.sh
```

**Run**

```bash
export CLAUDE_API_KEY=sk-...
bash Exocognii/GnosiumExanima/launch_gnosium.sh
# OR
source venv-GNOSIUM/bin/activate
PYTHONPATH=. python3 -m Exocognii.GnosiumExanima
```

**Tests**

```bash
PYTHONPATH=. python3 -m pytest Exocognii/GnosiumExanima/tests/ -v
```

Test coverage: vault scanner (JSON + YAML + malformed + empty +
duplicates), session store (CRUD + cascade + per-mode is_current),
session manager (auto-title + entity roster updates), composite
prompt (chamber + solo + mundana context + empty list), and an
integration test that runs a full message → stream → persist → reload
cycle with a monkeypatched ClaudeBox.

## 10. Packaging

**launch_gnosium.sh** (verbatim)

```bash
#!/usr/bin/env bash
set -euo pipefail
ARCA="${HOME}/ArcaCognitorium"
cd "${ARCA}"
source "${ARCA}/venv-GNOSIUM/bin/activate"
PYTHONPATH="${ARCA}" python3 -m Exocognii.GnosiumExanima "$@"
```

**GnosiumExanima.desktop** (verbatim)

```ini
[Desktop Entry]
Version=1.0
Type=Application
Name=Gnosium Exanima
GenericName=Tower Entity Overseer
Comment=Converse with Tower entities — Chamber and Solo modes
Exec=/home/lordfingers/ArcaCognitorium/Exocognii/GnosiumExanima/launch_gnosium.sh
Icon=gnosium_exanima
Terminal=false
Categories=Utility;Development;
StartupWMClass=GnosiumExanima
```

Install:

```bash
cp Exocognii/GnosiumExanima/GnosiumExanima.desktop \
   ~/.local/share/applications/
cp <your-icon>.png ~/.local/share/icons/gnosium_exanima.png
```

## 11. Extensibility — v2 Wishlist

╭──────────────────────────┬────────────────────────┬───────────────────────────╮
│  Feature                 │  User value            │  Implementation approach  │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│  Celestial Resolver      │  Entities react to     │  Extend MundanaWatcher to │
│  integration             │  sky/dasha/disruptive  │  subscribe to the         │
│                          │  state in real time    │  Celestial Resolver's     │
│                          │  via prompt injection  │  JSON feed; on change,    │
│                          │                        │  set _mundana_dirty and   │
│                          │                        │  call _rebuild next send  │
│  Fragment Protocol       │  Entities cite lore    │  On wizard_submit, scan   │
│                          │  fragments from        │  message for fragment ids │
│                          │  Exvacua Loricum       │  (:frag/xyz:) and inline  │
│                          │  before responding     │  lore_search results into │
│                          │                        │  the next prompt rebuild  │
│  Distillation            │  Long sessions stay    │  Replace _maybe_distill   │
│  auto-trigger            │  coherent without      │  polling with a store     │
│                          │  manual intervention   │  trigger that calls       │
│                          │                        │  Distiller off-main       │
│                          │                        │  whenever count crosses   │
│                          │                        │  threshold                │
│  celestial.yaml entity   │  Entities know their   │  Add celestial.yaml to    │
│  awareness               │  position in the       │  vault loader; inject     │
│                          │  celestial chain       │  "You are aligned with X" │
│                          │  and reference it      │  into prompt_section()    │
│  Session export          │  Archivable transcript │  New menu action that     │
│                          │  for later review      │  dumps messages +         │
│                          │                        │  distillations to         │
│                          │                        │  Markdown via a simple    │
│                          │                        │  template                 │
╰──────────────────────────┴────────────────────────┴───────────────────────────╯

---

*End of GNOSIUM EXANIMA dux.tome.md — v1.0.0*
