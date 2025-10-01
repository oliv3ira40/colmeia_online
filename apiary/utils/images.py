from __future__ import annotations

from io import BytesIO
from pathlib import Path
from typing import Tuple

from PIL import Image, ImageOps

from django.core.files.base import ContentFile

DEFAULT_WEBP_MAX_SIZE: Tuple[int, int] = (1920, 1920)
DEFAULT_WEBP_QUALITY: int = 80


def _normalize_image_mode(image: Image.Image) -> Image.Image:
    """Normalize image modes while preserving transparency when available."""

    has_transparency = "A" in image.getbands() or image.info.get("transparency") is not None

    if has_transparency:
        return image if image.mode == "RGBA" else image.convert("RGBA")

    if image.mode == "RGB":
        return image

    return image.convert("RGB")


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
