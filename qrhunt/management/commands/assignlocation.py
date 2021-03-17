from django.core.management.base import BaseCommand, CommandError
from qrhunt.models import Location, Profile, AssignedLocation
from random import sample


class Command(BaseCommand):
    def handle(self, *args, **options):
        profiles = Profile.objects.all()
        n = 5
        for profile in profiles:
            user = profile.user

            visited_location = AssignedLocation.objects.filter(
                user=user,
            ).values_list('location_id', flat=True)

            pks = Location.objects.filter(
                area__in=[profile.block.name, "00"],
            ).exclude(
                id__in=list(visited_location)
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
