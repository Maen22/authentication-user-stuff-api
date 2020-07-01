from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User
from django.utils.translation import gettext as _


class CustomUserAdmin(BaseUserAdmin):
    ordering = ('id',)
    search_fields = ('first_name', 'last_name', 'email')
    model = User
    list_display = ['email', 'first_name', 'last_name', 'gender', 'organization']
    list_filter = ('is_admin',)

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'gender', 'image', 'organization')}),
        (_('Permissions'), {
            'fields': ('is_admin',),
        }),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2'),
        }),
    )


admin.site.register(User, CustomUserAdmin)

