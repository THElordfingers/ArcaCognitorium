"""
Entry point — run as:
    cd /home/lordfingers/ArcaCognitorium/tools
    python -m Fenestrium
"""
import sys, os
# Insert tools/ so Python can find the Fenestrium package
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from Fenestrium.app import main
main()
