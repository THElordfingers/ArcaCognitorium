# MYTHOTEX — THE LIVING TOWER
*Generative lore engine for the Arca Cognitarium*

---

## Overview

Mythotex is a desktop application that procedurally generates arcane item
entries — title, lore, and illustration — for use in the **Arca Cognitarium**
project. Each generation produces a wiki-style lore entry (via GPT-4o) paired
with a volumetric fantasy illustration (via Stable Diffusion), with the
background automatically removed to yield a transparent-background PNG ready
for use as a collectible or catalogued relic.

The engine is self-refining: it periodically analyses its own vault of rated
outputs and revises its generation strategy, accumulating an **Aesthetic DNA**
that steers future generations toward styles you've approved and away from
styles you've penalised.

---

## Architecture

```
MythotexApp          QMainWindow — primary interface, sidebar, viewport
├── ControlPanel     QFrame — slide-out panel, all runtime parameters
├── CompendiumTome   QDialog — vault browser with aesthetic rating
├── MythotexWorker   QThread — lore generation (GPT) + image generation (SD)
└── AnalysisWorker   QThread — self-refining analysis engine
```

---

## Directory Structure

All runtime data lives under `~/Mythotex/` by default.

```
~/Mythotex/
├── Vault/                      Sealed relic entries
│   └── <slug>/
│       ├── relic_<ts>.png      Transparent-background illustration
│       └── relic_<ts>.json     Lore entry + seed + rating
├── Referentia/
│   ├── lore_immutable.md       Fixed world-canon — never overwritten
│   └── lore_mutable.md         Engine strategy — updated by AnalysisWorker
├── models/                     Place .safetensors here for sd.cpp backend
│   └── v1-5-pruned-emaonly.safetensors
├── aesthetic_dna.json          Accumulated favoured / forbidden qualities
├── generation_log.json         Generation counters, analysis trigger state
└── temp_manifest.png           Ephemeral working file, overwritten each run
```

> **`lore_immutable.md`** is the canonical foundation — world rules, tone,
> naming conventions. Write it once and leave it alone.
>
> **`lore_mutable.md`** is rewritten by the AnalysisWorker after every
> analysis pass. You can read it but shouldn't edit it manually.

---

## Setup

### 1. Python environment

```bash
python3 -m venv venv-Mythotex
source venv-Mythotex/bin/activate
pip install torch diffusers transformers accelerate openai PyQt6 Pillow
pip install rembg optimum-quanto          # optional but recommended
```

### 2. API key

```bash
export OPENAI_API_KEY="sk-..."
```

Add to `~/.bashrc` or `~/.profile` to persist.

### 3. Run

```bash
source venv-Mythotex/bin/activate
python Mythotex.py
```

On first run, Hugging Face will download the active model (~4 GB for LCM
Dreamshaper, ~4 GB for SD 1.5). These are cached in `~/.cache/huggingface/`
and not re-downloaded on subsequent launches.

---

## Hardware Notes (AMD Raphael iGPU)

Mythotex auto-detects hardware at startup and configures the pipeline
accordingly.

```
╔══════════════════╦══════════════════════════════╦═════════╦════════════════╗
║ Device           ║ Detection                    ║ dtype   ║ Notes          ║
╠══════════════════╬══════════════════════════════╬═════════╬════════════════╣
║ ROCm (AMD GPU)   ║ torch.cuda.is_available()    ║ float16 ║ Sequential CPU ║
║                  ║                              ║         ║ offload; GTT   ║
║                  ║                              ║         ║ spill for VRAM ║
╠══════════════════╬══════════════════════════════╬═════════╬════════════════╣
║ Apple MPS        ║ torch.backends.mps           ║ float16 ║ Attention      ║
║                  ║   .is_available()            ║         ║ slicing only   ║
╠══════════════════╬══════════════════════════════╬═════════╬════════════════╣
║ CPU              ║ fallback                     ║ float32 ║ Full system    ║
║                  ║                              ║         ║ RAM; default   ║
║                  ║                              ║         ║ for Raphael    ║
╚══════════════════╩══════════════════════════════╩═════════╩════════════════╝
```

The Raphael `0x164e` has 512 MB dedicated VRAM and 2 Compute Units. If ROCm
is installed but `torch.cuda.is_available()` returns `False`, try:

```bash
HSA_OVERRIDE_GFX_VERSION=10.3.0 python Mythotex.py
```

