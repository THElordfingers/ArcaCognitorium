# THE DOLIUM v2
### IdeaForge Build Document · PyQt6 · Modus Arcanus · 2026

---

## Idea Brief

| Field | Value |
|---|---|
| App Name | The Dolium v2 |
| One-Line Purpose | A PyQt6 desktop ideation instrument where ideas are
 cultivated through four chambers with an ambient AI entity that watches,
 whispers, and responds as you write |
| Platform | Linux (Debian/KDE) · Python 3.11 · PyQt6 |
| Primary User | LordFingers — sole Wizard, building the Arca Cognitorium 
during personal time |
| Core Loop | Open → select/create idea → write in living fields → entity 
whispers observations → refine → advance through chambers → declare and export |
| Framework | PyQt6 — full desktop, resizable panes, real text editing, 
streaming tokens |
| AI Integration | ClaudeBox with `thread_mode: threaded` — `on_token` 
signals stream text into the UI; QTimer debounce triggers ambient commentary 
on field changes |
| Status | v2 — complete redesign of the existing Textual-based Dolium |

---

## 1. Overview & Core Architecture

The Dolium v2 is a PyQt6 desktop application implementing a four-chamber 
ideation pipeline. It replaces the previous Textual-based version, resolving its
 core failure: the workspace felt like a form and the entity felt absent. The 
 redesign centres on two architectural principles — **living text surfaces** and
  **ambient entity presence**.

A living text surface is a QTextEdit that the entity watches. When the Wizard 
stops typing (1.5 second debounce), the entity generates a brief observation — 
not a response to a question, an unprompted whisper into the margin. It appears 
in a dedicated Whisper Panel beside the conversation area, not as a chat message. 
The Wizard did not ask for it. It arrived because the entity is present.

The pipeline logic is unchanged: four chambers, gate conditions, advancement, 
culling, Declaration, export. What changes is how it feels to inhabit it.

### Component Table

| Component | Responsibility |
|---|---|
| DoliumApp (QMainWindow) | Root window. Applies global Modus Arcanus stylesheet
. Owns ClaudeBox instance and IdeaStore. Hosts the three-panel splitter. |
| PipelinePanel (QWidget) | Left panel — fixed 280px, collapsible. Chamber tree 
with idea entries, search field, quick-action buttons. |
| WorkspacePanel (QWidget) | Centre panel — dominant. Active idea fields as 
living QTextEdit surfaces. Gate bar at bottom. Field-change debounce triggers
ambient whispers. |
| ChamberPanel (QWidget) | Right panel — conversation and whisper stream.
 Two sections: Whisper Stream (ambient) and Conversation (direct). Streaming 
 tokens render word by word. |
| IdeaStore | JSON persistence. Synchronous reads/writes. In-memory cache.
 Single source of truth. |
| ClaudeBox | API wrapper. Configured with `thread_mode: threaded`. `on_token`
 callback emits Qt signal per token. Sessions keyed per idea. |
| AmbientWorker (QThread) | Debounced field-watcher. Fires after 1500ms typing 
inactivity. Calls `send_threaded` with Whisper system prompt. Emits 
`token_received(str)` and `complete()`. |
| ConversationWorker (QThread) | Handles explicit user messages. Same ClaudeBox 
session as AmbientWorker — shared history. Emits `token_received(str)` and 
`complete()`. |
| GateEngine | Pure functions. Evaluates gate conditions per chamber. Returns 
`GateResult(passed, failures)`. No UI dependency. |
| ExportEngine | Generates .wiz .docx .md .txt .json from a completed Idea.
 Subprocess for .wiz via Node.js. |

---

## 2. Tech Stack

| Tool | Version | Justification |
|---|---|---|
| Python | 3.11+ | Match AC environment. Union type hints, match statements. |

