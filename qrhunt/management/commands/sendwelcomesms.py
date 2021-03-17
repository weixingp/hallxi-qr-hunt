from django.core.management.base import BaseCommand, CommandError

from qrhunt.apis.Twilio import Twilio
from qrhunt.models import Profile, AssignedLootBox


class Command(BaseCommand):

    def handle(self, *args, **options):
        profiles = Profile.objects.all()
        count = 1
        total = len(profiles)
        body = "Hi Hall XI, phase 2 of IBG has begun. Launch the app https://play.hallxi.com to play now. $500 " \
               "Shopee voucher, 24inch monitor and JBL speakers to be won."

        for profile in profiles:
            print(f"Processing SMS: {count} / {total}")

            if not profile.mobile:
                continue

            hp = profile.mobile.as_e164

            tw = Twilio()
            tw.send(hp, body)
            count += 1