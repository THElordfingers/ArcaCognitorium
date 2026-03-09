#!/usr/bin/env python3
"""
Phase 8 app.py patcher.
Run from ~/ArcaCognitorium:  python apply_phase8_patches.py
Creates a backup at ui/app.py.bak before patching.
"""
import shutil
from pathlib import Path

APP = Path("ui/app.py")
BAK = Path("ui/app.py.bak")

if not APP.exists():
    print("ERROR: ui/app.py not found. Run from project root.")
    exit(1)

shutil.copy(APP, BAK)
print(f"Backup written: {BAK}")

src = APP.read_text(encoding="utf-8")
original_len = len(src)


def patch(src, old, new, label):
    if old not in src:
        print(f"  MISS: {label} — target string not found")
        return src
    count = src.count(old)
    if count > 1:
        print(f"  WARN: {label} — {count} occurrences found, replacing first only")
        return src.replace(old, new, 1)
    result = src.replace(old, new, 1)
    print(f"  OK:   {label}")
    return result


# ── PATCH 1: Imports ──────────────────────────────────────────────────────────
src = patch(src,
    "        from entities.entity_compiler import EntityCompiler\n        from entities.council import Council\n        self.compiler = EntityCompiler(\"entities\")\n        self.council = Council(self.compiler)",
    """        from entities.entity_compiler import EntityCompiler
        from entities.council import Council
        from entities.emergence import EmergenceEngine
        from entities.interruption import InterruptionEngine
        from entities.dynamics import InterEntityDynamics
        self.compiler = EntityCompiler("entities")
        self.council = Council(self.compiler)
        reflection_log = self.cfg.raw.get("storage", {}).get(
            "reflection_log_path", "storage/logs/reflections.jsonl"
        )
        self.emergence_engine = EmergenceEngine(reflection_log)
        self.interruption_engine = InterruptionEngine()
        self.dynamics = InterEntityDynamics()""",
    "Patch 1: imports + engine instantiation"
)


# ── PATCH 2: Fix duplicate entity injection in _build_context ─────────────────
# Remove the second identical block (keep the first)
DUPE_BLOCK = """
        # Phase 6: Entity instruction string — always first in context
        active_entity = self.council.active
        if active_entity:
            messages.append({
                "role": "system",
                "content": active_entity.instruction_str
            })"""

# It appears twice — remove the second occurrence only
first_pos = src.find(DUPE_BLOCK)
if first_pos == -1:
    print("  MISS: Patch 2 — duplicate entity block not found")
else:
    second_pos = src.find(DUPE_BLOCK, first_pos + 1)
    if second_pos == -1:
        print("  SKIP: Patch 2 — only one entity injection block found (already clean)")
    else:
        src = src[:second_pos] + src[second_pos + len(DUPE_BLOCK):]
        print("  OK:   Patch 2: remove duplicate entity injection")


# ── PATCH 3: Add Tome injection to _build_context ────────────────────────────
src = patch(src,
    """        # Phase 3 decision:
        # retrieval is project-scoped on conversation_ids BUT thread-restricted per conversation""",
    """        # Phase 4 — Tome injection (project-scoped knowledge)
        tome_injection = self.tome.build_injection_string()
        if tome_injection:
            messages.append({
                "role": "system",
                "content": tome_injection
            })

        # Phase 3 decision:
        # retrieval is project-scoped on conversation_ids BUT thread-restricted per conversation""",
    "Patch 3: Tome injection in _build_context"
)


# ── PATCH 4: Refresh router baseline after distillation ───────────────────────
src = patch(src,
    """            self.animation_controller.fire_event('distillation')
            self.status_layer.update_status(
                distillation_count=self.status_layer.state.distillation_count + 1
            )
            return messages""",
    """            self.animation_controller.fire_event('distillation')
            self.status_layer.update_status(
                distillation_count=self.status_layer.state.distillation_count + 1
            )
            self.router.router.refresh_reflection_baseline()  # Phase 7/8
            return messages""",
    "Patch 4: refresh_reflection_baseline after distillation"
)


# ── PATCH 5: _assistant_task — add dynamics reset + Phase 8 hooks ─────────────
src = patch(src,
    """        self._streaming = True
        try:
            await asyncio.to_thread(self.conversations.append, "user", user_text, thread_id=thread_id)""",
    """        self._streaming = True
        self.dynamics.reset_turn()  # Phase 8: reset inter-entity dynamics each turn
        try:
            await asyncio.to_thread(self.conversations.append, "user", user_text, thread_id=thread_id)""",
    "Patch 5a: dynamics.reset_turn() in _assistant_task"
)

