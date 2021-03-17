from django.core.management.base import BaseCommand, CommandError
from qrhunt.models import Location, Profile, AssignedLocation, AssignedLootBox
from random import sample


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('amount', nargs='+', type=int)
        parser.add_argument('reason', nargs='+', type=str)

    def handle(self, *args, **options):
        n = options["amount"]
        profiles = Profile.objects.all()
        profiles = [Profile.objects.get(pk=3)]
        for profile in profiles:
            user = profile.user

            for i in range(0, n):
                AssignedLootBox.objects.create(
                    user=user,
                    reason=options["reason"]
                )