| PyQt6 | 6.6+ | Real text editing, QSplitter, QThread, Qt signals — solves 
every friction point of the Textual version. |
| ClaudeBox | local package | Custom Anthropic wrapper. `thread_mode: threaded`
 enables safe token streaming into Qt signals. |
| python-docx | latest | Clean .docx export. |
| Node.js + docx npm | 16+ / 9.x | .wiz export via subprocess. Optional — 
degrades gracefully. |
| QTimer | Qt built-in | 1500ms debounce on field changes before triggering
 ambient whisper. |

---

## 3. Annotated File Tree

```
dolium/
├── main.py                  — entry point; DoliumApp().run()
├── app.py                   — DoliumApp (QMainWindow); global style; ClaudeBox init
├── models.py                — Idea, ChamberLog, CullRecord dataclasses
├── store.py                 — IdeaStore; JSON persistence; in-memory cache
├── chambers.py              — GateEngine; pure gate functions; GateResult
├── prompts.py               — system prompts per chamber; build_user_message(); whisper prompt
├── manpages.py              — five manpage texts; injected into system prompts
├── export.py                — ExportEngine; .wiz .docx .md .txt .json
├── style.py                 — Modus Arcanus palette constants; GLOBAL_STYLE; widget factories
├── workers.py               — AmbientWorker, ConversationWorker (QThread subclasses)
├── ClaudeBox/               — local ClaudeBox package
├── ui/
│   ├── __init__.py
│   ├── main_window.py       — DoliumWindow; QSplitter; panel composition
│   ├── pipeline_panel.py    — PipelinePanel; chamber tree; idea list; search
│   ├── workspace_panel.py   — WorkspacePanel; living fields; gate bar; debounce wiring
│   ├── chamber_panel.py     — ChamberPanel; whisper stream; conversation; streaming render
│   ├── dialogs.py           — NewIdea, Advance, ReturnTo, Cull, Declaration, Export, Manpage, CullRegister
│   └── widgets.py           — ArcaneField, WhisperBubble, ConvBubble, GateBar
└── storage/
    ├── ideas.json
    ├── culled.json
    └── exports/
```

---

## 4. Module Breakdown

| Module | Responsibility · Inputs · Outputs · Dependencies |
|---|---|
| `main.py` | Entry point. QApplication init, DoliumWindow instantiation, exec(). → None → App launch → app.py, style.py |
| `app.py` | Global state: ClaudeBox instance, IdeaStore instance, active idea reference. Applies GLOBAL_STYLE. → Env vars → Running window → store.py, workers.py, ClaudeBox |
| `models.py` | Idea, ChamberLog, CullRecord dataclasses with to_dict/from_dict. → None → Typed data objects → stdlib only |
| `store.py` | IdeaStore: load, save, create, update, advance, return_to, cull, resurrect. → Path to storage/ → Idea objects → models.py |
| `chambers.py` | GateEngine: gate_1_to_2, gate_2_to_3, gate_3_to_4. Pure functions. → Idea → GateResult(passed, failures) → models.py |
| `prompts.py` | CHAMBER_1–4 system prompts. WHISPER prompt. build_user_message(idea, text). set_context(). → Idea, str → str system prompts → manpages.py |
| `manpages.py` | Five manpage texts. all_manpages_for_prompt(). → None → str → None |
| `export.py` | ExportEngine: _to_json, _to_md, _to_txt, _to_docx, _to_wiz. → Idea, output Path → Files on disk → python-docx, subprocess/Node |
| `style.py` | Modus Arcanus palette constants. GLOBAL_STYLE. arcane_button(), gold_label(), dim_label(), ArcaneTextEdit factory. → None → Qt widgets/stylesheets → PyQt6 |
| `workers.py` | AmbientWorker(QThread): debounced whisper. ConversationWorker(QThread): explicit messages. Both emit token_received(str) and complete(). → ClaudeBox, session_id, text → Qt signals → ClaudeBox, PyQt6 |
| `ui/main_window.py` | DoliumWindow: QMainWindow with QSplitter. Wires inter-panel signals. → IdeaStore, ClaudeBox → Main UI → all ui/ modules |
| `ui/pipeline_panel.py` | QTreeWidget showing chambers and ideas. Search. New/Advance/Cull buttons. Emits idea_selected(str). → IdeaStore → idea_selected signal → store.py, style.py |
| `ui/workspace_panel.py` | Chamber-gated ArcaneTextEdit fields. QTimer debounce. Gate bar. Emits field_changed and advance_requested. → Idea → signals → chambers.py, style.py, workers.py |
| `ui/chamber_panel.py` | WhisperStream and Conversation sections. Renders streaming tokens. Emits message_sent(str). → ClaudeBox session → Rendered text → workers.py, style.py |
| `ui/dialogs.py` | All modal QDialog subclasses. Each returns a result via .exec(). → Various → Dialog result → style.py |
| `ui/widgets.py` | ArcaneField, WhisperBubble, ConvBubble, GateBar. Reusable. → str, style → QWidget → style.py |

