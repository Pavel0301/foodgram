from rest_framework import serializers

from common.serializers import ImageMixin
from recipes.models.recipes import Ingredient, IngredientInRecipe, Recipe, Tag


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор модели ингредиентов."""

    class Meta:
        model = Ingredient
        fields = (
            'id',
            'name',
            'measurement_unit'
        )


class RecipeShortSerializer(serializers.Serializer, ImageMixin):

    cooking_time = serializers.IntegerField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'cooking_time',
            'image',
        )
        read_only_fields = (
            'image',
            'name',
            'cooking_time'
        )


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для тегов."""

    class Meta:
        model = Tag
        fields = (
            'id',
            'slug',
            'name',
        )


class IngredientsInRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для ингредиентов в рецепте."""
    id = serializers.ReadOnlyField(source='ingredients.id')
    name = serializers.ReadOnlyField(source='ingredients.name')
    amount = serializers.IntegerField()
    measurement_unit = serializers.ReadOnlyField(
        source='ingredients.measurement_unit'
    )

    class Meta:
        model = IngredientInRecipe
        fields = (
            'id',
            'name',
            'amount',
            'measurement_unit',
        )


class CreateIngredientsInRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для создания ингредиентов в рецепте"""
    id = serializers.IntegerField()
    amount = serializers.IntegerField()

    @staticmethod
    def validate_amount(value):
        if value < 1:
            raise serializers.ValidationError(
                'Количество ингредиента не может быть меньше 1.'
            )
        return value

    class Meta:
        model = IngredientInRecipe
        fields = (
            'id',
            'amount',
        )


class OptionalRecipeSerializer(serializers.ModelSerializer):
    """Дополнительный сериализатор для рецептов """

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time'
        )
