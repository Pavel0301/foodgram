from django.urls import include, path
from rest_framework import routers

from .views import IngredientsViewSet, RecipeViewSet, TagsViewSet

router = routers.DefaultRouter()
router.register(r'recipes', RecipeViewSet)
router.register(r'ingredients', IngredientsViewSet)
router.register(r'tags', TagsViewSet)

urlpatterns = [
    path('', include(router.urls))
]
