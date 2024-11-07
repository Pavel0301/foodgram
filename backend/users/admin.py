from django.contrib import admin

from .models import Follow, User


class BaseAdmin(admin.ModelAdmin):
    """Базовый класс для настройки административной панели Django."""

    empty_value_display = '-'
    list_per_page = 20


@admin.register(User)
class UserAdmin(BaseAdmin):
    list_display = (
        'username',
        'first_name',
        'last_name',
        'email',
    )
    search_fields = ('username', 'email',)
    list_filter = ('username', 'email',)
    ordering = ('username', )


@admin.register(Follow)
class FollowAdmin(BaseAdmin):
    list_display = (
        'user',
        'following',
    )
    list_display_links = ('user', 'following')
    search_fields = ('user__username', 'following__username',)
    list_filter = ('user', 'following',)
    ordering = ('user', )
