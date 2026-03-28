"""
Isometric Sprite Pipeline — CLI

Reproduces the workflow from @chongdashu's article:
  Side-view sprite → SE anchor → Cardinals → Diagonals → Assembly → Walk animation

All image generation via fal.ai (Nano Banana 2). Walk animation via Veo 3.1 Fast.
Deterministic steps (mirror, normalize, compose) in Python/Pillow.

Usage:
    python pipeline.py run --input sprite.png --output-dir ./output
    python pipeline.py assemble --cardinals cardinals.png --diagonals diagonals.png --output-dir ./output
    python pipeline.py animate --sprite sw_sprite.png --output-dir ./output
"""

import sys
from pathlib import Path

import click
from PIL import Image

from assembly import (
    assemble_pipeline,
    remove_chroma_key,
    auto_crop,
)
from fal_api import (
    generate_image,
    generate_video,
    download_video,
    load_image,
    save_image,
)
from prompts import ANCHOR_SE, CARDINALS, DIAGONALS, WALK_ANIMATION


@click.group()
def cli():
    """Isometric Sprite Pipeline — FFT-style 8-way turnaround sheet generator."""
    pass


# ── Full Pipeline ─────────────────────────────────────────────────────────────

@cli.command()
@click.option("--input", "input_path", required=True, type=click.Path(exists=True),
              help="Path to the source side-view sprite image.")
@click.option("--output-dir", default="./output", type=click.Path(),
              help="Directory for all output files.")
@click.option("--target-height", default=None, type=int,
              help="Normalize all sprites to this height (pixels).")
@click.option("--skip-animation", is_flag=True, help="Skip the Veo 3.1 walk animation step.")
@click.option("--mirror-west/--no-mirror-west", default=True,
              help="Mirror East to fix West (recommended).")
def run(input_path, output_dir, target_height, skip_animation, mirror_west):
    """Run the full pipeline: reference → anchor → cardinals → diagonals → sheet → animation."""
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    reference = load_image(input_path)
    click.echo(f"[1/5] Loaded reference sprite: {input_path}")

    # ── Stage 1: SE Anchor ───────────────────────────────────────────────
    click.echo("[2/5] Generating SE isometric anchor (Nano Banana 2)...")
    anchor_results = generate_image(ANCHOR_SE, reference_image=reference)
    if not anchor_results:
        click.echo("ERROR: No anchor image generated.", err=True)
        sys.exit(1)
    anchor_se = anchor_results[0]
    save_image(anchor_se, out / "stage1_anchor_se.png")
    click.echo(f"      Saved: {out / 'stage1_anchor_se.png'}")

    # ── Stage 2: Cardinals ───────────────────────────────────────────────
    click.echo("[3/5] Generating 4 cardinal facings (N/S/E/W)...")
    cardinal_results = generate_image(CARDINALS, reference_image=anchor_se)
    if not cardinal_results:
        click.echo("ERROR: No cardinal sheet generated.", err=True)
        sys.exit(1)
    cardinal_sheet = cardinal_results[0]
    save_image(cardinal_sheet, out / "stage2_cardinals.png")
    click.echo(f"      Saved: {out / 'stage2_cardinals.png'}")

    # ── Stage 3: Diagonals ───────────────────────────────────────────────
    click.echo("[4/5] Generating 4 diagonal facings (NW/NE/SW/SE)...")
    diagonal_results = generate_image(DIAGONALS, reference_image=anchor_se)
    if not diagonal_results:
        click.echo("ERROR: No diagonal sheet generated.", err=True)
        sys.exit(1)
    diagonal_sheet = diagonal_results[0]
    save_image(diagonal_sheet, out / "stage3_diagonals.png")
    click.echo(f"      Saved: {out / 'stage3_diagonals.png'}")

    # ── Stage 4: Deterministic Assembly ──────────────────────────────────
    click.echo("[5/5] Assembling 8-way turnaround sheet...")
    final_sheet = assemble_pipeline(
        cardinal_sheet=cardinal_sheet,
        diagonal_sheet=diagonal_sheet,
        anchor_se=anchor_se,
        mirror_west=mirror_west,
        target_height=target_height,
    )
    save_image(final_sheet, out / "turnaround_8way.png")
    click.echo(f"      Saved: {out / 'turnaround_8way.png'}")

    # ── Optional: Walk Animation ─────────────────────────────────────────
    if not skip_animation:
        click.echo("[BONUS] Generating walk animation with Veo 3.1 Fast...")
        # Extract SW frame for animation (FFT convention)
        from assembly import split_grid_2x2
        _, _, d_sw, _ = split_grid_2x2(diagonal_sheet)
        sw_sprite = auto_crop(remove_chroma_key(d_sw))
        save_image(sw_sprite, out / "sw_frame.png")

        video_url = generate_video(WALK_ANIMATION, reference_image=sw_sprite)
        video_path = download_video(video_url, out / "walk_cycle.mp4")
        click.echo(f"      Saved: {video_path}")

    click.echo("\nDone! All outputs in: " + str(out.resolve()))


# ── Assemble-Only (from pre-generated sheets) ────────────────────────────────

@cli.command()
@click.option("--cardinals", required=True, type=click.Path(exists=True),
              help="Path to the 2×2 cardinal facings sheet.")
@click.option("--diagonals", required=True, type=click.Path(exists=True),
              help="Path to the 2×2 diagonal facings sheet.")
@click.option("--anchor", default=None, type=click.Path(exists=True),
              help="Optional: path to approved SE anchor (overrides diagonal SE).")
@click.option("--output-dir", default="./output", type=click.Path(),
              help="Directory for output files.")
@click.option("--target-height", default=None, type=int,
              help="Normalize all sprites to this height (pixels).")
@click.option("--mirror-west/--no-mirror-west", default=True,
              help="Mirror East to fix West (recommended).")
def assemble(cardinals, diagonals, anchor, output_dir, target_height, mirror_west):
    """Assemble a turnaround sheet from pre-generated cardinal and diagonal sheets."""
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    cardinal_sheet = load_image(cardinals)
    diagonal_sheet = load_image(diagonals)
    anchor_se = load_image(anchor) if anchor else None

    click.echo("Assembling 8-way turnaround sheet...")
    final_sheet = assemble_pipeline(
        cardinal_sheet=cardinal_sheet,
        diagonal_sheet=diagonal_sheet,
        anchor_se=anchor_se,
        mirror_west=mirror_west,
        target_height=target_height,
    )
    save_image(final_sheet, out / "turnaround_8way.png")
    click.echo(f"Saved: {out / 'turnaround_8way.png'}")


# ── Animate-Only ──────────────────────────────────────────────────────────────

@cli.command()
@click.option("--sprite", required=True, type=click.Path(exists=True),
              help="Path to the sprite frame to animate (typically SW facing).")
@click.option("--output-dir", default="./output", type=click.Path(),
              help="Directory for output files.")
@click.option("--prompt", default=None, type=str,
              help="Custom animation prompt (default: walk cycle).")
def animate(sprite, output_dir, prompt):
    """Generate a walk-cycle animation from a single sprite frame using Veo 3.1."""
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    sprite_img = load_image(sprite)
    anim_prompt = prompt or WALK_ANIMATION

    click.echo("Generating walk animation with Veo 3.1 Fast...")
    video_url = generate_video(anim_prompt, reference_image=sprite_img)
    video_path = download_video(video_url, out / "walk_cycle.mp4")
    click.echo(f"Saved: {video_path}")


if __name__ == "__main__":
    cli()