---

## 5. UI Wireframe

```
╔══════════════════════════════════════════════════════════════════════════════╗
║  ◆  THE DOLIUM                                                   [_] [□] [×] ║
╠═════════════════╦═══════════════════════════════╦════════════════════════════╣
║  PIPELINE       ║  WORKSPACE                    ║  CHAMBER                   ║
║  ─────────────  ║  ─────────────────────────    ║  ──────────────────────    ║
║  / search...    ║  ▸ I · THE FOMENTARY          ║  WHISPERS                  ║
║                 ║                               ║  ┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄      ║
║  I FOMENTARY[1] ║  TITLE ◆                      ║  ◇ The idea of a ritual    ║
║  ┗ Onboarding   ║  ┌─────────────────────────┐  ║    suggests an entry       ║
║                 ║  │ The Onboarding Ritual   │  ║    point rather than       ║
║  II CULTIVATION ║  └─────────────────────────┘  ║    a feature. What is      ║
║  — empty —      ║                               ║    the transition being    ║
║                 ║  BODY ◆                       ║    marked?                 ║
║  III VESTIBULE  ║  ┌─────────────────────────┐  ║                            ║
║  — empty —      ║  │ The onboarding ritual   │  ║  ──────────────────────    ║
║                 ║  │ is an initiation event  │  ║  CONVERSATION              ║
║  IV CODEX       ║  │ that triggers on a      │  ║  ┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄      ║
║  — empty —      ║  │ Wizard's first open...  │  ║  Wizard                    ║
║                 ║  └─────────────────────────┘  ║  what triggers this?       ║
║  [+ New Idea]   ║                               ║                            ║
║                 ║  MOTIVATION ◆                 ║  The Fomentary             ║
║                 ║  ┌─────────────────────────┐  ║  The ritual marks the      ║
║                 ║  │ A way to introduce...   │  ║  moment of first contact   ║
║                 ║  └─────────────────────────┘  ║  between Wizard and Tower  ║
║                 ║                               ║                            ║
║                 ║  ◇ 2 conditions remaining     ║  ┌──────────────────────┐  ║
║                 ║  [Advance ›] [Return] [Cull]  ║  │ speak to the chamber │  ║
║                 ║                               ║  └──────────────┬───────┘  ║
╠═════════════════╩═══════════════════════════════╩══╡ Send ├═══════╝          ║
║  Status: The Dolium attends.              Chamber I · Officina Ferment.      ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

**Legend:** ◆ = required field · ◇ = gate status indicator · Whispers appear 
unprompted in the right panel upper section as the Wizard types · Conversation
 is below the divider · QSplitter handles all resize

---

## 6. Data Flow

### Path A — Wizard types in a field (happy path)

1. Wizard types in a WorkspacePanel ArcaneTextEdit
   - QTextEdit.textChanged fires
   - WorkspacePanel._on_field_changed() updates Idea attribute in memory
   - IdeaStore.update(idea) writes ideas.json
   - GateEngine re-evaluates; GateBar updates
   - QTimer (1500ms debounce) resets on each keystroke
2. After 1500ms of inactivity, QTimer fires
   - AmbientWorker created with current field text and Idea state
   - Calls ClaudeBox.send_threaded(content, session_id, on_token, on_complete)
   - ClaudeBox runs in background thread (thread_mode: threaded)
   - Each token: on_token → AmbientWorker emits token_received(str) Qt signal
   - ChamberPanel.on_whisper_token(str) appends to WhisperStream QTextEdit
   - on_complete → AmbientWorker emits complete() → WhisperBubble sealed

### Path B — Wizard sends an explicit message

1. Wizard types in conversation input and clicks Send
2. ChamberPanel.on_send() creates ConversationWorker
3. ConversationWorker calls send_threaded on the same session as AmbientWorker
4. Tokens stream into Conversation QTextEdit via token_received signal
5. on_complete seals the bubble; turn appended to idea.conversation
6. IdeaStore.update(idea) persists the turn

### Path C — Advancement fails gate check

1. Wizard clicks Advance or presses ctrl+a
2. GateEngine.gate_N_to_M(idea) returns GateResult(passed=False, failures=[...])
3. AdvanceDialog opens showing red ✕ checklist of unmet conditions
4. Wizard dismisses; no state change

---

## 7. Code Stubs

### workers.py

```python
class AmbientWorker(QThread):
    token_received = pyqtSignal(str)
    complete = pyqtSignal()
    error = pyqtSignal(str)

    def __init__(self, box, session_id: str, content: str, system: str):
        """Fires ambient whisper. Created fresh per debounce event."""

    def run(self) -> None:
        """Calls box.send_threaded. on_token emits token_received."""


