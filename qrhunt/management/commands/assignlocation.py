from random import randint

from django.core.management.base import BaseCommand, CommandError
import sys
from PIL import Image, ImageFont, ImageDraw
import requests
from django.utils.timezone import localtime

from hallxiqr.settings import BASE_DIR
from qrhunt.main import get_assigned_location
from qrhunt.models import Location, AssignedQuestion, User, Profile, AssignedLocation
from random import sample


class Command(BaseCommand):
    def handle(self, *args, **options):
        profiles = Profile.objects.all()
        profiles = [Profile.objects.get(pk=3)]
        n = 5
        for profile in profiles:
            user = profile.user

            visited_location = AssignedLocation.objects.filter(
                user=user,
                has_visited=False
            ).values_list('location_id', flat=True)

            pks = Location.objects.filter(
                area__in=[profile.block.name, "00"],
            ).exclude(
                id__in=list(visited_location)
            ).values_list('pk', flat=True)

            if pks < n:
                raise ValueError("Not enough locations")

            locations = sample(list(pks), k=n)
            for location_id in locations:
                location = Location.objects.get(pk=location_id)
                AssignedLocation.objects.create(
                    user=user,
                    location=location
                )
