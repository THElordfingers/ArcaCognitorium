# Pairz Text Sampler & Renderer

A rapid-design tool for testing typography, ASCII art layouts, and color pairings using JSON data and local FIGlet fonts.

## Directory Structure
- `pairz-venv/` - Python virtual environment.
- `text-sampler.py` - The main application script.
- `SampleText/` - Directory containing `.json` data files.
- `FigletFonts/` - Directory for custom `.flf` and `.tlf` fonts.


## Keyboard Shortcuts

#Key/Mouse,				Action
Spacebar 				Load a random JSON sample with a random FIGlet font.
Ctrl + Scroll			Scale the Body text font size (Instant).
Shift + Scroll			Scale the Title size (Font size + FIGlet render width).
Left / Right			Cycle text justification (Left, Center, Right).
Up / Down				Micro-adjust Body text font size.



## JSON Format Requirements
Samples should be stored as `.json` files in `SampleText/`:
```json
{
  "TITLE": "Your Header",
  "TEXT": "Your body content...",
  "WIDTH": 700,
  "PADDING": 30,
  "FONT_FAMILY": "Helvetica"
}