class ConversationWorker(QThread):
    token_received = pyqtSignal(str)
    complete = pyqtSignal()
    error = pyqtSignal(str)

    def __init__(self, box, session_id: str, content: str, system: str):
        """Fires explicit conversation message."""

    def run(self) -> None:
        """Calls box.send_threaded. on_token emits token_received."""
```

### ui/workspace_panel.py — debounce wiring

```python
class WorkspacePanel(QWidget):
    field_changed = pyqtSignal(str, str)          # (field_name, text)
    whisper_requested = pyqtSignal(str, str, object)  # (field, text, idea)

    def __init__(self):
        self._debounce = QTimer()
        self._debounce.setSingleShot(True)
        self._debounce.setInterval(1500)
        self._debounce.timeout.connect(self._on_debounce_fire)

    def _on_field_changed(self, field: str, text: str) -> None:
        """Called on every keystroke. Saves and resets debounce."""
        # Update idea attribute
        # Call store.update()
        # Refresh gate bar
        self._pending_field = field
        self._pending_text  = text
        self._debounce.start()  # restart resets the timer

    def _on_debounce_fire(self) -> None:
        """Fires after 1500ms silence. Emits whisper_requested."""
        self.whisper_requested.emit(
            self._pending_field, self._pending_text, self._idea
        )
```

### ui/chamber_panel.py — token streaming

```python
class ChamberPanel(QWidget):
    message_sent = pyqtSignal(str)

    def on_whisper_token(self, token: str) -> None:
        """Appends token to WhisperStream QTextEdit. Called from Qt signal."""
        cursor = self._whisper_edit.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        cursor.insertText(token)
        self._whisper_edit.setTextCursor(cursor)
        self._whisper_edit.ensureCursorVisible()

    def on_conv_token(self, token: str) -> None:
        """Appends token to Conversation QTextEdit. Same pattern."""