src = patch(src,
    """            # thread-scoped summary for analytics
            t = self.conversations.get_thread(thread_id)
            await asyncio.to_thread(
                self.reflection.observe,
                conversation_id=self.conversations.active.id,
                summary=t.summary,
                last_user=user_text,
                last_assistant=assistant_text,
            )

        except Exception as e:""",
    """            # thread-scoped summary for analytics
            t = self.conversations.get_thread(thread_id)
            await asyncio.to_thread(
                self.reflection.observe,
                conversation_id=self.conversations.active.id,
                summary=t.summary,
                last_user=user_text,
                last_assistant=assistant_text,
            )

            # Phase 8: emergence check + interruption
            await asyncio.to_thread(self._check_emergence)
            await self._check_interruption(user_text, assistant_text)

        except Exception as e:""",
    "Patch 5b: Phase 8 hooks at end of _assistant_task"
)


# ── PATCH 6: Add new methods before _handle_grimoire_command ──────────────────
NEW_METHODS = '''
    # ── Phase 8: Emergence, Interruption, Council Nav ────────────────────────

    def _check_emergence(self) -> None:
        """
        Read Reflection log. Check for newly emerged Entities.
        Silent — no system bubble. Called via asyncio.to_thread after distillation.
        """
        newly_emerged = self.emergence_engine.check_emergence(self.council)
        if newly_emerged:
            for entity_id in newly_emerged:
                try:
                    self.council.emerge(entity_id)
                except Exception:
                    pass
            self._refresh_council_nav()
            self.router.router.refresh_reflection_baseline()

    async def _check_interruption(self, message: str, response: str) -> None:
        """
        Post-response interruption check. If an Entity passes all three gates,
        renders an interruption bubble with ↯ in the header.
        Active Entity reverts to Luminarious after. Only one interruption per turn.
        """
        result = self.interruption_engine.check(
            message, response,
            council=self.council,
            emergence_engine=self.emergence_engine,
            dynamics=self.dynamics,
        )
        if not result.should_interrupt:
            return

        entity_id = result.entity_id
        compiled = self.council.get_compiled(entity_id)
        if not compiled:
            try:
                compiled = self.council.summon(entity_id)
            except Exception:
                return

        context = [
            {"role": "system", "content": compiled.instruction_str},
            {"role": "user", "content": message},
            {"role": "assistant", "content": response},
            {"role": "user", "content": (
                "You are interrupting this conversation. Speak briefly — one to three "
                "sentences only. Do not summarize what was said. Offer your specific "
                "perspective from your domain. Begin immediately."
            )},
        ]

        try:
            interruption_text = await asyncio.to_thread(
                self._interruption_api_call, context, compiled.sampling_profile
            )
        except Exception as e:
            self._set_status(f"Interruption error ({entity_id}): {e}")
            return

        self._mount_combo(
            self.middle.current_turn,
            header=f"↯ {compiled.display_name}",
            body=interruption_text,
            render_mode="markdown",
            align="left",
            combo_classes="assistant entity-interrupt",
        )
        self.animation_controller.fire_event(
            "entity_interrupt",
            entity_color=compiled.color_hex,
        )
        self.dynamics.record_speaker(entity_id)
        self.council.dismiss()  # revert to Luminarious

    def _interruption_api_call(self, context: list, profile: dict) -> str:
        """Synchronous. Run via asyncio.to_thread."""
        gen, _meta = self.router.stream_response_text(
            self.cfg.models.nano,
            context,
            max_output_tokens=profile.get("max_output_tokens", 300),
        )
        return "".join(gen)

    def _refresh_council_nav(self) -> None:
        """Update left nav COUNCIL section after emergence. Silent."""
        emerged = self.council.get_emerged()
        if not emerged:
            return
        lines = ["COUNCIL"]
        for entity_id in sorted(emerged):
            compiled = self.council.get_compiled(entity_id)
            name = compiled.display_name if compiled else entity_id.upper()
            lines.append(f"◆ {name}")
        council_text = "\\n".join(lines)
        if hasattr(self.left, "set_council"):
            self.left.set_council(council_text)

    async def _handle_model_command(self, argv: list) -> None:
        """
        /model              — list all models
        /model smart|fast   — pin tier
        /model [id]         — pin specific model
        /model auto         — unpin, resume routing
        """
        router = self.router.router
        if not argv:
            models = router.list_models()
            if models is None:
                self._set_status("Model registry not found at entities/models.yaml.")
                return
            lines = [
                f"[{m.get('tier','')}] {m.get('display_name','')} — {m.get('id','')}"
                for m in models
            ]
            self._set_status("Models:\\n" + "\\n".join(lines))
            return
        sub = argv[0].lower().strip()
        if sub == "auto":
            router.unpin_model()
            self._set_status("◆ Auto-routing restored.")
            return
        if sub == "smart":
            model_id = self.cfg.models.smart
        elif sub == "fast":
            model_id = self.cfg.models.fast
        else:
            model_id = argv[0].strip()
            models = router.list_models() or []
            known_ids = {m.get("id") for m in models}
            if known_ids and model_id not in known_ids:
                self._set_status(f"Unknown model: {model_id!r}. Use /model to list available.")
                return
        router.pin_model(model_id)
        self._set_status(
            f"◆ Model pinned: {model_id}. /model auto to resume routing."
        )

    async def _handle_route_command(self, argv: list) -> None:
        """
        /route              — show last routing decision breakdown
        /route [message]    — score hypothetical without sending
        """
        router = self.router.router
        if argv:
            result = router.route_full(" ".join(argv).strip())
            self._set_status(f"[HYPOTHETICAL]\\n{router.format_route_display(result)}")
        else:
            self._set_status(router.format_route_display())

    async def _handle_council_command(self, argv: list) -> None:
        """
        /council            — show emerged entities
        /council signals    — all entity signal strengths
        /council dynamics   — relationship graph
        """
        if not argv:
            emerged = self.council.get_emerged()
            signals = self.emergence_engine.get_signal_strengths()
            if not emerged:
                self._set_status("No Entities have emerged yet. The Council stirs...")
                return
            lines = ["COUNCIL"]
            for eid in sorted(emerged):
                sig = signals.get(eid, 0.0)
                compiled = self.council.get_compiled(eid)
                name = compiled.display_name if compiled else eid.upper()
                lines.append(f"  ◆ {name}  (signal: {sig:.2f})")
            self._set_status("\\n".join(lines))
            return
        sub = argv[0].lower()
        if sub == "signals":
            signals = self.emergence_engine.get_signal_strengths()
            lines = ["Signal strengths:"]
            for eid, sig in sorted(signals.items(), key=lambda x: -x[1]):
                mark = "◆" if self.council.has_emerged(eid) else "·"
                lines.append(f"  {mark} {eid:<20} {sig:.3f}")
            self._set_status("\\n".join(lines))
            return
        if sub == "dynamics":
            rels = self.dynamics.get_relationships()
            lines = ["Relationship graph:"]
            for r in rels:
                lines.append(f"  [{r.relationship_type}] {r.entity_a} → {r.entity_b}: {r.effect}")
            self._set_status("\\n".join(lines))
            return
        self._set_status("Council commands: /council · /council signals · /council dynamics")

'''

