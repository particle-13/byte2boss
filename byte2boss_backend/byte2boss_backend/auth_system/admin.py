from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ('email', 'name', 'is_verified', 'is_staff', 'is_superuser')
    list_filter = ('is_verified', 'is_staff', 'is_superuser')
    search_fields = ('email', 'name')
    ordering = ('email',)
    readonly_fields = ('last_login', 'date_joined')

    fieldsets = (
        (None, {'fields': ('email', 'name', 'password')}),
        ('Permissions', {'fields': ('is_verified', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'name', 'password1', 'password2', 'is_verified', 'is_staff', 'is_superuser')}
        ),
    )

    def has_delete_permission(self, request, obj=None):
        # Always allow superusers to delete
        if request.user.is_superuser:
            return True
        return super().has_delete_permission(request, obj)
