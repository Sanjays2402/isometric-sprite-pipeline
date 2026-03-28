"""
Prompt templates for each stage of the isometric sprite pipeline.

All prompts follow the article's lessons:
- Use #00FF00 chroma-key green (not magenta) for Nano Banana 2
- Use semantic slot descriptions for diagonals (not just compass labels)
- Request consistent proportions and character identity
"""

# ── Stage 1: SE Isometric Anchor ─────────────────────────────────────────────

ANCHOR_SE = (
    "Reinterpret this side-view pixel art character as a single isometric "
    "sprite facing south-east (SE). Final Fantasy Tactics style, "
    "chibi proportions, 3/4 top-down view. "
    "Preserve exact character details: same outfit colors, accessories, "
    "body proportions, and readable face. "
    "Flat #00FF00 chroma-key green background, no gradients, no shadows, no spill. "
    "Single character only, centered, clean pixel edges."
)

# ── Stage 2: Four Cardinal Facings ───────────────────────────────────────────

CARDINALS = (
    "Using this approved SE isometric anchor as the character reference, "
    "generate a 2×2 sprite sheet of the SAME character in 4 cardinal "
    "isometric facings: North (back view), South (front view), "
    "East (right side view), West (left side view). "
    "Final Fantasy Tactics style, chibi proportions, 3/4 top-down view. "
    "Each sprite must preserve exact character identity: same outfit colors, "
    "accessories, body proportions. "
    "Flat #00FF00 chroma-key green background. No gradients, no shadows, no spill. "
    "4 separate characters in a 2×2 grid, evenly spaced, clean pixel edges. "
    "Top-left: North, Top-right: East, Bottom-left: West, Bottom-right: South."
)

# ── Stage 3: Four Diagonal Facings ───────────────────────────────────────────
# Key insight: semantic descriptions beat compass labels

DIAGONALS = (
    "Using the approved SE anchor and the 4 cardinal facings sheet as reference, "
    "generate a 2×2 sprite sheet of the SAME character in 4 diagonal "
    "isometric facings. Final Fantasy Tactics style, chibi proportions, "
    "3/4 top-down view. "
    "The 4 diagonal directions with semantic descriptions: "
    "NW = mostly back, plus left side visible; "
    "NE = mostly back, plus right side visible; "
    "SW = mostly front, plus left side visible; "
    "SE = mostly front, plus right side visible. "
    "Each sprite must preserve exact character identity: same outfit colors, "
    "accessories, body proportions. "
    "Flat #00FF00 chroma-key green background. No gradients, no shadows, no spill. "
    "4 separate characters in a 2×2 grid, evenly spaced, clean pixel edges. "
    "Top-left: NW, Top-right: NE, Bottom-left: SW, Bottom-right: SE."
)

# ── Walk Animation ───────────────────────────────────────────────────────────

WALK_ANIMATION = (
    "This is an isometric pixel art character sprite facing south-west. "
    "Animate a smooth walk cycle loop. The character walks in place with "
    "natural body movement: arms swing, legs step, slight torso bob. "
    "Maintain the exact character design, pixel art style, and facing direction. "
    "Keep the background transparent or solid green #00FF00. "
    "Smooth, game-ready looping animation."
)
