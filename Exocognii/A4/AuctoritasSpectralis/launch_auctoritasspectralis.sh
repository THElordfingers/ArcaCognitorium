#!/usr/bin/env bash
# AUCTORITAS SPECTRALIS — v1.0.0
source "/home/lordfingers/ArcaCognitorium/Exocognii/A4/AuctoritasSpectralis/venv-SPECTRALIS/bin/activate"
export PYTHONPATH="/home/lordfingers/ArcaCognitorium/Exocognii/A4"
cd "/home/lordfingers/ArcaCognitorium/Exocognii/A4"
python3 -m AuctoritasSpectralis "$@"
