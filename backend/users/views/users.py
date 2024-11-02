from django.contrib.auth import get_user_model
from djoser import views
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import (IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response

from users.models.follows import Follow
from users.serializers.api import users as user_s
from users.serializers.api.follows import FollowSerializer

User = get_user_model()


class UserViewSet(views.UserViewSet):
    """Вьюсет для работы с объектами пользователя и подписок."""

    queryset = User.objects.all()
    serializer_class = user_s.UserSerializer
    pagination_classes = LimitOffsetPagination
    permission_classes = (IsAuthenticatedOrReadOnly,)

    @action(
        detail=False,
        methods=('get',),
        permission_classes=(IsAuthenticated,),
        url_path='subscription',
        url_name='subscription',
    )
    def subscribtions(self, request):
        """Метод создания подписок."""

        user = request.user
        queryset = User.objects.filter(follow__user=user)

        if queryset:
            pages = self.paginate_queryset(queryset)
            serializer = FollowSerializer(
                pages,
                many=True,
                context={'request': request}
            )
            return self.get_paginated_response(serializer.data)
        return Response(
            'В данный момент нет подписок.',
            status=status.HTTP_400_BAD_REQUEST
        )

    @action(
        detail=True,
        methods=('post', 'delete'),
        permission_classes=(IsAuthenticated,),
        url_path='subscribe',
        url_name='subscribe',
    )
    def subscribe(self, request, pk):
        """Метод позволяет управлять подписками."""

        user = request.user
        author = get_object_or_404(User, pk=pk)
        subscribe_status = Follow.objects.filter(
            user=user.id,
            author=author.id,
        )

        if request.method == 'POST':
            if user == author:
                return Response(
                    'Вы не можете подписаться на себя!',
                    status=status.HTTP_400_BAD_REQUEST
                )
            if subscribe_status.exists():
                return Response(
                    f'Вы уже подписаны на {author}',
                    status=status.HTTP_400_BAD_REQUEST
                )
            subscribe = Follow.objects.create(
                user=user,
                author=author
            )
            subscribe.save()
            return Response(
                f'Вы подписались на {author}',
                status=status.HTTP_201_CREATED
            )

        if subscribe_status.exists():
            subscribe_status.delete()
            return Response(
                f'Вы отписались от {author}',
                status=status.HTTP_204_NO_CONTENT
            )
        return Response(
            f'Вы не подписаны на {author}',
            status=status.HTTP_400_BAD_REQUEST
        )

    @action(
        methods=('get', 'patch'),
        detail=False,
        permission_classes=(IsAuthenticated, )
    )
    def me(self, request):
        """Получение или обновление пользователя."""
        serializer = user_s.UserSerializer(request.user)
        return Response(serializer.data)

    @action(
        methods=('get', 'put', 'delete'),
        detail=False,
        permission_classes=(IsAuthenticated, ),
        url_path='me/avatar'
    )
    def avatar(self, request):
        """Получение или обновление аватара пользователя."""
        user = request.user
        if request.method == 'GET':
            if user.avatar:
                return Response({'avatar_url': user.avatar.url},
                                status=status.HTTP_200_OK)
            return Response({'detail': 'Аватар не найден'},
                            status=status.HTTP_204_NO_CONTENT)
        elif request.method == 'PUT':
            if 'avatar' not in request.data:
                return Response({'detail':
                                     'Файл аватара не был предоставлен.'},
                                status=status.HTTP_400_BAD_REQUEST)
            serializer = user_s.AvatarSerializer(user, data=request.data,
                                          partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({'avatar': user.avatar.url},
                                status=status.HTTP_200_OK)
            return Response({'detail': 'Файл аватара не был предоставлен.'},
                            status=status.HTTP_400_BAD_REQUEST)
        elif request.method == 'DELETE':
            if user.avatar:
                user.avatar.delete(save=False)
                user.avatar = None
                user.save()
                return Response({'detail': 'Файл аватара удален.'},
                                status=status.HTTP_204_NO_CONTENT)
            return Response({'detail': 'Аватар не найден'},
                            status=status.HTTP_400_BAD_REQUEST)
