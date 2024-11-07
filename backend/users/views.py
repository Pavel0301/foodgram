from http import HTTPStatus

from api.serializers import FollowInfoSerializer, FollowSerializer
from django.shortcuts import get_object_or_404
from djoser import views
from rest_framework.decorators import action
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Follow, User
from .serializers import AvatarSerializer, UserSerializer


class UsersViewSet(views.UserViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = LimitOffsetPagination

    @action(
        methods=['GET', 'PATCH'],
        detail=False,
        permission_classes=[IsAuthenticated, ]
    )
    def me(self, request):
        """Получение или обновление пользователя."""
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

    @action(
        methods=['GET', 'PUT', 'DELETE'],
        detail=False,
        permission_classes=[IsAuthenticated, ],
        url_path='me/avatar'
    )
    def avatar(self, request):
        """Получение или обновление аватара пользователя."""
        user = request.user
        if request.method == 'GET':
            if user.avatar:
                return Response({'avatar_url': user.avatar.url},
                                status=HTTPStatus.OK)
            return Response({'detail': 'Аватар не найден'},
                            status=HTTPStatus.NOT_FOUND)
        elif request.method == 'PUT':
            if 'avatar' not in request.data:
                return Response({'detail':
                                 'Файл аватара не был предоставлен.'},
                                status=HTTPStatus.BAD_REQUEST)
            serializer = AvatarSerializer(user, data=request.data,
                                          partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({'avatar': user.avatar.url},
                                status=HTTPStatus.OK)
            return Response({'detail': 'Файл аватара не был предоставлен.'},
                            status=HTTPStatus.BAD_REQUEST)
        elif request.method == 'DELETE':
            if user.avatar:
                user.avatar.delete(save=False)
                user.avatar = None
                user.save()
                return Response({'detail': 'Файл аватара удален.'},
                                status=HTTPStatus.NO_CONTENT)
            return Response({'detail': 'Аватар не найден'},
                            status=HTTPStatus.NOT_FOUND)

    @action(
        methods=['POST', 'DELETE'],
        detail=True,
        permission_classes=[IsAuthenticated, ],
    )
    def subscribe(self, request, **kwargs):
        following = get_object_or_404(User, id=self.kwargs.get('id'))
        data = {'user': request.user.id,
                'following': following.id}
        serializer = FollowSerializer(data=data,
                                      context={'request': request})
        if request.method == 'POST':
            if Follow.objects.filter(user=request.user,
                                     following=following).exists():
                return Response({'error': 'Вы уже подписаны на '
                                 'этого пользователя'},
                                status=HTTPStatus.BAD_REQUEST)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=HTTPStatus.CREATED)
        elif request.method == 'DELETE':
            subscription = Follow.objects.filter(
                user=request.user,
                following=following
            ).first()
            if not subscription:
                return Response(
                    {"error": "Подписки не существует"},
                    status=HTTPStatus.BAD_REQUEST
                )
            subscription.delete()
            return Response(status=HTTPStatus.NO_CONTENT)

    @action(
        methods=['GET', ],
        detail=False,
        permission_classes=[IsAuthenticated, ]
    )
    def subscriptions(self, request):
        user = request.user
        queryset = User.objects.filter(
            following__user=user
        )
        limit = self.paginate_queryset(queryset)
        serializer = FollowInfoSerializer(
            limit,
            many=True,
            context={"request": request}
        )
        return self.get_paginated_response(serializer.data)