```

### style.py — Modus Arcanus palette and factories

```python
C_BG        = "#050507"   # Void
C_PANEL     = "#0a0a12"   # Obsidian
C_GOLD      = "#d4af37"   # Aurum
C_GOLD_DIM  = "#7a6a2a"   # Aurum Dimmus
C_GOLD_DARK = "#3a2e10"   # Aurum Nox
C_CRIMSON   = "#8b1a1a"   # Sanguis
C_TEAL      = "#1a5a5a"   # Viridis
C_TEXT      = "#c8b88a"   # Parchment
C_SUBTLE    = "#3a3528"   # Umbra
C_WHITE     = "#e8e0cc"   # Vellum

def arcane_button(text: str, accent: str = C_GOLD) -> QPushButton: ...
def gold_label(text: str, size: int = 11, bold: bool = False) -> QLabel: ...
def dim_label(text: str, size: int = 10) -> QLabel: ...
def arcane_text_edit(placeholder: str = "") -> QTextEdit: ...

GLOBAL_STYLE = f"""
QMainWindow, QWidget {{ background-color: {C_BG}; color: {C_TEXT}; font-family: Georgia, Constantia, serif; }}
QScrollBar:vertical {{ background: {C_PANEL}; width: 8px; border: none; }}
QScrollBar::handle:vertical {{ background: {C_GOLD_DARK}; border-radius: 4px; min-height: 20px; }}
...
"""
```

---

## 8. Error Handling

| Error | Cause | Strategy |
|---|---|---|
| ClaudeBox ImportError | ClaudeBox/ directory absent | Catch on init; status bar message; app runs without conversation |
| CLAUDE_API_KEY absent | Env var not set | Warn in status bar on launch; stub response in workers; pipeline features remain functional |
| AmbientWorker API error | Rate limit, timeout, network | emit error(str); dim error text in whisper stream; does not crash; next debounce fires normally |
| ConversationWorker API error | Same causes | emit error(str); red bubble in conversation; user can retry |
| IdeaStore corruption | Malformed JSON | Catch on load; rename to ideas.json.bak; start empty; notify via status bar |
| Gate advancement blocked | Missing required fields | AdvanceDialog shows red checklist; no state change; no exception |
| Export .wiz fails (no Node) | Node.js not on PATH | Catch subprocess error; skip .wiz; log warning; other formats still generated |
| QThread collision | Two workers firing simultaneously | AmbientWorker aborts if _conv_active flag is set on ChamberPanel |

---

## 9. Setup & Testing

### requirements.txt

```
PyQt6>=6.6.0
python-docx
anthropic
# ClaudeBox installed as local editable or directory copy
```

### Install & Run

```bash
cd ~/Dolium
pip install PyQt6 python-docx anthropic
export CLAUDE_API_KEY=your_key_here
export DOLIUM_REPO_PATH=/home/lordfingers/ArcaCognitorium
export DOLIUM_CONTEXT_FILE=/home/lordfingers/ArcaCognitorium/CONTEXT.md
python main.py
```

### Unit Tests

```
test_models.py  — Idea/ChamberLog/CullRecord round-trip serialisation
test_store.py   — IdeaStore CRUD, advance, cull, resurrect
test_gates.py   — all gate functions with passing and failing Ideas
test_export.py  — ExportEngine .md .txt .docx against a populated Idea
test_prompts.py — build_user_message injects all populated fields
```

### Integration Test

```
Launch app with CLAUDE_API_KEY unset
Create idea in Fomentary
Fill title, body (100+ chars), motivation
Verify gate bar turns green
Advance — confirm modal shows green checklist
Verify idea appears in Cultivation House in pipeline
No crash, no data loss
```

---

## 10. Packaging

### .desktop file

```ini
[Desktop Entry]
Name=The Dolium
Exec=/home/lordfingers/Dolium/launch.sh
Icon=/home/lordfingers/Dolium/assets/dolium.png
Type=Application
Terminal=false
Categories=Utility;
```

### launch.sh

```bash
#!/bin/bash
export CLAUDE_API_KEY=$(cat ~/.config/dolium/api_key)
export DOLIUM_REPO_PATH=/home/lordfingers/ArcaCognitorium
export DOLIUM_CONTEXT_FILE=/home/lordfingers/ArcaCognitorium/CONTEXT.md
cd /home/lordfingers/Dolium && python main.py
```

---

## 11. Extensibility

| Feature | User Value · Implementation Approach |
|---|---|
| Session persistence across restarts | Entity remembers previous conversation after app close. · Serialize idea.conversation to disk (already done). On session creation replay history into ClaudeBox session via session.history parameter. |
| Cross-idea awareness | Entity knows all ideas in the pipeline — can flag overlaps. · Inject compact pipeline summary (titles + chambers + one-line body) into system prompt. ~200 tokens per session. |
| Whisper confidence threshold | Suppress whispers for very short or empty fields. · Add min_chars=80 guard in _on_debounce_fire before creating AmbientWorker. |
| Whisper history panel | Browse all past whispers for an idea — a record of the entity's observations over time. · Store whispers as a list in the Idea dataclass. Render in a collapsible panel. |
| /save command integration | Append any entity response directly to a workspace field. · Add /save <field> command parser in ChamberPanel. Calls WorkspacePanel.append_to_field(field, text). |
| Keyboard command palette | Modal-free fast commands via ctrl+k. · QDialog with QLineEdit + QListWidget. Commands registered as a dict. Enter fires the command. |

---

## 12. Critical Implementation Notes

### ClaudeBox threading configuration

The `claudebox.config.yaml` must have `streaming.thread_mode` set to 
`"threaded"`. This is essential — it runs the stream in a background thread and
 fires `on_token` events thread-safely. Without this, callbacks from a worker
  QThread will attempt to update Qt widgets from a non-main thread and crash
   unpredictably.

```yaml
streaming:
  enabled: true
  thread_mode: "threaded"  # REQUIRED for PyQt6
