from django.db.models import Sum
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import SAFE_METHODS, AllowAny, IsAuthenticated
from rest_framework.response import Response

from recipes.filters import IngredientFilter, RecipeFilter
from recipes.models.recipes import (Favorite, Ingredient, IngredientInRecipe,
                                    Recipe, ShoppingCart, Tag)
from recipes.permissions import IsAdminOrReadOnly, IsAuthor
from recipes.serializers.api.recipe import (AddFavoriteSerializer,
                                            CreateRecipeSerializer,
                                            RecipeSerializer)
from recipes.serializers.nested.recipe import (IngredientSerializer,
                                               TagSerializer)


class RecipeViewSet(viewsets.ModelViewSet):
    """Вьюсет для работы запросов к рецептам."""

    queryset = Recipe.objects.all()
    pagination_classes = LimitOffsetPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        """Метод по условиям вызывает определенный сериализатор."""

        if self.request.method in SAFE_METHODS:
            return RecipeSerializer
        return CreateRecipeSerializer

    def get_serializer_context(self):
        """Метод меняет передаваемы контекст."""

        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    def get_permissions(self):
        if self.action == 'create':
            return (IsAuthenticated(),)
        if self.action in ['destroy', 'update', 'partial_update']:
            return (IsAuthor(),)
        return (AllowAny(),)

    @action(
        detail=True,
        methods=('post', 'delete', ),
        permission_classes=(IsAuthenticated,),
        url_path='favorite',
        url_name='favorite',
    )
    def favorite(self, request, pk):
        """Метод позваоляет управлять подписками."""

        user = request.user
        recipe = get_object_or_404(Recipe, pk=pk)
        favorite = Favorite.objects.filter(recipe=recipe, user=user)

        if request.method == 'POST':

            if favorite.exists():
                return Response(
                    f'Нельзя повторно добавить в избранное {recipe.name}',
                    status=status.HTTP_400_BAD_REQUEST,
                )
            Favorite.objects.create(recipe=recipe, user=user)
            serializer = AddFavoriteSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if favorite.exists():
            favorite.delete()
            return Response(
                f'Вы успешно удалили из избранного {recipe.name}',
                status=status.HTTP_204_NO_CONTENT,
            )
        return Response(
            f'Вы не добавлялись в избранное {recipe.name}',
            status=status.HTTP_400_BAD_REQUEST,
        )

    @action(
        detail=True,
        methods=['POST', 'DELETE'],
        permission_classes=[IsAuthenticated, ],
    )
    def shopping_card(self, request, pk):
        """Метод позваоляет управлять корзиной."""

        user = request.user
        recipe = get_object_or_404(Recipe, pk=pk)
        shopping_cart = ShoppingCart.objects.filter(user=user, recipe=recipe)

        if request.method == 'POST':

            if shopping_cart.exists():
                return Response(
                    f'Рецепт {recipe.name} уже был добавлен в корзину.',
                    status=status.HTTP_400_BAD_REQUEST,
                )
            ShoppingCart.objects.create(user=user, recipe=recipe)
            serializer = AddFavoriteSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if shopping_cart.exists():
            shopping_cart.delete()
            return Response(
                f'Рецепт {recipe.name} был удален из корзины.',
                status=status.HTTP_204_NO_CONTENT,
            )
        return Response(
            f'Нельзя удалить рецепт {recipe.name}.',
            status=status.HTTP_400_BAD_REQUEST,
        )

    def _put_ingredients_in_file(self, ingredients):
        text = ''
        for ingredient in ingredients:
            text += (
                f"{ingredient['ingredients__name']} "
                f"({ingredient['ingredients__measurement_unit']}) - "
                f"{ingredient['sum']}\n"
            )
        return text


    @action(
        methods=['GET', ],
        detail=False,
        permission_classes=[IsAuthenticated, ]
    )
    def download_shopping_cart(self, request):
        """Метод позволяет скачать корзину покупок."""

        ingredients = IngredientInRecipe.objects.filter(
            recipe__shopping_cart__user=request.user
        ).values(
            'ingredients__name',
            'ingredients__measurement_unit',
        ).annotate(
            sum=Sum('amount')
        )
        ingredients_list = self._put_ingredients_in_file(ingredients)
        return Response(ingredients_list, content_type='text/plain')


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет для работы с ингредиентами."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет работы с обьектами класса Tag."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (IsAdminOrReadOnly,)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
