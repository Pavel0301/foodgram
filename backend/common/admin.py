from django.contrib import admin


class BaseAdmin(admin.ModelAdmin):
    """Базовый класс администрирования моделей"""

    list_per_page = 25
    empty_value_display = '-'