from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone
from django.template.defaultfilters import truncatechars
from django.dispatch import receiver
from django.db.models.signals import post_save
from phonenumber_field.modelfields import PhoneNumberField


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
    block = models.CharField(
        max_length=2,
        choices=BLK_CHOICES,
    )

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
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="fk_user")
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name="fk_item")
    has_used = models.BooleanField(default=False)

    def __str__(self):
        return self.user.email + "'s " + self.item.name