---

## Inference Engines

Switch engines in the **⚡ ENGINE** tab of the control panel. Hit
**⚡ RELOAD ENGINE** in the sidebar to apply changes without restarting.

### LCM — `LCM (4–8 steps)` *(default)*

Uses **LCM Dreamshaper v7** (`SimianLuo/LCM_Dreamshaper_v7`) — a fantasy-art
tuned model running the LCM scheduler. Produces results in 4–8 steps instead
of 25–40, making it roughly 4–6× faster than Standard at comparable quality.

- **Recommended steps:** 4–8
- **Recommended CFG:** 1.0–2.0 (higher values degrade quality in LCM)
- **Negative prompts:** ignored by the LCM scheduler — cleared automatically
- Step and CFG sliders auto-adjust when you select this engine

### Standard SD 1.5 — `Standard SD 1.5`

Vanilla `runwayml/stable-diffusion-v1-5`. Slower but more controllable, with
full negative prompt support and the complete sampler selection.

- **Recommended steps:** 20–40
- **Recommended CFG:** 7–9
- **Samplers:** Euler, DPM++ 2M, LMS, PNDM

### sd.cpp — `sd.cpp (subprocess)`

Calls a locally compiled `stable-diffusion.cpp` binary as a subprocess. The
fastest option on CPU — the C++ implementation uses AVX2/AVX512 directly and
has negligible Python overhead.

**Build:**
```bash
git clone https://github.com/leejet/stable-diffusion.cpp
cd stable-diffusion.cpp
git submodule init && git submodule update --recursive
mkdir build && cd build
cmake .. -DGGML_AVX2=ON
cmake --build . --config Release -j$(nproc)
```

Place the binary at `~/sd.cpp/build/bin/sd` and a model at
`~/Mythotex/models/v1-5-pruned-emaonly.safetensors`.

- Progress is streamed from the subprocess to the progress bar
- The **Threads** spinner in the ENGINE tab controls `--threads`
  (defaults to CPU count − 1)

---

## Acceleration Options

All options live in the **⚡ ENGINE** tab. Changes take effect after
**⚡ RELOAD ENGINE**.

### INT8 Quantisation

Requires `optimum-quanto`. Quantises the UNet and text encoder weights to
INT8 in-place, halving their memory footprint and providing roughly 20%
faster inference on CPU.

```bash
pip install optimum-quanto
```

Disabled if the library is not installed. Quantisation runs at engine load
time — there is no per-generation overhead.

### torch.compile

Compiles the UNet with `torch.compile(mode="reduce-overhead")`. The first
generation after enabling this will be slow (kernel compilation and caching);
subsequent generations benefit from fused kernels. Recommended for long
sessions where the one-time warm-up cost is acceptable.

### 2× LANCZOS Upscale

Doubles image resolution with `PIL.Image.LANCZOS` resampling before
background removal. Gives `rembg` a larger, higher-quality input and results
in a sharper final PNG. Adds a second or two of CPU time.

### Background Removal (rembg)

Requires `rembg`. After generation the image is passed through the U2Net
model to produce a transparent-background RGBA PNG.

```bash
pip install rembg
```

The U2Net model (~170 MB) is downloaded on first use and cached thereafter.
Disabled if the library is not installed.

---

## The Ateliers

The sidebar lists 30 **Ateliers** — named workshops, each producing a
specific category of arcane object. Clicking an atelier triggers a full
generation cycle for that category.

