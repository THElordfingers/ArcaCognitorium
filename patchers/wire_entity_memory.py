#!/usr/bin/env python3
"""
wire_entity_memory.py
# VERSION: wire_entity_memory v1.0

Wires EntityMemory into app.py:
  1. Import EntityMemory
  2. Instantiate in __init__
  3. Set router after router is ready
  4. Inject entity memory into _build_context (after instruction string)
  5. Write to entity memory after primary response completes
  6. Write to entity memory after interruption completes
  7. Add /entity memory and /entity purge command handlers

Run from: /home/lordfingers/ArcaCognitorium/
    python wire_entity_memory.py
"""

import shutil, re
from pathlib import Path

APP_PY = Path("ui") / "app.py"
src = APP_PY.read_text(encoding="utf-8")
original = src


# ── 1. Import ─────────────────────────────────────────────────────────────────
if "from memory.entity_memory import EntityMemory" not in src:
    src = src.replace(
        "from memory.chronicle import Chronicle",
        "from memory.chronicle import Chronicle\nfrom memory.entity_memory import EntityMemory",
    )
    print("OK  import added")
else:
    print("SKIP import")


# ── 2. Instantiate after grimoire/tome init ───────────────────────────────────
if "self.entity_memory" not in src:
    src = src.replace(
        "        from memory.tome import Tome\n"
        "        self.tome = Tome(\n"
        "            project_store=self.projects,\n"
        "            max_injection_tokens=self.cfg.raw.get(\"memory\", {}).get(\"tome_max_tokens\", 600)\n"
        "        )",
        "        from memory.tome import Tome\n"
        "        self.tome = Tome(\n"
        "            project_store=self.projects,\n"
        "            max_injection_tokens=self.cfg.raw.get(\"memory\", {}).get(\"tome_max_tokens\", 600)\n"
        "        )\n"
        "\n"
        "        self.entity_memory = EntityMemory(\n"
        "            token_budget=self.cfg.raw.get(\"memory\", {}).get(\"entity_memory_budget\", 300),\n"
        "        )",
    )
    print("OK  EntityMemory instantiated")
else:
    print("SKIP instantiation")


# ── 3. Set router after router is ready ──────────────────────────────────────
# Router is created at top of __init__ — set entity_memory router at end of __init__
if "self.entity_memory.set_router" not in src:
    src = src.replace(
        "        from client.archivist_chronicler import BackgroundArchivist\n"
        "        self.background_archivist = BackgroundArchivist(",
        "        self.entity_memory.set_router(self.router)\n"
        "\n"
        "        from client.archivist_chronicler import BackgroundArchivist\n"
        "        self.background_archivist = BackgroundArchivist(",
    )
    print("OK  router set")
else:
    print("SKIP router set")


# ── 4. Inject entity memory into _build_context ───────────────────────────────
if "entity_memory.read" not in src:
    src = src.replace(
        "            messages.append({\n"
        "                \"role\": \"system\",\n"
        "                \"content\": lore_prefix + active_entity.instruction_str\n"
        "            })",
        "            entity_mem = self.entity_memory.read(active_entity.entity_id)\n"
        "            instruction_with_memory = active_entity.instruction_str\n"
        "            if entity_mem:\n"
        "                instruction_with_memory += \"\\n\\n\" + entity_mem\n"
        "            messages.append({\n"
        "                \"role\": \"system\",\n"
        "                \"content\": lore_prefix + instruction_with_memory\n"
        "            })",
    )
    print("OK  entity memory injected into _build_context")
else:
    print("SKIP _build_context injection")


# ── 5. Write after primary response ──────────────────────────────────────────
if "entity_memory.write" not in src:
    src = src.replace(
        "            # Background Archivist — chronicle preservation cycle",
        "            # Entity private memory — write after primary response\n"
        "            _em_entity = self.council.active\n"
        "            await asyncio.to_thread(\n"
        "                self.entity_memory.write,\n"
        "                _em_entity.entity_id,\n"
        "                _em_entity.display_name,\n"
        "                user_text,\n"
        "                assistant_text,\n"
        "            )\n"
        "\n"
        "            # Background Archivist — chronicle preservation cycle",
    )
    print("OK  write after primary response")
else:
    print("SKIP primary response write")


