import base64

from django.core.files.base import ContentFile
from rest_framework import serializers, validators
from users.models import Follow, User
from users.serializers import UserSerializer

from .models import (Favorite, Ingredients, IngredientsRecipe, Recipe,
                     ShoppingCart, Tags)
from .validators import recipe_validator


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]

            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class IngredientsSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Ingredients."""

    class Meta:
        model = Ingredients
        fields = ('id', 'name', 'measurement_unit')


class TagsSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Tags."""

    class Meta:
        model = Tags
        fields = ('id', 'slug', 'name')


class RecipeIngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для связи ингредиента с рецептом."""
    id = serializers.IntegerField()
    amount = serializers.IntegerField()
    name = serializers.SerializerMethodField()
    measurement_unit = serializers.SerializerMethodField()

    class Meta:
        model = IngredientsRecipe
        fields = (
            'id',
            'amount',
            'name',
            'measurement_unit'
        )

    def get_name(self, obj):
        ingredient = IngredientsRecipe.objects.filter(
            id=obj.id).values('ingredients__name')
        return ingredient[0]['ingredients__name']

    def get_measurement_unit(self, obj):
        ingredient = IngredientsRecipe.objects.filter(
            id=obj.id).values('ingredients__measurement_unit')
        return ingredient[0]['ingredients__measurement_unit']


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Recipe."""

    ingredients = RecipeIngredientSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tags.objects.all(),
        many=True,
    )
    image = Base64ImageField(required=False, allow_null=True)
    author = UserSerializer(read_only=True)

    class Meta:
        model = Recipe
        fields = ('id',
                  'author',
                  'name',
                  'tags',
                  'ingredients',
                  'text',
                  'cooking_time',
                  'image')
        read_only_fields = ('author',)
        validators = [recipe_validator]

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        author = self.context.get('request').user
        recipe = Recipe.objects.create(author=author, **validated_data)
        recipe.tags.set(tags)
        ingredients_data = [
            IngredientsRecipe(
                ingredients_id=ingredient['id'],
                recipe=recipe,
                amount=ingredient['amount']
            ) for ingredient in ingredients
        ]
        IngredientsRecipe.objects.bulk_create(ingredients_data)
        return recipe

    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        instance.tags.clear()
        instance.tags.set(tags)
        IngredientsRecipe.objects.filter(recipe=instance).delete()
        ingredients_data = [
            IngredientsRecipe(
                ingredients_id=ingredient['id'],
                recipe=instance,
                amount=ingredient['amount']
            ) for ingredient in ingredients
        ]
        IngredientsRecipe.objects.bulk_create(ingredients_data)
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        return RecipeReadSerializer(instance, context=self.context).data


class RecipeReadSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Recipe."""
    author = UserSerializer(read_only=True)
    tags = TagsSerializer(many=True)
    ingredients = RecipeIngredientSerializer(many=True,
                                             source='ingredientsrecipe_set')
    cooking_time = serializers.IntegerField()
    image = Base64ImageField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()

    class Meta:
        fields = ('id',
                  'name',
                  'author',
                  'tags',
                  'ingredients',
                  'cooking_time',
                  'text',
                  'image',
                  'is_favorited',
                  'is_in_shopping_cart')
        model = Recipe

    def get_is_favorited(self, obj):
        request = self.context.get("request")

        return bool(
            request and request.user.is_authenticated
            and Favorite.objects.filter(
                recipe=obj,
                user=self.context.get('request').user
            ).exists()
        )

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get("request")

        return bool(
            request and request.user.is_authenticated
            and ShoppingCart.objects.filter(
                recipe=obj,
                user=self.context.get('request').user
            ).exists()
        )


class RecipeShortSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Recipe."""
    image = Base64ImageField()
    cooking_time = serializers.IntegerField()

    class Meta:
        fields = ('id',
                  'name',
                  'cooking_time',
                  'image')
        model = Recipe
        read_only_fields = (
            'image',
            'name',
            'cooking_time',
        )


class FollowInfoSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField(read_only=True)
    recipes_count = serializers.SerializerMethodField(read_only=True)
    recipes = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'avatar',
            'is_subscribed',
            'recipes',
            'recipes_count'
        )
        read_only_fields = (
            'email',
            'username',
            'first_name',
            'last_name',
        )

    def get_recipes(self, obj):
        request = self.context.get('request')
        recipes_limit = request.query_params.get('recipes_limit')
        recipes_queryset = Recipe.objects.filter(author=obj)
        if recipes_limit is not None:
            recipes_queryset = recipes_queryset[:int(recipes_limit)]
        serializer = RecipeShortSerializer(recipes_queryset, many=True)
        return serializer.data

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj).count()

    def get_is_subscribed(self, obj):
        request = self.context.get("request")

        return bool(
            request and request.user.is_authenticated
            and Follow.objects.filter(
                following=obj,
                user=self.context.get('request').user
            ).exists()
        )


class FollowSerializer(serializers.ModelSerializer):

    class Meta:
        model = Follow
        fields = ('id', 'user', 'following')
        validators = [
            validators.UniqueTogetherValidator(
                queryset=Follow.objects.all(),
                fields=('user', 'following')
            )
        ]

    def validate(self, data):
        request = self.context.get("request")
        if request.user == data["following"]:
            raise serializers.ValidationError(
                'Пользователь не может подписаться на самого себя.'
            )
        return data

    def to_representation(self, instance):
        return FollowInfoSerializer(
            instance.following,
            context={"request": self.context.get("request")},
        ).data


class UserRecipeSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('user', 'recipe')

    def to_representation(self, instance):
        return RecipeShortSerializer(
            instance.recipe,
            context={"request": self.context.get("request")},
        ).data


class FavoriteSerializer(UserRecipeSerializer):

    class Meta(UserRecipeSerializer.Meta):
        model = Favorite
        validators = [
            validators.UniqueTogetherValidator(
                queryset=Favorite.objects.all(),
                fields=('user', 'recipe'),
                message='Рецепт в избранном',
            ),
        ]


class ShoppingSerializer(UserRecipeSerializer):

    class Meta(UserRecipeSerializer.Meta):
        model = ShoppingCart
        validators = [
            validators.UniqueTogetherValidator(
                queryset=ShoppingCart.objects.all(),
                fields=('user', 'recipe'),
                message='Рецепт в списке покупок',
            ),
        ]
