from django.core.management.base import BaseCommand, CommandError
from qrhunt.models import Profile, AssignedLootBox


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('-n', "--amount", type=int)
        parser.add_argument('-r', "--reason", type=str)

    def handle(self, *args, **options):
        if not options["amount"] or not options["reason"]:
            raise ValueError("Invalid args.")

        n = options["amount"]
        profiles = Profile.objects.all()
        for profile in profiles:
            user = profile.user

            for i in range(0, n):
                AssignedLootBox.objects.create(
                    user=user,
                    reason=options["reason"]
                )
