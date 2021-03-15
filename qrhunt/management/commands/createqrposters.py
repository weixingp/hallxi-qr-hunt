from django.core.management.base import BaseCommand, CommandError
import sys
from PIL import Image, ImageFont, ImageDraw
import requests

from hallxiqr.settings import BASE_DIR
from qrhunt.models import Location


class Command(BaseCommand):
    def handle(self, *args, **options):
        # locations = Location.objects.all()
        google_qr_base = "https://chart.googleapis.com/chart"
        payload = {
            "cht": "qr",
            "chs": "500x500",
            "chld": "M|0",
            "chl": "https://127.0.0.1:8000/location/24d8f616-e736-4a11-b39f-0785904dd593"
        }
        font_dir = str(BASE_DIR) + '/qrhunt/qrcodes/Roboto-Regular.ttf'
        # font = ImageFont.truetype(str(BASE_DIR) + '/qrhunt/qrcodes/Roboto-Regular.ttf', size=12)
        font = ImageFont.truetype(font_dir, size=47)

        qr = Image.open(requests.get(google_qr_base, stream=True, params=payload).raw)
        qr = qr.resize((984, 984))
        im = Image.open(BASE_DIR / 'qrhunt/qrcodes/base.jpg')
        im.paste(qr, (1369, 811))

        draw = ImageDraw.Draw(im)
        draw.text((1600, 1822), "Block 55 Lounge", (255, 255, 255), font=font)
        im.save(BASE_DIR / 'qrhunt/qrcodes/generated/test.jpg')
