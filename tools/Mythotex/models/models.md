# ╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌
# ⯨                                                                         ⯩
# ⯨   𝐀𝐍𝐍𝐔𝐒 🟌 ＭＭＸＸＶＩ                                      MODELS.md   ⯩
# ⯨                                                                         ⯩
# ╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌

# Mythotex — Model Grimoire
## SD 1.5 Architecture — Drop-in `.safetensors` for `~/ArcaCognitorium/tools/Mythotex/models/`

All models below are SD 1.5 arch — same binary, same flags, zero code changes.
Drop file → restart app → appears in Model dropdown.

---

## ★★★★★  TIER 1 — HIGHEST PRIORITY FOR YOUR AESTHETIC

### Inkpunk Diffusion v2
**Target style:** Punk woodcut, Gorillaz-esque, rough ink, high energy linework
**Why it matters:** The single best SD 1.5 model for bold outlined graphic illustration.
Trained on dreambooth, heavily influenced by Gorillaz, FLCL, Yoji Shinkawa.
Trigger token required: **`nvinkpunk`** — add to every positive prompt.
**CFG:** 7–9 (lower than you'd think — it's heavily biased already)
**Steps:** 20–30, euler_a
**Source:** https://huggingface.co/Envvi/Inkpunk-Diffusion
**Civitai:** https://civitai.com/models/1087/inkpunk-diffusion
**File:** `inkpunk-diffusion-v2.safetensors` (~2.1 GB)

> ⚠ Note: Add `nvinkpunk` to your positive prompts in Mythotex's `STYLE_PRESETS`
> when using this model. The Inkpunk preset already has the style tokens —
> just prepend `nvinkpunk,` to the positive string.

---

### DreamShaper v8
**Target style:** Illustration-first generalist. Fantasy, surreal, painterly illustration.
Not a linework model, but extraordinarily good at arcane/fantasy object rendering.
The best "does everything well" SD 1.5 model. Use when you want lush artifact imagery
over crisp linework.
**CFG:** 7–10, CLIP skip 2
**Steps:** 25–35, euler_a or dpm++2m
**Source:** https://huggingface.co/Lykon/DreamShaper
**Civitai:** https://civitai.com/models/4384/dreamshaper
**File:** `dreamshaper_8.safetensors` (~2.1 GB)

---

## ★★★★☆  TIER 2 — STRONG ALTERNATES

### Deliberate v3
**Target style:** Detailed illustration, concept art, strong object rendering.
Clean, sharp, handles isolated objects on white backgrounds well.
No special trigger token needed.
**CFG:** 10–14
**Steps:** 25–40, euler_a or dpm++2s_a
**Civitai:** https://civitai.com/models/4823/deliberate
**File:** `deliberate_v3.safetensors` (~2.1 GB)

---

