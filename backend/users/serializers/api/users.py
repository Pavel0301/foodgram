from rest_framework import serializers
from rest_framework.exceptions import ParseError

from common.serializers import Base64ImageField, ImageMixin
from users.models.follows import Follow
from users.models.users import User


class RegistrationSerializer(serializers.ModelSerializer):
    """Сериализатор для регистрации новых пользователей."""

    email = serializers.EmailField()
    password = serializers.CharField(
        allow_blank=False,
        allow_null=False,
        required=False,
        write_only=True
    )

    class Meta:
        model = User
        fields = (
            'id',
            'first_name',
            'last_name'
            'username',
            'email',
            'password',
        )

    @staticmethod
    def validate_email(value):
        email = value.lower()
        if User.objects.filter(email=email).exists():
            raise ParseError(
                "Пользователь с такой почтой уже существует!"
            )
        return email

    @staticmethod
    def validate_username(value):
        username = value.lower()
        if User.objects.filter(username=username).exists():
            raise ParseError(
                "Пользователь с таким именем уже существует!"
            )
        return username

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для модели User."""

    avatar = Base64ImageField(required=False, allow_null=True)
    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = (
            'id',
            'first_name',
            'last_name',
            'email',
            'username',
            'avatar',
            'is_subscribed',
        )

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return Follow.objects.filter(
            user=request.user
        ).exists()


class UserSearchSerializer(serializers.ModelSerializer):
    class Meta:
        fields = (
            'id',
            'username',
            'full_name',
        )


class AvatarSerializer(serializers.ModelSerializer, ImageMixin):

    class Meta:
        model = User
        fields = ('avatar',)
