"""
🮈🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃▍
🮈  ██████   █████  ████████  ██████ ██   ██         ███    ███  █████  ██ ███    ██        ██    ██ ██████  ▍
🮈  ██   ██ ██   ██    ██    ██      ██   ██         ████  ████ ██   ██ ██ ████   ██        ██    ██      ██ ▍
🮈  ██████  ███████    ██    ██      ███████         ██ ████ ██ ███████ ██ ██ ██  ██        ██    ██  █████  ▍
🮈  ██      ██   ██    ██    ██      ██   ██         ██  ██  ██ ██   ██ ██ ██  ██ ██         ██  ██       ██ ▍
🮈  ██      ██   ██    ██     ██████ ██   ██ ███████ ██      ██ ██   ██ ██ ██   ████ ███████  ████   ██████  ▍
🮈                                                                                                           ▍
🮈                                                                                                           ▍
🮈                                               Python Script                                               ▍
🭅▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃🭐
██████████████████████████████████████████████████████████████████████████████████████████████████████████████
█░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░█
🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃
patch_main_v3.py — Devoted Absurd / main.py
Wires the Claude generation path (generate_character_async) into the UI.
Previously the Generate button only used the local pool-pick path.
Now:
  — "GENERATE" calls Claude generation (pools as vocabulary reference)
  — "LOCAL" calls the old local pool-pick path (fast, offline fallback)
  — char card now shows era_blend if present
  — generate_character_async call passes archetype_vocabulary

Usage:
    python patch_main_v3.py           # apply
    python patch_main_v3.py --check   # dry run, no changes written
"""

import sys
import shutil
from pathlib import Path

TARGET = Path.home() / "ArcaCognitorium/Exocognii/Entitex/Referentia/Prompts/DevotedAbsurd-PromptGen/__main__.py"
BACKUP = TARGET.with_suffix(".py.bak_v3")

