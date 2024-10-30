from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models

User = get_user_model()


class Tag(models.Model):
    """Модель для описания Тегов."""
    name = models.CharField(
        max_length=50,
        unique=True,
        verbose_name='Тег',
    )
    slug = models.SlugField(
        max_length=50,
        unique=True,
        verbose_name='Слаг тега',
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """Модель для описания Ингредиента."""
    name = models.CharField(
        max_length=150,
        db_index=True,
        verbose_name='Название ингредиента',
    )
    measurement_unit = models.CharField(
        max_length=100,
        verbose_name='Единица измерения'
    )
    amount = models.CharField(
        verbose_name='Колличество',
        max_length=50,
        blank=True
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

        ordering = ('name',)

    def __str__(self):
        return f'{self.name}, {self.measurement_unit}'


class Recipe(models.Model):
    """Модель для описания Рецептов."""
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор рецепта',
    )
    name = models.CharField(
        max_length=100,
        verbose_name='Название рецепта',
    )
    image = models.ImageField(
        upload_to='recipes/',
        blank=True,
        verbose_name='Фото рецепта',
    )
    text = models.TextField(
        verbose_name='Описание рецепта',
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientInRecipe',
        related_name='recipes',
        verbose_name='Ингредиенты рецепта',
    )
    tags = models.ManyToManyField(
        Tag,
        related_name='recipes',
        verbose_name='Теги рецепта',
    )
    cooking_time = models.PositiveSmallIntegerField(
        'Время приготовления блюда',
        validators=[
            MinValueValidator(
                1,
                'Минимальное значение 1!'
            )
        ],
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        verbose_name='Дата публикации рецепта',
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

        ordering = ('-created_at',)

    def __str__(self):
        return self.name


class IngredientInRecipe(models.Model):
    """Модели для описания ингредиента в рецепте."""

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='ingredient_list',
        verbose_name='Рецепт'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='in_recipe',
        verbose_name='Ингредиент',
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name='Количество',
        validators=[
            MinValueValidator(
                1,
                message='Минимальное количество 1!',
            )
        ],
    )

    class Meta:
        verbose_name = 'Ингредиент в рецепте'
        verbose_name_plural = 'Ингредиенты в рецепте'
        constraints = [
            models.UniqueConstraint(
                fields=('recipe', 'ingredient'),
                name='unique_ingredients_in_the_recipe',
            )
        ]

    def __str__(self):
        return f'{self.ingredients} {self.recipe}'


class TagInRecipe(models.Model):
    """Модели для создания Тега рецепта."""

    tag = models.ForeignKey(
        Tag,
        on_delete=models.CASCADE,
        verbose_name='Тег рецепта',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
    )

    class Meta:
        verbose_name = 'Тег рецепта'
        verbose_name_plural = 'Теги рецепта'
        constraints = [
            models.UniqueConstraint(
                fields=['tag', 'recipe'],
                name='unique_tagrecipe',
            )
        ]

    def __str__(self):
        return f'{self.tag} {self.recipe}'


class ShoppingCart(models.Model):
    """Модели для описания Корзины покупок."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shopping',
        verbose_name='Пользователь',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipes'
    )

    class Meta:
        verbose_name = 'Корзина покупок'
        verbose_name_plural = 'Корзины покупок'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_shoppingcart'
            )
        ]


class Favorite(models.Model):
    """Модель для описания избранного пользователя."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favourites',
        verbose_name='Пользователь',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favourites'
    )

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное',
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_favourite'
            )
        ]

    def __str__(self):
        return f'{self.user} {self.recipe}'
