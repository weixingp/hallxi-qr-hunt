from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User, Profile, Question, Answer, Item


class ItemAdmin(admin.ModelAdmin):
    # inlines = (AnswerInline,)

    # Reverse lookup full name from profile
    def get_description(self, obj):
        return obj.get_item_description()

    get_description.short_description = 'Description'
    # get_description.admin_order_field = 'profile__fullname'

    list_display = ('name', 'type', 'rarity', 'get_description')
    list_filter = ('type', 'rarity',)
    search_fields = ('name',)


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


class QuestionAdmin(admin.ModelAdmin):
    inlines = (AnswerInline,)
    list_display = ('question', 'difficulty', 'type',)
    list_filter = ('difficulty', 'type',)
    search_fields = ('question',)


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = True
    verbose_name_plural = 'Profile'
    fk_name = 'user'


class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'fullname', 'block', 'level', 'mobile')
    list_filter = ('block', 'level',)
    search_fields = ('user',)


class UserAdmin(BaseUserAdmin):
    inlines = (ProfileInline,)

    fieldsets = (
        (None,
         {'fields': (
             'email',
             # 'password',
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


admin.site.register(User, UserAdmin)
admin.site.register(Question, QuestionAdmin)
admin.site.register(Profile, ProfileAdmin)
admin.site.register(Item, ItemAdmin)
