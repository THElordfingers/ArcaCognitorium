::INIT

TIER: TIER 6 — VIGILARUM MIGRATION
TARGET: Build Vigilarum V2
STATE: ::THEORY ::REVIEW ::BUILD

FILES IN SCOPE:
- ~/ArcaCognitorium/Exocognii/Vigilarum/
									control.py
									data.py
									display.py
									engine.py
									renderers.py
									state.py
									widgets.py
					

CONTEXT:
Vigilarum is a GUI that interfaces outputs from pyswisseph in the form of 
widgets. This is it's upgrade to PyQt6. 

TASK:
Analyze the old app, design an upgrade, run it through IdeaForge.
May also be a good time to index, inspect, and integrate all the 
data points and variables with the machinae family of apps and see what
needs to be written to connect everything.

CONSTRAINTS:
This is not an integration into any system, it is a standalone app that monitors
the variable outputs of pyswisseph for demonstrative purposes. 

KNOWN STATE:
A lot of the issues stemmed from widgets having mediocre or unusable outputs, 
mostly stemming from limitations presented by Textual UI