# ── 6. Write after interruption ───────────────────────────────────────────────
if "entity_memory.write" in src and "interruption_text" in src:
    # Find the interruption dismiss line and add write before it
    if "entity_memory.write" not in src.split("self.council.dismiss()")[0].split("interruption_text")[-1]:
        src = src.replace(
            "        self.dynamics.record_speaker(entity_id)\n"
            "        self.council.dismiss()  # revert to Luminarious",
            "        self.dynamics.record_speaker(entity_id)\n"
            "\n"
            "        # Entity private memory — write after interruption\n"
            "        await asyncio.to_thread(\n"
            "            self.entity_memory.write,\n"
            "            entity_id,\n"
            "            compiled.display_name,\n"
            "            message,\n"
            "            interruption_text,\n"
            "        )\n"
            "\n"
            "        self.council.dismiss()  # revert to Luminarious",
        )
        print("OK  write after interruption")
    else:
        print("SKIP interruption write")


# ── 7. Add /entity command handler ───────────────────────────────────────────
entity_cmd_handler = '''
    async def _handle_entity_command(self, argv: list) -> None:
        """
        /entity memory <id>   — show entity private memory
        /entity purge <id>    — clear entity private memory
        /entity memory all    — show all entity memory stores
        """
        if not argv:
            self._set_status("Usage: /entity memory <id> | /entity purge <id>")
            return

        sub = argv[0].lower()

        if sub == "memory":
            if len(argv) < 2:
                self._set_status("Usage: /entity memory <entity_id>  OR  /entity memory all")
                return
            target = argv[1].lower()
            if target == "all":
                lines = []
                for eid in ["luminarious"] + self.council.ALL_ENTITY_IDS:
                    entries = self.entity_memory.get_all_entries(eid)
                    if entries:
                        compiled = self.council.get_compiled(eid)
                        name = compiled.display_name if compiled else eid.upper()
                        lines.append(f"{name} ({len(entries)} entries):")
                        for e in entries:
                            lines.append(f"  - {e.content}")
                if not lines:
                    self._set_status("No entity memories recorded yet.")
                else:
                    self._set_status("\\n".join(lines))
                return
            entries = self.entity_memory.get_all_entries(target)
            if not entries:
                self._set_status(f"No memory for {target}.")
                return
            compiled = self.council.get_compiled(target)
            name = compiled.display_name if compiled else target.upper()
            lines = [f"{name} — private memory ({len(entries)} entries):"]
            for e in entries:
                lines.append(f"  [{e.created_at[:10]}] {e.content}")
                if e.context:
                    lines.append(f"    context: {e.context[:80]}")
            usage = self.entity_memory.token_usage(target)
            lines.append(f"  tokens: {usage['used_tokens']}/{usage['budget_tokens']} ({usage['pct']}%)")
            self._set_status("\\n".join(lines))

        elif sub == "purge":
            if len(argv) < 2:
                self._set_status("Usage: /entity purge <entity_id>")
                return
            target = argv[1].lower()
            self.entity_memory.purge(target)
            self._set_status(f"Memory purged: {target}")

        else:
            self._set_status("Usage: /entity memory <id> | /entity purge <id>")

'''

if "_handle_entity_command" not in src:
    # Insert before the closing of command dispatcher section
    src = src.replace(
        "    async def _handle_model_command",
        entity_cmd_handler + "    async def _handle_model_command",
    )
    print("OK  /entity command handler added")
else:
    print("SKIP /entity handler")


# ── 8. Wire /entity into command dispatcher ───────────────────────────────────
if 'cmd == "/entity"' not in src:
    src = src.replace(
        '        if cmd == "/summon":',
        '        if cmd == "/entity":\n'
        '            await self._handle_entity_command(argv)\n'
        '            return\n'
        '\n'
        '        if cmd == "/summon":',
    )
    print("OK  /entity wired into dispatcher")
else:
    print("SKIP dispatcher wiring")


# ── Write ─────────────────────────────────────────────────────────────────────
if src == original:
    print("\nNothing changed.")
else:
    shutil.copy2(APP_PY, APP_PY.with_suffix(".py.bak"))
    APP_PY.write_text(src, encoding="utf-8")
    print(f"\nOK  {APP_PY} written")
