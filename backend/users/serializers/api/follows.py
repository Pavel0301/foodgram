from rest_framework import serializers, validators

from recipes.models.recipes import Recipe
from recipes.serializers.nested.recipe import RecipeShortSerializer
from users.models.follows import Follow
from users.models.users import User


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
        fields = (
            'id',
            'user',
            'following'
        )
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
                'Вы не может подписаться на самого себя.'
            )
        return data

    def to_representation(self, instance):
        return FollowInfoSerializer(
            instance.following,
            context={"request": self.context.get("request")},
        ).data
