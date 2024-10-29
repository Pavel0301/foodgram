from django.urls import include, path
from users.urls import urlpatterns as user_s
from recipes.urls import urlpatterns as recipe_s

urlpatterns = [
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]

urlpatterns += user_s
urlpatterns += recipe_s