```
╔══════════════════════════════╦════════════════════════════════════════════╗
║ Wing                         ║ Ateliers                                   ║
╠══════════════════════════════╬════════════════════════════════════════════╣
║ Written Arts                 ║ The Bureau of Scrollworks                  ║
║                              ║ The Cartographer's Scriptorium             ║
║                              ║ The Verba Arcanum                          ║
╠══════════════════════════════╬════════════════════════════════════════════╣
║ Staves & Focuses             ║ The Stavewrights Annex                     ║
║                              ║ The Channeller's Gallery                   ║
╠══════════════════════════════╬════════════════════════════════════════════╣
║ Vestments & Regalia          ║ The Weaver's Loom                          ║
║                              ║ The Hatter's Conjury                       ║
║                              ║ The Glover's Sanctum                       ║
╠══════════════════════════════╬════════════════════════════════════════════╣
║ Jewellery & Adornments       ║ The Jeweller's                             ║
║                              ║ The Sigillary                              ║
╠══════════════════════════════╬════════════════════════════════════════════╣
║ Vessels, Tools & Instruments ║ The Laborum Alchemica                      ║
║                              ║ The Glasswright's Athanor                  ║
║                              ║ The Sundial & Orrery Works                 ║
║                              ║ The Scriptorium of Instruments             ║
╠══════════════════════════════╬════════════════════════════════════════════╣
║ Relics & Constructed Objects ║ Arx Opus                                   ║
║                              ║ The Hall of Future Antiquities             ║
║                              ║ The Golem Foundry                          ║
╠══════════════════════════════╬════════════════════════════════════════════╣
║ Familiars & Living Things    ║ The Biogenica Nexus                        ║
║                              ║ The Expansum Botanica                      ║
╠══════════════════════════════╬════════════════════════════════════════════╣
║ Illumination & Fire          ║ The Lamplighter's Vault                    ║
║                              ║ The Pyroglyphic Chamber                    ║
╠══════════════════════════════╬════════════════════════════════════════════╣
║ Mirrors, Lenses & Scrying    ║ The Catoptric Hall                         ║
║                              ║ The Warden of Veils                        ║
╠══════════════════════════════╬════════════════════════════════════════════╣
║ Keys, Locks & Thresholds     ║ The Wardenship                             ║
║                              ║ The Cartouche Press                        ║
╠══════════════════════════════╬════════════════════════════════════════════╣
║ Music & Sound                ║ The Resonance Workshop                     ║
╠══════════════════════════════╬════════════════════════════════════════════╣
║ Games, Puzzles & Divination  ║ The Curio Cabinet                          ║
║                              ║ The House of Lots                          ║
║                              ║ The Horologium Arcanum                     ║
╠══════════════════════════════╬════════════════════════════════════════════╣
║ Containers & Storage         ║ The Cofferwright's Annex                   ║
║                              ║ The Bottleworks                            ║
╠══════════════════════════════╬════════════════════════════════════════════╣
║ Death, Memory & Binding      ║ The Ossuary Bindery                        ║
║                              ║ The Mnemorium                              ║
╚══════════════════════════════╩════════════════════════════════════════════╝
```

To add a new atelier, add an entry to `ATELIER_PRODUCTS` in `Mythotex.py`.
The key is the display name; the value is a prompt fragment passed to GPT.

---

## Generation Cycle

Each generation follows this sequence:

```
  1. GPT-4o      →  JSON lore entry
                    (title, description, history, aura, visual_keywords)
  2. SD pipeline →  512×512 RGB image
  3. LANCZOS 2×  →  1024×1024  (if enabled)
  4. rembg       →  RGBA transparent PNG
  5. Viewport    →  display + enable SEAL / REFORGE
```

The lore entry contains five fields:

```
╔══════════════════╦═══════════════════════════════════════════════════════╗
║ Field            ║ Description                                           ║
╠══════════════════╬═══════════════════════════════════════════════════════╣
║ title            ║ The object's proper name                              ║
╠══════════════════╬═══════════════════════════════════════════════════════╣
║ description      ║ One sentence — what it is                             ║
╠══════════════════╬═══════════════════════════════════════════════════════╣
║ history          ║ 2–4 sentences — provenance, lore, effects             ║
╠══════════════════╬═══════════════════════════════════════════════════════╣
║ aura             ║ A brief impression — sensory or atmospheric           ║
╠══════════════════╬═══════════════════════════════════════════════════════╣
║ visual_keywords  ║ 6–10 comma-separated visual descriptors fed           ║
║                  ║ directly into the SD prompt                           ║
╚══════════════════╩═══════════════════════════════════════════════════════╝
```

`visual_keywords` is the bridge between the lore engine and the image engine.
GPT is prompted to think like an illustrator: materials, textures, colours,
shapes, surface treatments — not narrative adjectives.

---

## Prompt Architecture

### Positive prompt structure

```
{title}, {description}, {visual_keywords (up to 3)},
3d rendered fantasy illustration, volumetric lighting,
painted surface detail, studio white background,
jewel-tone colours, warm amber teal palette, sharp focus
[+ 1 favoured DNA hint if available]
```

The prompt is kept under **77 tokens** — CLIP's hard limit. Anything past
token 77 is silently truncated. The style boilerplate consumes ~30 tokens,
leaving ~40 for subject and keywords.

