from django_filters import FilterSet, filters

from recipes.models.recipes import Ingredient, Recipe, Tag


class RecipeFilter(FilterSet):
    """Фильтр по избранному и корзине покупок."""

    tags = filters.ModelMultipleChoiceFilter(
        queryset=Tag.objects.all(),
        field_name='tag__slug',
        to_field_name='slug',
    )
    is_favorited = filters.BooleanFilter(
        method='filter_is_favorited'
    )
    is_in_shopping_cart = filters.BooleanFilter(
        method='filter_is_in_shopping_cart'
    )

    class Meta:
        model = Recipe
        fields = (
            'tags',
            'author',
            'is_favorited',
            'is_in_shopping_cart',
        )

    def filter_is_favorited(self, queryset, value):
        user = self.request.user
        if value and self.request and user.is_authenticated:
            return queryset.filter(favourites__user=user)
        return queryset

    def filter_is_in_shopping_cart(self, queryset, value):
        user = self.request.user
        if value and self.request and user.is_authenticated:
            return queryset.filter(shopping_cart__user=user)
        return queryset


class IngredientFilter(FilterSet):
    """Фильтр по ингредиентам."""

    name = filters.CharFilter('startswith')

    class Meta:
        model = Ingredient
        fields = (
            'name',
        )