src = patch(src,
    "    async def _handle_grimoire_command(self, args: list[str]) -> None:",
    NEW_METHODS + "    async def _handle_grimoire_command(self, args: list[str]) -> None:",
    "Patch 6: new Phase 8 methods"
)


# ── PATCH 7: Route /model, /route, /council in _handle_menu_command ───────────
src = patch(src,
    """        if cmd == "/dismiss":
            self.council.dismiss()
            entity = self.council.active
            self.status_layer.update_status(
                entity_name=entity.display_name,
                entity_color=entity.color_hex
            )
            self._set_status(f"Returned to: {entity.display_name}")
            return""",
    """        if cmd == "/dismiss":
            self.council.dismiss()
            entity = self.council.active
            self.status_layer.update_status(
                entity_name=entity.display_name,
                entity_color=entity.color_hex
            )
            self._set_status(f"Returned to: {entity.display_name}")
            return

        if cmd == "/model":
            await self._handle_model_command(argv)
            return

        if cmd == "/route":
            await self._handle_route_command(argv)
            return

        if cmd == "/council":
            await self._handle_council_command(argv)
            return""",
    "Patch 7: /model, /route, /council command routing"
)


APP.write_text(src, encoding="utf-8")
print(f"\nDone. {original_len} → {len(src)} chars (+{len(src)-original_len})")
print("Run: pytest tests/ -v")
