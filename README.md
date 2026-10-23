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

## Terms & Disclaimer

By using this project you agree to the following.

- **No warranty.** This software is provided "as is", without warranty of any kind, express or implied, including merchantability, fitness for a particular purpose, and non-infringement.
- **No liability.** To the maximum extent permitted by law, the author and contributors are not liable for any claim, loss, or damage (direct, indirect, incidental, or consequential, including lost data or profits) arising from its use.
- **Your responsibility.** You use it at your own risk and are responsible for complying with the laws that apply to you.
- **AI output.** Generated content can be inaccurate, biased, or offensive. Review it before relying on or sharing it. Third-party AI providers or models you use process your input under their own terms.
- **Third parties.** Names, logos, APIs, and services of others belong to their owners and are used for identification only; no affiliation or endorsement is implied.
- **Your statutory rights.** Nothing here limits rights that cannot be waived by agreement, including under consumer-protection laws in the USA, Canada (including Quebec), and India (Consumer Protection Act, 2019).
- **License.** Use, copying, and distribution are governed by the [LICENSE](LICENSE) file; if anything here conflicts with it, the license controls.

## Content, Assets & Fair Use

- **Original work.** Unless noted otherwise (including below), the code, text, design, and images in this repository were created by the author.
- **Libraries, fonts, and icons.** Third-party libraries, fonts (for example Google Fonts), and icon sets belong to their creators and are used under their own licenses; see the dependency manifests and each source for terms.
- **Logos, brands, and screenshots.** Third-party names, logos, and screenshots appear only to identify or describe their products (nominative use). They remain the property of their owners and do not imply affiliation or endorsement.
- **Ideas and inspiration.** Where this project is inspired by another product, game, or idea, it is an independent implementation. It borrows only general ideas, mechanics, or styles, which are not anyone's exclusive property, and is meant to contain no third-party code or artwork used without permission.
- **AI-generated content.** Some outputs are produced by AI models. They may resemble existing works by chance; check them before any public or commercial use.
- **Fair use and fair dealing.** Any third-party material is used in limited ways for purposes such as education, research, review, commentary, or identification, relying on fair use in the USA (17 U.S.C. § 107), fair dealing in Canada (Copyright Act, ss. 29–29.2), and fair dealing in India (Copyright Act, 1957, s. 52), where they apply.
- **Concerns and takedown requests.** If you own rights in something here and believe it is used improperly, [open an issue](https://github.com/Sanjays2402/isometric-sprite-pipeline/issues) or contact the author through their GitHub profile with a link to the material and your claim. It will be reviewed promptly and credited, changed, or removed as appropriate. You may also use GitHub's DMCA process.
- **Contributions.** By contributing, you confirm you have the right to submit your contribution and agree it is licensed under this repository's license.