```

### Worker lifecycle — prevent QThread collision

AmbientWorker and ConversationWorker share the same ClaudeBox session per idea. 
They must not run simultaneously or they will interleave tokens into each
 other's UI targets. ChamberPanel must set a `self._conv_active` flag when
  ConversationWorker starts and clear it on `complete()`. AmbientWorker must
   check this flag in `_on_debounce_fire` and abort if True. The debounce time
   r does not restart during active conversation.

### QTimer debounce must be created on the main thread

QTimer objects must be created in the main thread. Do not create the debounce
 timer inside a worker. WorkspacePanel creates it in `__init__` and it lives on
  the main thread. Only the timeout signal crosses the thread boundary — it
   connects to `_on_debounce_fire` which then creates the AmbientWorker.

### Modus Arcanus — no deviation without explicit instruction

Every visual element follows `ModusArcanus_dux_tome.md` exactly. No cool greys,
 no pure black, no sans-serif, no bright colours other than gold. All widget 
 factories defined in `style.py`. No inline stylesheets in UI files.

---

## 13. Open Questions

- **Whisper prompt character** — what voice should the ambient whisper have? It
 is not the same as the chamber entity. More like a marginal annotation — brief, 
 observational, slightly oracular. Needs a specific system prompt distinct from 
 the conversation prompts. This is the most important creative decision in the
  redesign. Design it before building the ambient loop.

- **Whisper placement** — should whispers appear inline beside the field that 
triggered them, or in a unified stream in the right panel? Unified stream is
 architecturally cleaner. Field-level placement is more intuitive but requires 
 a more complex layout.

- **Session sharing between workers** — AmbientWorker and ConversationWorker 
should share history so the entity's conversation is aware of its own whispers.
 But this creates potential for confusing context. Consider a separate session 
 for whispers and a primary session for conversation.

- **Whisper rate limiting** — if the Wizard writes continuously across multiple 
fields, multiple whispers could queue up. Consider a cooldown period after a 
whisper completes before the next debounce can fire.

---

*The Dolium v2 — IdeaForge Build Document · 2026*
