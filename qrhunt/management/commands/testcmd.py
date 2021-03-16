
from django.core.management.base import BaseCommand, CommandError
import sys
from PIL import Image, ImageFont, ImageDraw
import requests
from django.utils.timezone import localtime

from hallxiqr.settings import BASE_DIR
from qrhunt.models import Location, AssignedQuestion, User


class Command(BaseCommand):
    def handle(self, *args, **options):
        user = User.objects.get(id=4)

        question_list = AssignedQuestion.objects.filter(
            user=user,
            has_answered=False,
            time__date=localtime().date(),
        )

        print(question_list)
