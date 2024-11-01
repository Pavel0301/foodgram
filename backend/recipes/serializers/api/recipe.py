from rest_framework import serializers

from common.serializers import ImageMixin, ImageUrlMixin
from recipes.models.recipes import (IngredientInRecipe, Recipe, ShoppingCart,
                                    Tag)
from recipes.serializers.nested.recipe import (
    CreateIngredientsInRecipeSerializer, IngredientsInRecipeSerializer,
    TagSerializer)
from recipes.validators import recipe_validator
from users.models.follows import Follow
from users.serializers.api.users import UserSerializer


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для рецептов."""

    tags = TagSerializer(many=True)
    ingredients = IngredientsInRecipeSerializer(
        many=True,
        source='ingredient_list',
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
        validators = [recipe_validator]

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

    ingredients = CreateIngredientsInRecipeSerializer(many=True)
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
                if not ingredient.get('name') or not ingredient.get(
                        'measurement_unit'
                ):
                    raise serializers.ValidationError(
                        'У ингредиентов должно быть название и мера'
                    )
                if ingredient.name in ingredients:
                    raise serializers.ValidationError(
                        'Ингредиенты не должны повторяться'
                    )
                ingredients_list.append(ingredient.name)
        return data

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        author = self.context.get('request').user
        recipe = Recipe.objects.create(author=author, **validated_data)
        recipe.tags.set(tags)
        ingredients_data = [
            IngredientInRecipe(
                ingredients_id=ingredient['id'],
                recipe=recipe,
                amount=ingredient['amount']
            ) for ingredient in ingredients
        ]
        IngredientInRecipe.objects.bulk_create(ingredients_data)
        return recipe

    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        instance.tags.clear()
        instance.tags.set(tags)
        IngredientInRecipe.objects.filter(recipe=instance).delete()
        ingredients_data = [
            IngredientInRecipe(
                ingredients_id=ingredient['id'],
                recipe=instance,
                amount=ingredient['amount']
            ) for ingredient in ingredients
        ]
        IngredientInRecipe.objects.bulk_create(ingredients_data)
        return super().update(instance, validated_data)

    def to_representation(self, instance):
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
