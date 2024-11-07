from rest_framework.serializers import ValidationError

from .models import Ingredients


def recipe_validator(value):
    ingredients = value.get('ingredients')
    tags = value.get('tags')
    image = value.get('image')
    cooking_time = value.get('cooking_time')
    if ingredients is None or tags is None:
        raise ValidationError(
            'Вы не указали ингредиенты или теги.'
        )
    if image is None:
        raise ValidationError(
            'Вы не добавили картинку.'
        )
    if int(cooking_time) < 1:
        raise ValidationError(
            'Время приготовления не может быть меньше 1 минуты.'
        )
    if len(ingredients) < 1 or len(tags) < 1:
        raise ValidationError(
            'Вы не указали ингредиенты или теги.'
        )
    if len(tags) > len(set(tags)):
        raise ValidationError(
            'Теги не должны повторяться.'
        )
    ing_list = []
    for ingredient in ingredients:
        ing_id = ingredient.get('id')
        if ing_id in ing_list:
            raise ValidationError(
                'Ингредиенты не должны повторяться.'
            )
        else:
            ing_list.append(ing_id)
        if not Ingredients.objects.filter(id=ing_id).exists():
            raise ValidationError(f'Ингредиент с id {ing_id} не существует.')
        if ingredient['amount'] < 1:
            raise ValidationError('Колличество ингредиента не может быть '
                                  'меньше 1.')
