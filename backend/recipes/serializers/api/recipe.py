from common.serializers import ImageMixin, ImageUrlMixin
from recipes.models.recipes import (Ingredient, IngredientInRecipe, Recipe,
                                    ShoppingCart, Tag)
from recipes.serializers.nested.recipe import (CreateIngredientsInSerializer,
                                               IngredientsInRecipeSerializer,
                                               TagSerializer)
from rest_framework import serializers, validators
from users.models.follows import Follow
from users.serializers.api.users import UserSerializer


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор модели ингредиентов."""

    class Meta:
        model = Ingredient
        fields = (
            'id',
            'name',
            'measurement_unit'
        )


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для рецептов."""

    tags = TagSerializer(many=True)
    ingredients = IngredientsInRecipeSerializer(
        many=True,
        sorce='ingredient_list',
    )
    author = UserSerializer()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        )

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return ShoppingCart.objects.filter(
            recipe=obj,
            user=request.user
        ).exists()

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return Follow.objects.filter(
            following=obj.author,
            user=request.user
        ).exists()


class CreateRecipeSerializer(serializers.ModelSerializer, ImageUrlMixin):
    """Сериализатор для создания рецептов"""

    ingredients = CreateIngredientsInSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True,
    )

    class Meta:
        model = Recipe
        fields = (
            'ingredients',
            'tags',
            'name',
            'image',
            'text',
            'cooking_time',
        )

    def validate(self, data):
        """Проверка каждого ингредиента."""

        ingredients_list = []
        ingredients = data.get('ingredients')
        if ingredients:
            for ingredient in ingredients:
                if not ingredient.get('name') or not ingredient.get('measurement_unit'):
                    raise serializers.ValidationError('У ингредиентов должно быть название и мера')
                if ingredient.name in ingredients:
                    raise serializers.ValidationError('Ингредиенты не должны повторяться')
                ingredients_list.append(ingredient.name)
        return data

    def _create_ingredients(self, ingredients, recipe):
        """Метод выполнет создание ингредиента в рецепте."""

        for _ingredient in ingredients:
            id = _ingredient.get('id')
            ingredient = Ingredient.objects.get(id=id)
            amount = _ingredient.get('amount')
            IngredientInRecipe.objects.create(
                ingredient=ingredient,
                recipe=recipe,
                amount=amount
            )

    def _create_tags(self, tags, recipe):
        """Метод добавляет теги."""

        recipe.tags.set(tags)

    def create(self, validated_data):
        """Метод создания нового рецепта."""

        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        user = self.context.get('request').user
        recipe = Recipe.objects.create(**validated_data, author=user)
        self._create_tags(tags, recipe)
        self._create_ingredients(ingredients, recipe)
        return recipe


    def to_representation(self, instance):
        """Метод сериализации рецепта."""
        return RecipeSerializer(instance, context=self.context).data


class AddFavoriteSerializer(serializers.ModelSerializer, ImageMixin):
    """Сериализатор для добавления рецепта в избранное."""

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time',
        )
