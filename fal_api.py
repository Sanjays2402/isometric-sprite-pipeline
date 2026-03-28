"""
fal.ai API client for image generation (Nano Banana 2) and video generation (Veo 3.1).
"""

import base64
import io
import os
from pathlib import Path

import fal_client
import requests
from PIL import Image


def _get_fal_key() -> str:
    key = os.environ.get("FAL_KEY")
    if not key:
        raise RuntimeError(
            "FAL_KEY environment variable is not set. "
            "Get your key at https://fal.ai/dashboard/keys"
        )
    return key


def image_to_data_uri(img: Image.Image, fmt: str = "PNG") -> str:
    buf = io.BytesIO()
    img.save(buf, format=fmt)
    b64 = base64.b64encode(buf.getvalue()).decode()
    mime = "image/png" if fmt == "PNG" else "image/jpeg"
    return f"data:{mime};base64,{b64}"


def load_image(path: str | Path) -> Image.Image:
    return Image.open(path).convert("RGBA")


def save_image(img: Image.Image, path: str | Path) -> Path:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    img.save(p)
    return p


def download_image(url: str) -> Image.Image:
    resp = requests.get(url, timeout=120)
    resp.raise_for_status()
    return Image.open(io.BytesIO(resp.content)).convert("RGBA")


def generate_image(
    prompt: str,
    reference_image: Image.Image | None = None,
    model: str = "fal-ai/nano-banana-2",
    image_size: str = "square",
    num_images: int = 1,
) -> list[Image.Image]:
    """Generate images using fal.ai (Nano Banana 2 by default)."""
    _get_fal_key()

    arguments: dict = {
        "prompt": prompt,
        "image_size": image_size,
        "num_images": num_images,
    }

    if reference_image is not None:
        arguments["image_url"] = image_to_data_uri(reference_image)

    result = fal_client.subscribe(model, arguments=arguments)

    images: list[Image.Image] = []
    for img_data in result.get("images", []):
        url = img_data.get("url")
        if url:
            images.append(download_image(url))
    return images


def generate_video(
    prompt: str,
    reference_image: Image.Image,
    model: str = "fal-ai/veo-3.1/fast",
    duration: int = 4,
) -> str:
    """Generate a walk-cycle video using Veo 3.1 Fast via fal.ai. Returns the video URL."""
    _get_fal_key()

    arguments = {
        "prompt": prompt,
        "image_url": image_to_data_uri(reference_image),
        "duration": duration,
    }

    result = fal_client.subscribe(model, arguments=arguments)
    video_url = result.get("video", {}).get("url", "")
    if not video_url:
        raise RuntimeError(f"No video URL in fal.ai response: {result}")
    return video_url


def download_video(url: str, output_path: str | Path) -> Path:
    p = Path(output_path)
    p.parent.mkdir(parents=True, exist_ok=True)
    resp = requests.get(url, timeout=300, stream=True)
    resp.raise_for_status()
    with open(p, "wb") as f:
        for chunk in resp.iter_content(chunk_size=8192):
            f.write(chunk)
    return p
