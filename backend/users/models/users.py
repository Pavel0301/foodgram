from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from users.managers import CustomUserManager

USER = 'user'
MODERATOR = 'moderator'
ADMIN = 'admin'
CHOICES = [
    ('admin', ADMIN),
    ('moderator', MODERATOR),
    ('user', USER)
]


class User(AbstractUser):
    """Модель пользователя"""

    email = models.EmailField(
        verbose_name='Электронная почта',
        unique=True,
        error_messages={
            'unique': 'Пользователь с такой электронной почтой уже зарегистрирован!'
        }
    )
    username = models.CharField(
        max_length=100,
        verbose_name='Имя пользователя',
        unique=True,
        db_index=True,
        error_messages={
            'unique': 'Пользователь с таким именем уже зарегистрирован!'
        },
        validators=[
            RegexValidator(
                regex=r'^[\w/@+-]+$',
                message='Недопустимые символы в имени пользователя!'
            )
        ]
    )
    first_name = models.CharField(
        max_length=100,
        verbose_name='Имя',
    )
    last_name = models.CharField(
        max_length=100,
        verbose_name='Фамилия',
    )
    role = models.CharField(
        verbose_name='Права пользователя',
        max_length=30,
        choices=CHOICES,
        default='user'
    )
    image = models.ImageField(
        verbose_name='Фотография профиля',
        blank=True,
        null=True,
        upload_to='profiles/'
    )

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

        ordering = ('username',)

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

    @property
    def full_name(self):
        return f'{self.first_name} {self.last_name}'

    def save(self, *args, **kwargs):
        if self.role == self.is_admin:
            self.is_staff = True
        super().save(*args, **kwargs)
