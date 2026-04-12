╔═════════════════════════════════════════════════════════════════════════╗
║◤                                                                      ◥ ║
║                                                                         ║
║    ＴＨＥ ＤＯＬＩＵＭ — ＳＹＳＴＥＭＳ ＣＨＥＣＫ                      ║
║                                                                         ║
║◣                                                                      ◢ ║
╠═════════════════════════════════════════════════════════════════════════╣
║                                                                         ║
║    Application  ·  The Dolium                                           ║
║    Version      ·  2.0                                                  ║
║    Tests        ·  74/74 passing                                        ║
║    Started      ·  04-01-2026                                           ║
║                                                                         ║
╚═════════════════════════════════════════════════════════════════════════╝

╔═════════════════════╗
║ Verification steps: ║
╚═════════════════════╝
☑  1. App opens — three-panel layout visible


☑  2. Create a new idea — title and Fomentary fields accept input


☑  3. Type in a Fomentary field — entity whisper appears within ~2 seconds


☑  4. Try to advance with thin content — gate should block
		advance button greyed out

☑  5. Send a chat message — streams into conversation pane

☑  6. Restart app — idea and conversation history restore


═════════════════════════════════════════════════════════════════════════
╔════════════╗
║ Checklist: ║
╚════════════╝
☑  Storage directory exists and is writable


☑  ClaudeBox import resolves without error


☑   AmbientWorker fires within 1500ms of typing inactivity


☑   Whisper and conversation do not collide — `_conv_active` working


☑   Gate correctly blocks advancement with minimal content


☑  Export produces valid .md file on Declaration
.wiz export failed: [Errno 2] No such file or directory: 'node'

☑ App runs without entity if ClaudeBox unavailable (graceful degrade)




═════════════════════════════════════════════════════════════════════════
╔════════════╗
║ Open Items ║
╚════════════╝

Shared knowledge center context injection — deferred.
Praesidium pipeline state feed — not wired (infrastructure not ready).
Token budget display / session summarisation — deferred.
Theme resolution from Auctoritas Spectralis — deferred.
wiz_export.js Node dependency — degrades gracefully without Node.js.
