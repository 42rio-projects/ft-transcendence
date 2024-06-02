from django.db import models
# from django.core.exceptions import ValidationError


class Chat(models.Model):
    starter = models.ForeignKey(
        'user.User',
        on_delete=models.CASCADE,
        related_name='started_chats'
    )
    receiver = models.ForeignKey(
        'user.User',
        on_delete=models.CASCADE,
        related_name='received_chats'
    )

    def save(self, *args, **kwargs):
        # Essa budega nao funciona nem por um inferno
        # if not self.receiver:
        #     raise ValidationError("Usuário não encontrado.")

        # Verifica se o usuário está na blocklist
        # if self.starter.blocked_users.filter(username=self.receiver.username).exists():
        # raise ValidationError("Você não pode iniciar um chat com um usuário na sua blocklist.")

        if Chat.objects.filter(
                starter=self.receiver, receiver=self.starter
        ).exists():
            # Chat already exists, don't create a duplicate entry
            pass
        else:
            super().save(*args, **kwargs)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                name="%(app_label)s_%(class)s_unique_relationships",
                fields=["starter", "receiver"]
            ),
        ]


class Message(models.Model):
    content = models.CharField(max_length=255)
    date = models.DateTimeField(auto_now_add=True)
    sender = models.ForeignKey(
        'user.User',
        null=True,
        on_delete=models.SET_NULL,
        related_name="messages"
    )
    chat = models.ForeignKey(
        Chat, on_delete=models.CASCADE, related_name="messages"
    )

    def save(self, *args, **kwargs):
        if self.sender != self.chat.starter and \
                self.sender != self.chat.receiver:
            return
        else:
            super().save(*args, **kwargs)
