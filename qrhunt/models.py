from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone
from django.contrib import admin
from django.utils.html import format_html
from django.core.validators import MaxValueValidator, MinValueValidator
from phonenumber_field.modelfields import PhoneNumberField
import uuid
from urllib.parse import urlencode
from hallxiqr.settings import SITE_URL


class Block(models.Model):
    name = models.CharField(max_length=2, unique=True)
    max_hp = models.IntegerField(validators=[MinValueValidator(0)],)
    max_exploration_points = models.IntegerField(validators=[MinValueValidator(0)],)

    def __str__(self):
        return self.name


class Question(models.Model):
    question = models.TextField(max_length=1000)

    DIFFICULTY_CHOICES = (
        ("1", "Easy"),
        ("2", "Normal"),
        ("3", "Hard"),
    )
    difficulty = models.CharField(
        max_length=1,
        choices=DIFFICULTY_CHOICES,
    )

    TYPE_CHOICES = (
        ("1", "Covid 19"),
        ("2", "Hall XI")
    )
    type = models.CharField(
        max_length=1,
        choices=TYPE_CHOICES,
    )

    # Object name for display in admin panel
    def __str__(self):
        return self.question


class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="question_fk")
    answer = models.CharField(max_length=256)
    is_correct = models.BooleanField(default=False)

    # Object name for display in admin panel
    def __str__(self):
        if self.is_correct:
            return "Correct"
        else:
            return "Incorrect"


class UserManager(BaseUserManager):

    def _create_user(self, email, password, is_staff, is_superuser, **extra_fields):
        if not email:
            raise ValueError('Users must have an email address')
        now = timezone.now()
        email = self.normalize_email(email)
        user = self.model(
            email=email,
            is_staff=is_staff,
            is_active=True,
            is_superuser=is_superuser,
            last_login=now,
            date_joined=now,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password, **extra_fields):
        return self._create_user(email, password, False, False, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        user = self._create_user(email, password, True, True, **extra_fields)
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(max_length=254, unique=True)
    name = models.CharField(max_length=254, null=True, blank=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    last_login = models.DateTimeField(null=True, blank=True)
    date_joined = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = 'email'
    EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def get_absolute_url(self):
        return "/users/%i/" % self.pk


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    fullname = models.CharField(max_length=128)

    BLK_CHOICES = (
        ("53", "53"),
        ("54", "54"),
        ("55", "55"),
        ("56", "56"),
    )
    # block = models.CharField(
    #     max_length=2,
    #     choices=BLK_CHOICES,
    # )

    block = models.ForeignKey(Block, on_delete=models.CASCADE, related_name="fk_profile_block", blank=False,)

    LVL_CHOICES = (
        ("01", "01"),
        ("02", "02"),
        ("03", "03"),
        ("04", "04"),
        ("05", "05"),
        ("06", "06"),
    )
    level = models.CharField(
        max_length=2,
        choices=LVL_CHOICES,
    )

    room_number = models.CharField(max_length=10)
    mobile = PhoneNumberField(null=True, blank=True, unique=True)
    has_checked = models.BooleanField(default=False)

    def __str__(self):
        return self.user.email


class Item(models.Model):
    name = models.CharField(max_length=30)
    RARITY_CHOICE = (
        ("1", "Common"),
        ("2", "Rare"),
        ("3", "Super Rare"),
        ("4", "Legendary")
    )

    rarity = models.CharField(
        max_length=1,
        choices=RARITY_CHOICE,
    )

    TYPE_CHOICE = (
        ("1", "Attack"),
        ("2", "Heal"),
        ("3", "Hall XI Merchandise"),
    )

    type = models.CharField(
        max_length=1,
        choices=TYPE_CHOICE
    )

    value = models.IntegerField(blank=True, null=True)

    description = models.TextField(blank=True)

    # Hardcoded points gained for each of the rarity
    def get_points(self):
        if self.rarity == '1':
            points = 10
        elif self.rarity == '2':
            points = 30
        elif self.rarity == '3':
            points = 50
        elif self.rarity == '4':
            points = 60
        else:
            points = 0

        return points

    def get_item_description(self):
        if self.type == "1":
            desc = "A " + self.get_rarity_display() + " attack item that does " + str(self.value) + " damage to the " \
                                                                                                    "selected block. Gain " + str(
                self.get_points()) + " points."
        elif self.type == "2":
            desc = "A " + self.get_rarity_display() + " healing item that heals " + str(self.value) + " HP for your " \
                                                                                                      "block. Gain " + str(
                self.get_points()) + " points."
        elif self.type == "3":
            desc = "A physical Hall XI merchandise. You can't use now, we will contact you for collection at a later " \
                   "date. Gain " + str(self.get_points()) + " points."

        else:
            desc = "No description available."

        return desc

    # Object name for display in admin panel
    def __str__(self):
        return self.name


class Inventory(models.Model):
    class Meta:
        verbose_name_plural = "Inventories"

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="fk_inventory_user")
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name="fk_inventory_item")
    has_used = models.BooleanField(default=False)
    time = models.DateTimeField(auto_now=True, blank=True)

    def __str__(self):
        return self.user.email + "'s " + self.item.name


class AssignedQuestion(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="fk_assigned_question_user")
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name="fk_assigned_question_question",
        null=True,
    )
    time = models.DateTimeField(null=True)
    has_answered = models.BooleanField(default=False)
    answered_time = models.DateTimeField(blank=True, null=True)

    class Meta:
        unique_together = ('user', 'question',)

    def __str__(self):
        return self.user.email + "'s question"


class Location(models.Model):
    name = models.CharField(max_length=38)
    AREA_CHOICES = (
        ("53", "53"),
        ("54", "54"),
        ("55", "55"),
        ("56", "56"),
        ("00", "Common Area")
    )
    area = models.CharField(
        max_length=2,
        choices=AREA_CHOICES,
    )

    LVL_CHOICES = (
        ("01", "01"),
        ("02", "02"),
        ("03", "03"),
        ("04", "04"),
        ("05", "05"),
        ("06", "06"),
        ("00", "Not applicable")
    )
    level = models.CharField(
        max_length=2,
        choices=LVL_CHOICES,
    )

    image = models.ImageField(upload_to="locations/", null=True, blank=True)

    uuid = models.UUIDField(default=uuid.uuid4, editable=False)

    def qr_code(self):
        q = {
            "cht": "qr",
            "chl": SITE_URL + "location/" + str(self.uuid),
            "chs": "500x500",
        }
        qr_link = "https://chart.googleapis.com/chart?" + urlencode(q)
        return format_html(
            '<a href="{}" target="_blank">QR Code</a>',
            # SITE_URL + "qr/" + self.uuid,
            qr_link,
        )

    def uuid_str(self):
        return self.uuid.hex

    def __str__(self):
        return self.name


class AssignedLocation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="fk_assigned_location_user")
    location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name="fk_assigned_location_location")
    time = models.DateTimeField(auto_now=True, blank=True)
    has_visited = models.BooleanField(default=False)
    visit_time = models.DateTimeField(blank=True, null=True)

    class Meta:
        unique_together = ('user', 'location',)

    def __str__(self):
        return self.user.email + "'s " + self.location.name


class HpLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="fk_hp_log_user")
    target_block = models.ForeignKey(Block, on_delete=models.CASCADE, related_name="fk_hp_log_block")
    value = models.IntegerField()
    reason = models.CharField(null=True, blank=True, max_length=255)
    time = models.DateTimeField(auto_now=True, blank=True)

    def __str__(self):
        return self.target_block.name + "'s HP Log"
