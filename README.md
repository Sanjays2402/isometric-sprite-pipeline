# 🎮 Isometric Sprite Pipeline

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat&logo=python&logoColor=white)
![fal.ai](https://img.shields.io/badge/fal.ai-API-FF6B6B?style=flat)
![License](https://img.shields.io/badge/License-MIT-green?style=flat)

Generate **Final Fantasy Tactics-style isometric 8-way turnaround sprites** from a single side-view reference image — using **Nano Banana 2** for image generation and **Veo 3.1 Fast** for walk-cycle animation, all via [fal.ai](https://fal.ai/).

Based on the workflow from [@chongdashu's article](https://x.com/chongdashu/status/2037109734445084684).

## ✨ Features

- 🖼️ Single input image → full 8-way isometric turnaround sheet
- 🎬 Automatic walk-cycle animation via Veo 3.1 Fast
- 🪞 Deterministic mirroring for consistent West-facing sprites
- 🎯 Staged generation (anchor → cardinals → diagonals) for reliability
- 📐 Configurable sprite height normalization
- 🟢 Chroma-key green background removal

## 🔄 Pipeline Overview

```
Side-view sprite (your input)
        │
   Nano Banana 2 — one SE isometric anchor
        │
   Nano Banana 2 — 4 cardinal facings (N/S/E/W)
        │
   Nano Banana 2 — 4 diagonal facings from cardinals
        │
   Deterministic assembly — mirror, normalize, combine
        │
   8-way isometric turnaround sheet
        │
   Veo 3.1 Fast — walk animation from SW anchor
```

## 🚀 Setup

```bash
cd isometric-sprite-pipeline
pip install -r requirements.txt
```

Set your fal.ai API key:

```bash
export FAL_KEY="your-fal-ai-key-here"
```

Get a key at [fal.ai/dashboard/keys](https://fal.ai/dashboard/keys).

## 📖 Usage

### Full Pipeline (end-to-end)

```bash
python pipeline.py run --input my_sprite.png --output-dir ./output
```

Options:
- `--target-height 128` — normalize all sprites to a specific pixel height
- `--skip-animation` — skip the Veo 3.1 walk animation step
- `--no-mirror-west` — don't mirror East → West (not recommended)

### Assembly Only (from pre-generated sheets)

If you've already generated cardinal and diagonal sheets (manually or from a previous run):

```bash
python pipeline.py assemble \
  --cardinals output/stage2_cardinals.png \
  --diagonals output/stage3_diagonals.png \
  --anchor output/stage1_anchor_se.png \
  --output-dir ./output
```

### Animate Only

Generate a walk-cycle animation from any sprite frame:

```bash
python pipeline.py animate --sprite output/sw_frame.png --output-dir ./output
```

## 📁 Output Files

| File | Description |
|------|-------------|
| `stage1_anchor_se.png` | SE-facing isometric anchor (approved before proceeding) |
| `stage2_cardinals.png` | 2×2 sheet: N, E, W, S cardinal facings |
| `stage3_diagonals.png` | 2×2 sheet: NW, NE, SW, SE diagonal facings |
| `turnaround_8way.png` | Final assembled 8-way turnaround sheet |
| `sw_frame.png` | Extracted SW frame used for animation |
| `walk_cycle.mp4` | Walk-cycle animation from Veo 3.1 |

## 💡 Key Lessons from the Article

1. **One-shot turnarounds don't work** — staged (anchor → cardinals → diagonals) is what makes it reliable
2. **Mirror, don't re-prompt** — West kept drifting, so we deterministically mirror East
3. **Semantic descriptions beat compass labels** — "mostly back, plus left side" > "NW"
4. **Use `#00FF00` chroma-key green** — not magenta (too close to red accessories)
5. **Consistency > peak quality** — Nano Banana 2 is more predictable than GPT Image 1.5 across runs

## 🏗️ Project Structure

```
isometric-sprite-pipeline/
├── pipeline.py      # CLI entry point — full pipeline, assemble, animate
├── fal_api.py       # fal.ai API client (image gen + video gen)
├── assembly.py      # Deterministic assembly (chroma removal, crop, mirror, normalize, compose)
├── prompts.py       # All prompt templates for each stage
├── requirements.txt
├── pyproject.toml
└── output/          # Generated assets go here
```

## 👤 Author

**Sanjay Santhanam**
