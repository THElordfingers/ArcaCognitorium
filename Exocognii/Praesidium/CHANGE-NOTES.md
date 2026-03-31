╭────────────────────────╮
│🟄                      🟄│
│🟄 ＰＲＡＥＳＩＤＩＵＭ 🟅│
│🟆     ＵＰＤＡＴＥ     🟆│
│🟅      ＮＯＴＥＳ      🟅│
│🟄                      🟄│
╰────────────────────────╯


🟂 TO DO board 	
			  	⭑ Arrange/Rename list items
				⭑ Fix erratic multiple widgets on load
				⭑ Custom Glyph Sheet Browser	
				⭑ Display widget needs to retain whitespace in loaded files.
				⭑ needs font resizing option (added but non functional)
				
🟂


🟂


🟂


🟂


🟂


🟂


🟂


🟂 Glyph Browser crash:

Traceback (most recent call last):
  File "/home/lordfingers/ArcaCognitorium/Exocognii/Praesidium/praesidium_app.py", line 179, in _show_widget_picker
    self._spawn_widget(chosen.data())
  File "/home/lordfingers/ArcaCognitorium/Exocognii/Praesidium/praesidium_app.py", line 186, in _spawn_widget
    w = self._registry.instantiate(
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/lordfingers/ArcaCognitorium/Exocognii/Praesidium/widget_registry.py", line 87, in instantiate
    module = importlib.import_module(module_path)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/lordfingers/.pyenv/versions/3.11.9/lib/python3.11/importlib/__init__.py", line 126, in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "<frozen importlib._bootstrap>", line 1204, in _gcd_import
  File "<frozen importlib._bootstrap>", line 1176, in _find_and_load
  File "<frozen importlib._bootstrap>", line 1147, in _find_and_load_unlocked
  File "<frozen importlib._bootstrap>", line 690, in _load_unlocked
  File "<frozen importlib._bootstrap_external>", line 940, in exec_module
  File "<frozen importlib._bootstrap>", line 241, in _call_with_frames_removed
  File "/home/lordfingers/ArcaCognitorium/Exocognii/Praesidium/widgets/glyph_browser.py", line 267, in <module>
    class GlyphButton(QLabel):
  File "/home/lordfingers/ArcaCognitorium/Exocognii/Praesidium/widgets/glyph_browser.py", line 297, in GlyphButton
    def mousePressEvent(self, event: QMouseEvent) -> None:
                                     ^^^^^^^^^^^
NameError: name 'QMouseEvent' is not defined
/home/lordfingers/ArcaCognitorium/Exocognii/Praesidium/Praesidium.sh: line 11: 17658 Aborted                 (core dumped) python3 run.py


