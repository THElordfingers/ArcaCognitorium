**Claude API → ClaudeBox** — all intelligence routes through the shared wrapper. No app calls the API directly.

**ClaudeBox fans out** to the four main apps (Dolium, Praesidium, Entitex, Mythotex) and the smaller tools (Lexiferium, Incitamentum). Vigilarum is there but flagged. Fenestrium is pending a retirement decision.

**Involucrum layer** — all apps fire-and-forget to both memory services simultaneously. Neither service is in the critical path for any app.

**Memory services** (both planned, schemas complete) — Exvacua Loricum holds lore canon, Perpetuum Aedificare holds build state. Both feed the Praesidium read layer which is the Wizard-facing query surface.

**Bottom tier** — Configuus (config), Codexium Chromaticus (theme pipeline, planned), and the token ledger. These are the shared infrastructure that everything else either already uses or will use once built.