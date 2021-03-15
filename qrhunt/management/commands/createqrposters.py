from django.core.management.base import BaseCommand, CommandError
import sys
from PIL import Image, ImageFont, ImageDraw
import requests

from hallxiqr.settings import BASE_DIR
from qrhunt.models import Location


class Command(BaseCommand):
    def handle(self, *args, **options):
        google_qr_base = "https://chart.googleapis.com/chart"
        font_dir = str(BASE_DIR) + '/qrhunt/qrcodes/Roboto-Regular.ttf'
        font = ImageFont.truetype(font_dir, size=48)

        locations = Location.objects.all()
        count = 1
        for location in locations:
            print(f"Processing location: {count} / {len(locations)}")
            location_uuid = location.uuid_str()
            payload = {
                "cht": "qr",
                "chs": "500x500",
                "chld": "M|0",
                "chl": f"https://play.hallxi.com/location/{location_uuid}"
            }

            qr = Image.open(requests.get(google_qr_base, stream=True, params=payload).raw)
            qr = qr.resize((984, 984))
            im = Image.open(BASE_DIR / 'qrhunt/qrcodes/base.jpg')
            im.paste(qr, (1369, 811))

            draw = ImageDraw.Draw(im)
            draw.text((1600, 1820), "Computer Lab", (255, 255, 255), font=font)
            save_dir = str(BASE_DIR) + f"/qrhunt/qrcodes/generated/{location.uuid_str()}.jpg"
            im.save(save_dir)
            count += 1
