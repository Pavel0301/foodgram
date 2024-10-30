import base64
from django.core.files.base import ContentFile
from rest_framework import serializers


class Base64ImageField(serializers.ImageField):
    """Кастомное поле для картинок."""

    def to_internal_field(self, data):
        """Метод для преобразования картинок."""

        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='photo.' + ext)

        return super().to_internal_value(data)


class ImageMixin:
    image = Base64ImageField(required=False, allow_null=True)


class ImageUrlMixin:
    image = Base64ImageField(use_url=True)
