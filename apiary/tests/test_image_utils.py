from __future__ import annotations

from io import BytesIO

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import SimpleTestCase
from PIL import Image

from apiary.utils.images import convert_image_to_webp


class ConvertImageToWebPTests(SimpleTestCase):
    def _build_uploaded_image(self, *, mode: str, color, format: str = "PNG"):
        buffer = BytesIO()
        Image.new(mode, (64, 64), color=color).save(buffer, format=format)
        buffer.seek(0)
        return SimpleUploadedFile("test_image.png", buffer.getvalue(), content_type="image/png")

    def test_convert_image_to_webp_preserves_transparency(self):
        uploaded = self._build_uploaded_image(mode="RGBA", color=(255, 0, 0, 128))

        converted = convert_image_to_webp(uploaded, original_name="test.png")

        self.assertTrue(converted.name.endswith(".webp"))

        converted.seek(0)
        with Image.open(converted) as image:
            self.assertIn("A", image.getbands())

    def test_convert_image_to_webp_returns_rgb_when_no_alpha(self):
        uploaded = self._build_uploaded_image(mode="RGB", color=(255, 255, 255))

        converted = convert_image_to_webp(uploaded, original_name="test.png")

        converted.seek(0)
        with Image.open(converted) as image:
            self.assertNotIn("A", image.getbands())
