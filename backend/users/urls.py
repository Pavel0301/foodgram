from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path
from rest_framework import routers

from users.views.users import UserViewSet

router = routers.DefaultRouter()
router.register(r'users', UserViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)