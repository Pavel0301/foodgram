from django.db.models import Sum
from django.http import HttpResponse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django_filters.rest_framework import (DjangoFilterBackend, FilterSet,
                                           filters)
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import SAFE_METHODS, AllowAny, IsAuthenticated
from rest_framework.response import Response

from .models import (Favorite, Ingredients, IngredientsRecipe, Recipe,
                     ShoppingCart, Tags)
from .permissions import IsAdminOrReadOnly, IsAuthor
from .serializers import (FavoriteSerializer, IngredientsSerializer,
                          RecipeReadSerializer, RecipeSerializer,
                          ShoppingSerializer, TagsSerializer)


class RecipeFilter(FilterSet):
    tags = filters.AllValuesMultipleFilter(field_name='tags__slug')
    is_favorited = filters.BooleanFilter(
        method="filter_is_favorited"
    )
    is_in_shopping_cart = filters.BooleanFilter(
        method="filter_is_in_shopping_cart"
    )

    class Meta:
        model = Recipe
        fields = ("tags", "author", "is_favorited", "is_in_shopping_cart")

    def filter_is_favorited(self, queryset, name, value):
        if value and self.request and self.request.user.is_authenticated:
            return queryset.filter(favorites__user=self.request.user)
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        if value and self.request and self.request.user.is_authenticated:
            return queryset.filter(shopping_cart__user=self.request.user)
        return queryset


class IngredientFilter(FilterSet):

    name = filters.CharFilter(lookup_expr="startswith")

    class Meta:
        model = Ingredients
        fields = ("name",)


class RecipeViewSet(viewsets.ModelViewSet):
    """Вьюсет для работы с рецептами."""

    queryset = Recipe.objects.all()
    pagination_class = LimitOffsetPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return RecipeReadSerializer
        return RecipeSerializer

    def get_permissions(self):
        if self.action == 'create':
            return (IsAuthenticated(),)
        if self.action in ['destroy', 'update', 'partial_update']:
            return (IsAuthor(),)
        return (AllowAny(),)

    @action(detail=True, methods=['get'], url_path='get-link')
    def get_link(self, request, pk=None):
        try:
            recipe = self.get_object()
            recipe_id = urlsafe_base64_encode(force_bytes(recipe.id))
            short_link = request.build_absolute_uri(f'/recipes/{recipe_id}/')
            return Response({'short-link': short_link},
                            status=status.HTTP_200_OK)
        except Recipe.DoesNotExist:
            return Response({'detail': 'Рецепт не найден.'},
                            status=status.HTTP_404_NOT_FOUND)

    @action(
        detail=True,
        methods=['POST', 'DELETE'],
        permission_classes=[IsAuthenticated, ],
    )
    def favorite(self, request, pk):
        if not Recipe.objects.filter(id=pk).exists():
            return Response(
                {'error': 'Данного рецепта не существует.'},
                status=status.HTTP_404_NOT_FOUND
            )
        if not request.user.is_authenticated:
            return Response(
                {'error': 'Вы должны быть аутентифицированы для добавления в '
                 'избранное.'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        recipe = Recipe.objects.get(id=pk)
        data = {
            'user': request.user.id,
            'recipe': recipe.id
        }
        serializer = FavoriteSerializer(data=data,
                                        context={'request': request})
        if request.method == 'POST':
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        favorite = Favorite.objects.filter(
            recipe=recipe,
            user=request.user
        )
        if not favorite:
            return Response({"error": "Подписки не существует"},
                            status=status.HTTP_400_BAD_REQUEST)
        favorite.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=['POST', 'DELETE'],
        permission_classes=[IsAuthenticated, ],
    )
    def shopping_cart(self, request, pk):
        if not Recipe.objects.filter(id=pk).exists():
            return Response(
                {'error': 'Данного рецепта не существует.'},
                status=status.HTTP_404_NOT_FOUND
            )
        if not request.user.is_authenticated:
            return Response(
                {'error': 'Вы должны быть аутентифицированы для добавления в '
                 'избранное.'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        recipe = Recipe.objects.get(id=pk)
        data = {
            'user': request.user.id,
            'recipe': recipe.id
        }
        serializer = ShoppingSerializer(data=data,
                                        context={'request': request})
        if request.method == 'POST':
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        favorite = ShoppingCart.objects.filter(
            recipe=recipe,
            user=request.user
        )
        if not favorite:
            return Response({"error": "Подписки не существует"},
                            status=status.HTTP_400_BAD_REQUEST)
        favorite.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @staticmethod
    def ingredients_in_file(ingredients):
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
        user = request.user
        ingredients = IngredientsRecipe.objects.filter(
            recipe__shopping_cart__user=user
        ).values(
            'ingredients__name', 'ingredients__measurement_unit'
        ).annotate(sum=Sum('amount')).order_by('ingredients__name')
        if not ingredients.exists():
            return HttpResponse("Вы ничего не добавляли в список покупок",
                                content_type='text/plain')
        shopping_cart = self.ingredients_in_file(ingredients)
        return HttpResponse(shopping_cart, content_type='text/plain')


class IngredientsViewSet(viewsets.ModelViewSet):
    """Вьюсет для работы с ингредиентами."""

    queryset = Ingredients.objects.all()
    serializer_class = IngredientsSerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class TagsViewSet(viewsets.ModelViewSet):
    """Вьюсет для работы с тегами."""

    queryset = Tags.objects.all()
    serializer_class = TagsSerializer
    permission_classes = (IsAdminOrReadOnly,)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
