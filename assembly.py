"""
Deterministic assembly — Stage 4 of the pipeline.

Handles: chroma-key removal, cropping, mirroring East→West,
baseline normalization, and final 8-way sheet composition.
"""

from PIL import Image


# ── Chroma-Key Removal ───────────────────────────────────────────────────────

def remove_chroma_key(
    img: Image.Image,
    key_color: tuple[int, int, int] = (0, 255, 0),
    tolerance: int = 60,
) -> Image.Image:
    """Replace #00FF00 chroma-key green with transparency."""
    img = img.convert("RGBA")
    pixels = img.load()
    w, h = img.size
    for y in range(h):
        for x in range(w):
            r, g, b, a = pixels[x, y]
            dr = abs(r - key_color[0])
            dg = abs(g - key_color[1])
            db = abs(b - key_color[2])
            if dr + dg + db < tolerance:
                pixels[x, y] = (0, 0, 0, 0)
    return img


# ── Auto-crop to content ─────────────────────────────────────────────────────

def auto_crop(img: Image.Image, padding: int = 2) -> Image.Image:
    """Crop to the bounding box of non-transparent pixels with optional padding."""
    bbox = img.getbbox()
    if bbox is None:
        return img
    left, upper, right, lower = bbox
    left = max(0, left - padding)
    upper = max(0, upper - padding)
    right = min(img.width, right + padding)
    lower = min(img.height, lower + padding)
    return img.crop((left, upper, right, lower))


# ── Split a 2×2 Grid ─────────────────────────────────────────────────────────

def split_grid_2x2(sheet: Image.Image) -> list[Image.Image]:
    """Split a 2×2 sprite sheet into 4 individual sprites (TL, TR, BL, BR)."""
    w, h = sheet.size
    hw, hh = w // 2, h // 2
    return [
        sheet.crop((0, 0, hw, hh)),       # top-left
        sheet.crop((hw, 0, w, hh)),        # top-right
        sheet.crop((0, hh, hw, h)),        # bottom-left
        sheet.crop((hw, hh, w, h)),        # bottom-right
    ]


# ── Mirror (for fixing West from East) ───────────────────────────────────────

def mirror_horizontal(img: Image.Image) -> Image.Image:
    return img.transpose(Image.Transpose.FLIP_LEFT_RIGHT)


# ── Normalize sprites to consistent baseline and size ─────────────────────────

def normalize_sprites(
    sprites: dict[str, Image.Image],
    target_height: int | None = None,
) -> dict[str, Image.Image]:
    """
    Normalize all sprites to:
    - Same height (scaled proportionally)
    - Same canvas size (max_width × target_height)
    - Bottom-aligned (baseline normalization)
    """
    # Auto-crop each sprite first
    cropped = {d: auto_crop(s) for d, s in sprites.items()}

    # Determine target height
    if target_height is None:
        target_height = max(s.height for s in cropped.values())

    # Scale proportionally to target height
    scaled: dict[str, Image.Image] = {}
    for direction, sprite in cropped.items():
        if sprite.height == 0:
            scaled[direction] = sprite
            continue
        scale = target_height / sprite.height
        new_w = max(1, int(sprite.width * scale))
        scaled[direction] = sprite.resize(
            (new_w, target_height), Image.Resampling.NEAREST
        )

    # Find max width for uniform canvas
    max_w = max(s.width for s in scaled.values())

    # Center each sprite on a uniform canvas, bottom-aligned
    result: dict[str, Image.Image] = {}
    for direction, sprite in scaled.items():
        canvas = Image.new("RGBA", (max_w, target_height), (0, 0, 0, 0))
        x_offset = (max_w - sprite.width) // 2
        y_offset = target_height - sprite.height  # bottom-align
        canvas.paste(sprite, (x_offset, y_offset), sprite)
        result[direction] = canvas

    return result


# ── Compose the final 8-way turnaround sheet ──────────────────────────────────

# Layout order (standard 8-way isometric):
#   Row 0: N,  NE, E
#   Row 1: NW, --  SE
#   Row 2: W,  SW, S
# Or simpler 2-row / 1-row:

DIRECTION_ORDER_ROW = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]


def assemble_turnaround_sheet(
    sprites: dict[str, Image.Image],
    columns: int = 8,
    spacing: int = 4,
) -> Image.Image:
    """
    Assemble 8 directional sprites into a horizontal turnaround sheet.
    Order: N, NE, E, SE, S, SW, W, NW
    """
    ordered = [sprites[d] for d in DIRECTION_ORDER_ROW]

    cell_w = max(s.width for s in ordered)
    cell_h = max(s.height for s in ordered)

    rows = (len(ordered) + columns - 1) // columns
    sheet_w = columns * cell_w + (columns - 1) * spacing
    sheet_h = rows * cell_h + (rows - 1) * spacing

    sheet = Image.new("RGBA", (sheet_w, sheet_h), (0, 0, 0, 0))

    for i, sprite in enumerate(ordered):
        col = i % columns
        row = i // columns
        x = col * (cell_w + spacing) + (cell_w - sprite.width) // 2
        y = row * (cell_h + spacing) + (cell_h - sprite.height)
        sheet.paste(sprite, (x, y), sprite)

    return sheet


def assemble_pipeline(
    cardinal_sheet: Image.Image,
    diagonal_sheet: Image.Image,
    anchor_se: Image.Image | None = None,
    mirror_west: bool = True,
    target_height: int | None = None,
) -> Image.Image:
    """
    Full deterministic assembly from cardinal + diagonal sheets.

    Cardinal sheet layout (2×2): TL=North, TR=East, BL=West, BR=South
    Diagonal sheet layout (2×2): TL=NW, TR=NE, BL=SW, BR=SE

    If mirror_west=True, West is replaced with a mirrored East (the article's fix).
    If anchor_se is provided and better quality, it replaces the diagonal SE.
    """
    # Split sheets
    c_n, c_e, c_w, c_s = split_grid_2x2(cardinal_sheet)
    d_nw, d_ne, d_sw, d_se = split_grid_2x2(diagonal_sheet)

    # Remove chroma key from all
    sprites_raw = {
        "N": remove_chroma_key(c_n),
        "E": remove_chroma_key(c_e),
        "W": remove_chroma_key(c_w),
        "S": remove_chroma_key(c_s),
        "NW": remove_chroma_key(d_nw),
        "NE": remove_chroma_key(d_ne),
        "SW": remove_chroma_key(d_sw),
        "SE": remove_chroma_key(d_se),
    }

    # Mirror East → West fix (article: "West kept drifting")
    if mirror_west:
        sprites_raw["W"] = mirror_horizontal(sprites_raw["E"])

    # Use the approved anchor for SE if provided
    if anchor_se is not None:
        sprites_raw["SE"] = remove_chroma_key(anchor_se)

    # Normalize all to consistent baseline and height
    sprites = normalize_sprites(sprites_raw, target_height=target_height)

    # Assemble final sheet
    return assemble_turnaround_sheet(sprites)
