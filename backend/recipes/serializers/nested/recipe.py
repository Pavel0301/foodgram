from rest_framework import serializers

from common.serializers import Base64ImageField
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


class RecipeShortSerializer(serializers.Serializer):

    cooking_time = serializers.IntegerField()
    image = Base64ImageField()

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

    id = serializers.IntegerField()
    amount = serializers.IntegerField()
    name = serializers.SerializerMethodField()
    measurement_unit = serializers.SerializerMethodField()

    class Meta:
        model = IngredientInRecipe
        fields = (
            'id',
            'amount',
            'name',
            'measurement_unit'
        )

    def get_name(self, obj):
        ingredient = IngredientInRecipe.objects.filter(
            id=obj.id).values('ingredients__name')
        return ingredient[0]['ingredients__name']

    def get_measurement_unit(self, obj):
        ingredient = IngredientInRecipe.objects.filter(
            id=obj.id).values('ingredients__measurement_unit')
        return ingredient[0]['ingredients__measurement_unit']


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


class UserRecipeSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('user', 'recipe')

    def to_representation(self, instance):
        return RecipeShortSerializer(
            instance.recipe,
            context={"request": self.context.get("request")},
        ).data