### Negative prompt structure

```
photograph, photorealistic, 3d render, CGI,
flat colors, cel shading, anime, cartoon,
busy background, multiple objects, human figure, person,
blurry, watermark, text, deformed, bad anatomy
[+ 1 forbidden DNA hint if available]
```

Negative prompts are **ignored in LCM mode** — the LCM scheduler doesn't
use them. They are cleared automatically when LCM is active.

---

## The Vault

Generated items are reviewed in the **Compendium Tome**
(`◎ COMPENDIUM TOME` button). Each entry shows the illustration thumbnail,
title, description, and aura, with a 1–5 star rating for **stylistic
integrity** (visual tone only, not lore quality).

Ratings feed directly into the **Aesthetic DNA**:

- **4–5 stars** → description added to `dna["favored"]`
- **1–2 stars** → description added to `dna["forbidden"]`

The most recent favoured hint is appended to the positive prompt on the next
generation. The most recent forbidden hint is appended to the negative prompt.

To **seal** an item, click **SEAL IN VAULT**. Unsealed items exist only as
`temp_manifest.png` and will be overwritten on the next generation.

---

## Self-Refining Analysis Engine

The `AnalysisWorker` runs off the main thread and triggers automatically:

```
╔══════════════════════╦══════════════════════════════════════════════════╗
║ Trigger              ║ Condition                                        ║
╠══════════════════════╬══════════════════════════════════════════════════╣
║ Vault threshold      ║ Every N seals         (default: 5)               ║
╠══════════════════════╬══════════════════════════════════════════════════╣
║ Periodic threshold   ║ Every N generations   (default: 10)              ║
╚══════════════════════╩══════════════════════════════════════════════════╝
```

Both thresholds are configurable in the **GPT ORACLE** tab.

When triggered, the engine reviews the last 20 vault entries and their
ratings, then asks GPT-4o to produce a revised strategy document with two
sections: **LORE GENERATION STRATEGY** and **SD PROMPT STRATEGY**. This is
appended to `lore_mutable.md` with a timestamp and included in the system
prompt for all subsequent lore generations.

---

## Control Panel Reference

Open with **⚙ RITUAL PARAMETERS**. The panel slides out from the right edge.

### ⚡ ENGINE tab

```
╔══════════════════════╦══════════════════════════════════════════════════╗
║ Control              ║ Description                                      ║
╠══════════════════════╬══════════════════════════════════════════════════╣
║ Inference engine     ║ LCM / Standard SD 1.5 / sd.cpp                   ║
╠══════════════════════╬══════════════════════════════════════════════════╣
║ INT8 quantisation    ║ Halves model memory; ~20% faster.                ║
║                      ║ Requires optimum-quanto                          ║
╠══════════════════════╬══════════════════════════════════════════════════╣
║ torch.compile        ║ Fused kernels after first-run warm-up            ║
╠══════════════════════╬══════════════════════════════════════════════════╣
║ 2× LANCZOS upscale   ║ Doubles resolution before BG removal             ║
╠══════════════════════╬══════════════════════════════════════════════════╣
║ Remove background    ║ rembg transparent PNG output. Requires rembg     ║
╠══════════════════════╬══════════════════════════════════════════════════╣
║ Threads              ║ CPU thread count for sd.cpp subprocess           ║
╚══════════════════════╩══════════════════════════════════════════════════╝
```

### SD FORGE tab

```
╔══════════════╦════════════════╦═════════════╦══════════════════╗
║ Control      ║ Range          ║ LCM default ║ Standard default ║
╠══════════════╬════════════════╬═════════════╬══════════════════╣
║ Steps        ║ 1–60           ║ 6           ║ 28               ║
╠══════════════╬════════════════╬═════════════╬══════════════════╣
║ CFG          ║ 1–20           ║ 2           ║ 8                ║
╠══════════════╬════════════════╬═════════════╬══════════════════╣
║ Width        ║ 256–768 (×64)  ║ 512         ║ 512              ║
╠══════════════╬════════════════╬═════════════╬══════════════════╣
║ Height       ║ 256–768 (×64)  ║ 512         ║ 512              ║
╠══════════════╬════════════════╬═════════════╬══════════════════╣
║ Sampler      ║ Euler /        ║ —           ║ Euler            ║
║              ║ DPM++ 2M /     ║             ║                  ║
║              ║ LMS / PNDM     ║             ║                  ║
╠══════════════╬════════════════╬═════════════╬══════════════════╣
║ Seed         ║ −1 to 2³¹−1   ║ −1 (random) ║ −1 (random)      ║
╚══════════════╩════════════════╩═════════════╩══════════════════╝
```

