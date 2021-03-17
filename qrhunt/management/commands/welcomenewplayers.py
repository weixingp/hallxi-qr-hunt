from django.core.management.base import BaseCommand, CommandError
from qrhunt.models import Location, Profile, AssignedLocation, AssignedLootBox
from random import sample


class Command(BaseCommand):
    def handle(self, *args, **options):
        profiles = Profile.objects.all()
        n = 5
        for profile in profiles:
            user = profile.user

            has_location = AssignedLocation.objects.filter(
                user=user
            )
            has_lootbox = AssignedLootBox.objects.filter(
                user=user
            )

            if not has_lootbox:
                print(f"Assigning loot box for new player: {profile.fullname}")
                for i in range(0, 2):
                    AssignedLootBox.objects.create(
                        user=user,
                        reason="welcome_gift_late"
                    )

            if has_location:
                continue
            else:
                print(f"Assigning location for new player: {profile.fullname}")

                pks = Location.objects.filter(
                    area__in=[profile.block.name, "00"],
                ).values_list('pk', flat=True)

                if len(pks) < n:
                    raise ValueError("Not enough locations")

                locations = sample(list(pks), k=n)
                for location_id in locations:
                    location = Location.objects.get(pk=location_id)
                    AssignedLocation.objects.create(
                        user=user,
                        location=location
                    )
