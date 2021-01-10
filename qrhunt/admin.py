from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User, Profile


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = True
    verbose_name_plural = 'Profile'
    fk_name = 'user'


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
            # 'groups',
            # 'user_permissions',
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
