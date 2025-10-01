from __future__ import annotations

from io import BytesIO
from pathlib import Path
from typing import Tuple

from PIL import Image, ImageOps

from django.core.files.base import ContentFile

DEFAULT_WEBP_MAX_SIZE: Tuple[int, int] = (1920, 1920)
DEFAULT_WEBP_QUALITY: int = 80


def _normalize_image_mode(image: Image.Image) -> Image.Image:
    """Ensure the image is in a mode supported by WebP."""
    if image.mode in {"RGB", "RGBA"}:
        return image.convert("RGB")
    if image.mode == "P":
        return image.convert("RGB")
    if image.mode == "CMYK":
        return image.convert("RGB")
    if image.mode == "LA":
        return image.convert("RGB")
    return image.convert("RGB") if image.mode != "RGB" else image


def convert_image_to_webp(
    uploaded_file,
    *,
    original_name: str,
    max_size: Tuple[int, int] = DEFAULT_WEBP_MAX_SIZE,
    quality: int = DEFAULT_WEBP_QUALITY,
) -> ContentFile:
    """Convert an uploaded image to an optimized WebP representation."""
    uploaded_file.seek(0)
    image = Image.open(uploaded_file)
    image = ImageOps.exif_transpose(image)
    image = _normalize_image_mode(image)
    image.thumbnail(max_size, Image.Resampling.LANCZOS)

    buffer = BytesIO()
    image.save(
        buffer,
        format="WEBP",
        quality=quality,
        method=6,
    )
    buffer.seek(0)

    name = f"{Path(original_name).stem}.webp"
    return ContentFile(buffer.getvalue(), name=name)
