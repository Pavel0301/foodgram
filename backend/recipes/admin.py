from django.contrib import admin

from common.admin import BaseAdmin
from recipes.models.recipes import (Favorite, Ingredient, IngredientInRecipe,
                                    Recipe, ShoppingCart, Tag)


class IngredientInRecipeInline(admin.TabularInline):
    model = IngredientInRecipe
    extra = 0
    min_num = 1


@admin.register(Ingredient)
class IngredientAdmin(BaseAdmin):
    list_display = ('name', 'measurement_unit')
    search_fields = ('name', )
    list_filter = ('name', )
    inlines = (IngredientInRecipeInline, )


@admin.register(Tag)
class TagAdmin(BaseAdmin):
    list_display = ('name', 'slug')
    search_fields = ('name',)
    list_filter = ('name',)


@admin.register(Recipe)
class RecipeAdmin(BaseAdmin):
    list_display = (
        'name',
        'author',
        'cooking_time',
        'created_at',
    )
    list_display_links = ('author',)
    search_fields = ('name', 'author__username')
    list_filter = ('author', 'name', 'tags')
    inlines = (IngredientInRecipeInline,)


@admin.register(ShoppingCart)
class ShoppingCartAdmin(BaseAdmin):
    list_display = ('user', 'recipe')
    list_display_links = ('user', 'recipe')
    list_filter = ('user', 'recipe')
    search_fields = ('user',)


@admin.register(Favorite)
class FavoriteAdmin(BaseAdmin):
    list_display = ('user', 'recipe')
    list_display_links = ('user', 'recipe')
    list_filter = ('user', 'recipe')
    search_fields = ('user',)
