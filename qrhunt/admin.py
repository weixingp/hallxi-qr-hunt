from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.urls import reverse
from django.utils.html import format_html
from .models import User, Profile, Question, Answer, Item, Inventory, AssignedQuestion, AssignedItem
from .models import Location, AssignedLocation, Block, HpLog, AssignedLootBox


def linkify(field_name):
    """
    Converts a foreign key value into clickable links.

    If field_name is 'parent', link text will be str(obj.parent)
    Link will be admin url for the admin url for obj.parent.id:change
    """

    def _linkify(obj):
        linked_obj = getattr(obj, field_name)
        if linked_obj is None:
            return '-'
        app_label = linked_obj._meta.app_label
        model_name = linked_obj._meta.model_name
        view_name = f'admin:{app_label}_{model_name}_change'
        link_url = reverse(view_name, args=[linked_obj.pk])
        return format_html('<a href="{}">{}</a>', link_url, linked_obj)

    _linkify.short_description = field_name  # Sets column name
    return _linkify


@admin.register(AssignedLootBox)
class AssignedLootBoxAdmin(admin.ModelAdmin):
    list_display = ('user', linkify(field_name="assigned_item"), 'reason', 'has_opened', 'time_opened', 'time')
    list_filter = ('has_opened',)
    search_fields = ('reason', 'user__email')


@admin.register(AssignedItem)
class AssignedItemAdmin(admin.ModelAdmin):
    list_display = ('user', linkify(field_name="item"), 'has_used', 'time_used', 'time')
    list_filter = ('has_used',)
    search_fields = ('user__email',)


@admin.register(HpLog)
class HpLogAdmin(admin.ModelAdmin):
    list_display = ('user', linkify(field_name="target_block"), 'value', 'reason', 'time')
    list_filter = ('target_block__name',)
    search_fields = ('reason',)


@admin.register(Block)
class BlockAdmin(admin.ModelAdmin):
    list_display = ('name', 'max_hp', 'max_exploration_points',)


@admin.register(AssignedLocation)
class AssignedLocationAdmin(admin.ModelAdmin):
    list_display = ('user', linkify(field_name="location"), 'time', 'has_visited', 'visit_time')
    list_filter = ('has_visited',)
    search_fields = ('user__email', 'location__name', 'location__uuid')


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ('name', 'area', 'level', 'uuid_str', 'qr_code')
    list_filter = ('area', 'level',)
    search_fields = ('name', 'uuid')


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):

    # Reverse lookup full name from profile
    def get_description(self, obj):
        return obj.get_item_description()

    get_description.short_description = 'Description'
    # get_description.admin_order_field = 'profile__fullname'

    list_display = ('name', 'type', 'rarity', 'get_description')
    list_filter = ('type', 'rarity',)
    search_fields = ('name',)


@admin.register(Inventory)
class InventoryAdmin(admin.ModelAdmin):
    # inlines = (AnswerInline,)

    list_display = ('user', linkify(field_name="item"), 'has_used', 'time')
    list_filter = ('has_used',)
    search_fields = ('user__email', 'item__name')


class AnswerInline(admin.StackedInline):
    model = Answer
    can_delete = True
    verbose_name_plural = 'Answers'
    fk_name = 'question'

    def get_extra(self, request, obj=None, **kwargs):
        if not hasattr(obj, 'question_fk') or not obj.question_fk.exists():
            return 4
        else:
            return 0


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    inlines = (AnswerInline,)
    list_display = ('question', 'difficulty', 'type',)
    list_filter = ('difficulty', 'type',)
    search_fields = ('question',)


@admin.register(AssignedQuestion)
class AssignedQuestionAdmin(admin.ModelAdmin):
    list_display = ('user', linkify(field_name="question"), 'time', 'has_answered', 'answered_time')
    list_filter = ('has_answered',)
    search_fields = ('user__email', 'question__question')


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = True
    verbose_name_plural = 'Profile'
    fk_name = 'user'


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'fullname', linkify(field_name="block"), 'level', 'mobile', 'has_checked')
    list_filter = ('block__name', 'level', 'has_checked')
    search_fields = ('user__email',)


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    inlines = (ProfileInline,)

    fieldsets = (
        (None,
         {'fields': (
             'email',
             'password',
             # 'name',
             'last_login'
         )}),
        ('Permissions', {'fields': (
            'is_active',
            'is_staff',
            'is_superuser',
            'groups',
            'user_permissions',
        )}),
    )
    add_fieldsets = (
        (
            None,
            {
                'classes': ('wide',),
                'fields': ('email', 'password1', 'password2')
            }
        ),
    )

    # Reverse lookup full name from profile
    def get_fullname(self, obj):
        return obj.profile.fullname

    get_fullname.short_description = 'Full Name'
    get_fullname.admin_order_field = 'profile__fullname'

    # Reverse lookup block from profile
    def get_block(self, obj):
        return obj.profile.block

    get_block.short_description = 'Block'
    get_block.admin_order_field = 'profile__block'

    list_display = ('email', 'get_fullname', 'get_block', 'last_login')
    list_select_related = ('profile',)

    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups')
    search_fields = ('email',)
    ordering = ('email',)
    filter_horizontal = ('groups', 'user_permissions',)