SD 1.5 was trained at 512×512. Going above 512px in Standard mode can
introduce compositional drift (duplicate subjects, merged objects). LCM is
more tolerant of higher resolutions.

### GPT ORACLE tab

```
╔══════════════════════╦══════════════════════════════════════════════════╗
║ Control              ║ Description                                      ║
╠══════════════════════╬══════════════════════════════════════════════════╣
║ Model                ║ gpt-4o / gpt-4o-mini / gpt-4-turbo /            ║
║                      ║ gpt-3.5-turbo                                    ║
╠══════════════════════╬══════════════════════════════════════════════════╣
║ Temperature          ║ 0.0–2.0 (default 1.0) — lore creativity         ║
╠══════════════════════╬══════════════════════════════════════════════════╣
║ Vault threshold      ║ Trigger analysis every N seals                   ║
╠══════════════════════╬══════════════════════════════════════════════════╣
║ Periodic threshold   ║ Trigger analysis every N generations             ║
╚══════════════════════╩══════════════════════════════════════════════════╝
```

---

## Workflow: REFORGE VISUAL

**REFORGE VISUAL** re-runs image generation on the current lore entry with
a new random seed, without calling GPT again. Use this when the lore is good
but the image missed the mark. Each reforge costs only SD inference time.

---

## Troubleshooting

**`HSA_OVERRIDE_GFX_VERSION` / ROCm not detected**
The Raphael iGPU (0x164e) may require `HSA_OVERRIDE_GFX_VERSION=10.3.0`
set before launch for PyTorch ROCm to recognise the device.

**Prompt truncation warning (`147 > 77`)**
CLIP's tokeniser hard-caps at 77 tokens. The prompt is budgeted to stay
under this limit, but `visual_keywords` from GPT can occasionally push past
it. The excess is silently truncated — not an error, but those tokens have
no effect on the image.

**sd.cpp: `ggml` submodule missing**
```bash
cd stable-diffusion.cpp
git submodule init && git submodule update --recursive
```
Delete `build/` and re-run cmake.

**`callback` / `callback_steps` FutureWarning**
Harmless in current versions. The new `callback_on_step_end` API is used.
If the warning persists, upgrade diffusers: `pip install -U diffusers`.

**`transformer_kandinsky` autocast warnings**
Harmless — diffusers imports that file transitively regardless of which
pipeline is loaded. No action needed.

---

## Dependencies

```
╔══════════════════╦══════════════════════════════════════╦═════════════╗
║ Package          ║ Purpose                              ║ Required    ║
╠══════════════════╬══════════════════════════════════════╬═════════════╣
║ torch            ║ Tensor compute, model inference      ║ Yes         ║
╠══════════════════╬══════════════════════════════════════╬═════════════╣
║ diffusers        ║ SD pipeline, schedulers              ║ Yes         ║
╠══════════════════╬══════════════════════════════════════╬═════════════╣
║ transformers     ║ CLIP tokeniser / text encoder        ║ Yes         ║
╠══════════════════╬══════════════════════════════════════╬═════════════╣
║ accelerate       ║ Model loading optimisations          ║ Yes         ║
╠══════════════════╬══════════════════════════════════════╬═════════════╣
║ openai           ║ GPT lore generation                  ║ Yes         ║
╠══════════════════╬══════════════════════════════════════╬═════════════╣
║ PyQt6            ║ Desktop UI                           ║ Yes         ║
╠══════════════════╬══════════════════════════════════════╬═════════════╣
║ Pillow           ║ Image I/O, LANCZOS upscale           ║ Yes         ║
╠══════════════════╬══════════════════════════════════════╬═════════════╣
║ rembg            ║ Background removal (U2Net)           ║ Recommended ║
╠══════════════════╬══════════════════════════════════════╬═════════════╣
║ optimum-quanto   ║ INT8 quantisation                    ║ Recommended ║
╚══════════════════╩══════════════════════════════════════╩═════════════╝
```

---

*Mythotex is a component of the Arca Cognitarium project.*