PATCHES = [

    # 1. Rename "GENERATE" to "CLAUDE GEN" and add LOCAL button
    {
        "description": "Rename generate button and add LOCAL fallback button",
        "old": '        self.btn_generate = QPushButton("GENERATE")\n        self.btn_generate.setObjectName("btn_generate")\n        self.btn_random = QPushButton("↻ RANDOM")\n        self.btn_random.setObjectName("btn_random")\n        btn_lay.addWidget(self.btn_generate)\n        btn_lay.addWidget(self.btn_random)',
        "new": '        self.btn_generate = QPushButton("CLAUDE GEN")\n        self.btn_generate.setObjectName("btn_generate")\n        self.btn_local = QPushButton("LOCAL")\n        self.btn_local.setObjectName("btn_random")\n        self.btn_local.setToolTip("Generate from pools directly (fast, offline fallback)")\n        self.btn_random = QPushButton("↻ RANDOM")\n        self.btn_random.setObjectName("btn_random")\n        btn_lay.addWidget(self.btn_generate)\n        btn_lay.addWidget(self.btn_local)',
    },

    # 2. Wire the new LOCAL button
    {
        "description": "Wire LOCAL button click to generate_local",
        "old": "        self.btn_generate.clicked.connect(self.generate)\n        self.btn_random.clicked.connect(self.generate_random)\n        self.btn_copy.clicked.connect(self.copy_prompt)\n        self.btn_clear.clicked.connect(self.clear)",
        "new": "        self.btn_generate.clicked.connect(self.generate)\n        self.btn_local.clicked.connect(self.generate_local)\n        self.btn_random.clicked.connect(self.generate_random)\n        self.btn_copy.clicked.connect(self.copy_prompt)\n        self.btn_clear.clicked.connect(self.clear)",
    },

    # 3. Replace generate() with Claude generation path
    {
        "description": "Replace generate() to use Claude generation with vocabulary",
        "old": """    def generate(self):
        weights = learning.get_weights()
        char = dp.build_character(
            archetype_key=self._get_archetype_key(),
            overrides=self._get_overrides(),
            combo_weights=weights,
        )
        prompt = dp.assemble_prompt(char)
        self._current_char = char
        self._current_entry_id = str(uuid.uuid4())[:8]
        self._current_prompt = prompt
        self._claude_result = None

        self.prompt_output.setPlainText(prompt)
        self._update_char_card(char)
        self.btn_analyse.setEnabled(True)
        self._reset_claude_panel()
        self._update_stats_footer()

        self.tabs.setCurrentIndex(0)
        self.status(f"Generated: {char['archetype_label']} / {char['role'][:40]}")

        if self.chk_auto_analyse.isChecked():
            QTimer.singleShot(300, self.send_to_claude)""",
        "new": """    def generate(self):
        \"\"\"Claude generation path — pools as vocabulary reference, Claude invents freely.\"\"\"
        archetype_key = self._get_archetype_key()
        if archetype_key == "random":
            import random
            archetype_key = random.choice(list(dp.ARCHETYPES.keys()))

        arch = dp.ARCHETYPES[archetype_key]
        overrides = self._get_overrides()
        vocabulary = dp.get_archetype_vocabulary(archetype_key)

        self._current_entry_id = str(uuid.uuid4())[:8]
        self._claude_result = None
        self._reset_claude_panel()
        self.btn_analyse.setEnabled(False)
        self.progress_bar.show()
        self.status("Claude generating character...")

        claude_worker.generate_character_async(
            archetype_key=archetype_key,
            archetype_label=arch["label"],
            palette_hint=arch["palette_hint"],
            style_flex=arch["style_flex"],
            overrides=overrides,
            archetype_vocabulary=vocabulary,
            on_complete=self._on_claude_generated,
            on_error=self._on_claude_generate_error,
        )

    def _on_claude_generated(self, char: dict):
        \"\"\"Receive Claude-generated character, build prompt, update UI.\"\"\"
        prompt = char.get("assembled_prompt") or dp.assemble_prompt(char)
        self._current_char = char
        self._current_prompt = prompt

        self.prompt_output.setPlainText(prompt)
        self._update_char_card(char)
        self.btn_analyse.setEnabled(True)
        self.progress_bar.hide()
        self._update_stats_footer()
        self.tabs.setCurrentIndex(0)
        self.status(f"Claude generated: {char['archetype_label']} / {char.get('role', '')[:40]}")

        if self.chk_auto_analyse.isChecked():
            QTimer.singleShot(300, self.send_to_claude)

    def _on_claude_generate_error(self, error: str):
        self.progress_bar.hide()
        self.btn_analyse.setEnabled(False)
        self.status(f"Claude generation error: {error[:80]} — try LOCAL instead")

    def generate_local(self):
        \"\"\"Local fallback path — direct pool selection, fast and offline.\"\"\"
        weights = learning.get_weights()
        char = dp.build_character(
            archetype_key=self._get_archetype_key(),
            overrides=self._get_overrides(),
            combo_weights=weights,
        )
        prompt = dp.assemble_prompt(char)
        self._current_char = char
        self._current_entry_id = str(uuid.uuid4())[:8]
        self._current_prompt = prompt
        self._claude_result = None

        self.prompt_output.setPlainText(prompt)
        self._update_char_card(char)
        self.btn_analyse.setEnabled(True)
        self._reset_claude_panel()
        self._update_stats_footer()

        self.tabs.setCurrentIndex(0)
        self.status(f"[LOCAL] Generated: {char['archetype_label']} / {char['role'][:40]}")

        if self.chk_auto_analyse.isChecked():
            QTimer.singleShot(300, self.send_to_claude)""",
    },

    # 4. generate_random now calls generate() (Claude path) not generate_local
    {
        "description": "generate_random clears fields then calls Claude generate",
        "old": """    def generate_random(self):
        self.combo_archetype.setCurrentIndex(0)
        self.combo_mood.setCurrentIndex(0)
        self.combo_body.setCurrentIndex(0)
        self.combo_age.setCurrentIndex(0)
        self.combo_gender.setCurrentIndex(0)
        self.combo_bg.setCurrentIndex(0)
        self.input_name.clear()
        self.input_role.clear()
        self.input_personality.clear()
        self.input_extra.clear()
        self.generate()""",
        "new": """    def generate_random(self):
        \"\"\"Full random — clears all overrides and fires Claude generation.\"\"\"
        self.combo_archetype.setCurrentIndex(0)
        self.combo_mood.setCurrentIndex(0)
        self.combo_body.setCurrentIndex(0)
        self.combo_age.setCurrentIndex(0)
        self.combo_gender.setCurrentIndex(0)
        self.combo_bg.setCurrentIndex(0)
        self.input_name.clear()
        self.input_role.clear()
        self.input_personality.clear()
        self.input_extra.clear()
        self.generate()""",
    },

    # 5. Update char card to show era_blend if present
    {
        "description": "Update _update_char_card to show era_blend",
        "old": """    def _update_char_card(self, char: dict):
        lines = [
            f"<b style='color:{C['amber']}'>{char['archetype_label'].upper()}</b>  "
            f"<span style='color:{C['text_dim']}'>{'| ' + char['name'] if char['name'] else ''}</span>",
            f"<span style='color:{C['green_b']}'>{char['role']}</span>"
            f"  <span style='color:{C['muted']}'>({char['age'].split('—')[0].strip()})</span>",
            f"<span style='color:{C['text_dim']}'>{char['personality']}</span>",
        ]
        self.lbl_char_info.setText("<br>".join(lines))
        self.lbl_char_info.setTextFormat(Qt.TextFormat.RichText)""",
        "new": """    def _update_char_card(self, char: dict):
        era = char.get("era_blend", "")
        era_span = (
            f"<br><span style='color:{C['teal_b']}; font-size:10px;'>{era}</span>"
            if era else ""
        )
        lines = [
            f"<b style='color:{C['amber']}'>{char['archetype_label'].upper()}</b>  "
            f"<span style='color:{C['text_dim']}'>{'| ' + char['name'] if char['name'] else ''}</span>",
            f"<span style='color:{C['green_b']}'>{char.get('role','')}</span>"
            f"  <span style='color:{C['muted']}'>({char.get('age','').split('—')[0].strip()})</span>"
            f"{era_span}",
            f"<span style='color:{C['text_dim']}'>{char.get('personality','')}</span>",
        ]
        self.lbl_char_info.setText("<br>".join(lines))
        self.lbl_char_info.setTextFormat(Qt.TextFormat.RichText)""",
    },
]


def apply(dry_run: bool = False):
    if not TARGET.exists():
        print(f"ERROR: target not found:\n  {TARGET}")
        sys.exit(1)

    source = TARGET.read_text(encoding="utf-8")
    result = source
    all_ok = True

    for p in PATCHES:
        if p["old"] not in result:
            print(f"  MISS  [{p['description']}] — string not found, skipping")
            all_ok = False
        else:
            count = result.count(p["old"])
            if count > 1:
                print(f"  WARN  [{p['description']}] — {count} matches, patching all")
            result = result.replace(p["old"], p["new"])
            print(f"  OK    [{p['description']}]")

    if dry_run:
        print("\n-- DRY RUN — no files written --")
        return

    if not all_ok:
        print("\nWARN: some patches missed. Writing what succeeded.")

    shutil.copy2(TARGET, BACKUP)
    print(f"\nBackup: {BACKUP}")
    TARGET.write_text(result, encoding="utf-8")
    print(f"Patched: {TARGET}")


if __name__ == "__main__":
    dry_run = "--check" in sys.argv
    if dry_run:
        print("-- CHECK MODE --\n")
    apply(dry_run)
