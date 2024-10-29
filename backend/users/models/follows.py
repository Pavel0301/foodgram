from django.db import models


class Follow(models.Model):
    user = models.ForeignKey(
        'users.User', on_delete=models.CASCADE, related_name='follower'
    )
    following = models.ForeignKey(
        'users.User', on_delete=models.CASCADE, related_name='following'
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        ordering = ('user',)

        constraints = [
            models.UniqueConstraint(
                fields=('user', 'following'),
                name='unique_follow',
            )
        ]

    def __str__(self):
        return f'Пользователь {self.user.username} подписан(а) на {self.following.username}'