### ToonYou Beta 6
**Target style:** Cel-shaded cartoon, flat colour fills, clean outlines. 
Closest to the Enamel Pin preset aesthetic of any SD 1.5 model.
VAE included in the file from Beta 2 onward.
**CFG:** 7–8 (model is opinionated — don't push CFG high)
**Steps:** 20–28, euler_a
**CLIP skip:** 2
**Civitai:** https://civitai.com/models/30240/toonyou
**File:** `toonyou_beta6.safetensors` (~2.1 GB)

---

### NeverEnding Dream (NED)
**Target style:** Dreamlike, surreal, illustrative. Strong on atmospheric dark fantasy.
Handles unusual object compositions well. Good for Atelier Umbrae / Atelier Maris.
**CFG:** 7–12
**Steps:** 20–35, euler_a
**Source:** https://huggingface.co/Lykon/neverending-dream-ned
**File:** `neverEndingDream_v122.safetensors` (~2.1 GB)

---

### Analog Diffusion
**Target style:** Grungy analog/film aesthetic with strong contrast.
Good for Atelier Ossium, Atelier Sanguinis — aged, physical, tactile objects.
Trigger token: **`analog style`**
**CFG:** 8–12
**Steps:** 20–30
**Source:** https://huggingface.co/wavymulder/Analog-Diffusion
**File:** `analog-diffusion-1.0.safetensors` (~2.1 GB)

---

## ★★★☆☆  TIER 3 — SITUATIONAL / EXPERIMENTAL

### DreamLike Diffusion 1.0
**Target style:** Soft painterly fantasy illustration. Like an oil painting of your artifact.
Not great for linework but stunning for purely painterly arcana.
Trigger token: **`dreamlikeart`**
**Civitai/HF:** https://huggingface.co/dreamlike-art/dreamlike-diffusion-1.0
**File:** `dreamlike-diffusion-1.0.safetensors` (~2.1 GB)

---

### epiCRealism
**Target style:** Hyperrealistic. Not your primary target but excellent for
Atelier Ferrum clockwork objects — makes metal/mechanical objects look physically real.
**CFG:** 5–8
**Steps:** 30–40, dpm++2m karras
**Civitai:** https://civitai.com/models/25694/epicrealism
**File:** `epicrealism_naturalSin.safetensors` (~2.1 GB)

---

### Meinamix / MeinaMix v11
**Target style:** Anime-adjacent illustration with strong flat colour and outline.
Closer to the Enamel Pin / Silhouette aesthetic than pure anime. Surprisingly versatile.
**CFG:** 7–9, CLIP skip 2
**Steps:** 20–30
**Civitai:** https://civitai.com/models/7240/meinamix
**File:** `meinamix_meinaV11.safetensors` (~2.1 GB)

---

## LoRA SUPPLEMENTS (stack on top of any base model)

These are small files (~50–150 MB) that steer an existing checkpoint.
Place in the same models directory — sd-cli supports `--lora` flag.

| LoRA | Effect | Token | Source |
|------|--------|-------|--------|
| Anime Lineart / Manga Style | Forces hard ink outlines | `lineart` | civitai/16014 |
| Western Comics Style v2 | 1970s-80s eurocomics, limited palette | — | civitai |
| Retro Vintage Comics | Vintage newsprint comic ink | — | civitai |
| Organic Abstract Minimalism | Lino-cut style minimal forms | — | civitai |
| Brushstrokes (over-inked linocut) | Rough over-inked lino aesthetic | — | civitai |

> To use a LoRA with sd-cli, add to your subprocess cmd:
> `"--lora", "path/to/lora.safetensors", "--lora-multiplier", "0.7"`

---

## QUICK DECISION TREE

```
Want bold linework / woodcut?     → Inkpunk Diffusion v2  (+ nvinkpunk token)
Want enamel pin / cel shaded?     → ToonYou Beta 6
Want lush arcane illustration?    → DreamShaper v8
Want dark/grungy/aged objects?    → Analog Diffusion  (+ analog style token)
Want hyperreal metal/clockwork?   → epiCRealism
Want everything / experimenting?  → DreamShaper v8 (safe default)
```

---

## DOWNLOAD COMMANDS (wget from HuggingFace)

```bash
cd ~/ArcaCognitorium/tools/Mythotex/models/

# Inkpunk Diffusion v2 (PRIMARY — get this first)
wget -O inkpunk-diffusion-v2.safetensors \
  "https://huggingface.co/Envvi/Inkpunk-Diffusion/resolve/main/Inkpunk-Diffusion-v2.ckpt"

# DreamShaper v8
wget -O dreamshaper_8.safetensors \
  "https://huggingface.co/Lykon/DreamShaper/resolve/main/DreamShaper_8_pruned.safetensors"

# NeverEnding Dream
wget -O neverEndingDream.safetensors \
  "https://huggingface.co/Lykon/neverending-dream-ned/resolve/main/NeverEndingDream_v122.safetensors"

# Analog Diffusion
wget -O analog-diffusion-1.0.safetensors \
  "https://huggingface.co/wavymulder/Analog-Diffusion/resolve/main/analog-diffusion-1.0.ckpt"
```

> Deliberate v3, ToonYou, epiCRealism, Meinamix — download via Civitai
> (requires free account login for the direct file link).
> https://civitai.com → search model name → Files tab → Download .safetensors
