from common.admin import BaseAdmin
from django.contrib import admin
from users.models.users import User

from .models.follows import Follow


@admin.register(User)
class UserAdmin(BaseAdmin):
    list_display = (
        'username',
        'first_name',
        'last_name',
        'email',
    )
    search_fields = (
        'username',
        'email',
    )
    list_filter = (
        'username',
        'email',
    )


@admin.register(Follow)
class FollowAdmin(BaseAdmin):
    list_display = (
        'user',
        'following',
    )
    list_filter = (
        'user',
        'following',
    )
    search_fields = (
        'user__username',
        'following__username',
    )
    list_display_links = (
        'user',
        'following',
    )
