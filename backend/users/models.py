from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models

USER = 'user'
MODERATOR = 'moderator'
ADMIN = 'admin'
CHOICES = [
    ('admin', ADMIN),
    ('moderator', MODERATOR),
    ('user', USER)
]


class User(AbstractUser):
    """Класс для работы с пользователями."""

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = (
        'username',
        'first_name',
        'last_name'
    )

    email = models.EmailField(
        'Адрес электронной почты',
        unique=True,
        error_messages={
            'unique': 'Пользователь с такой электронной почтой '
            'уже зарегистрирован'
        }
    )
    username = models.CharField(
        'Имя пользователя',
        max_length=150,
        unique=True,
        error_messages={
            'unique': 'Пользователь с таким именем уже зарегистрирован'
        },
        validators=[RegexValidator(regex=r'^[\w.@+-]+$',
                                   message='Недопустимые символы в '
                                   'имени пользователя')]
    )
    first_name = models.CharField(
        'Имя',
        max_length=150,
    )
    last_name = models.CharField(
        'Фамилия',
        max_length=150,
    )
    avatar = models.ImageField('Аватар', blank=True, null=True)
    role = models.CharField(
        'Права юзера',
        max_length=30, choices=CHOICES, default='user'
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ['username', 'email']

    def __str__(self):
        return self.username

    @property
    def is_user(self):
        return self.role == USER

    @property
    def is_admin(self):
        return self.role == ADMIN

    @property
    def is_moderator(self):
        return self.role == MODERATOR

    def save(self, *args, **kwargs):
        if self.role == self.is_admin:
            self.is_staff = True
        super().save(*args, **kwargs)


class Follow(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='follower'
    )
    following = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='following'
    )

    class Meta:
        ordering = ('user',)
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'following'),
                name='unique_follow'
            )
        ]

    def __str__(self):
        return f'{self.user.username} подписан(а) на {self.following.username}'
