from django.db import models


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
            models.CheckConstraint(
                name="%(app_label)s_%(class)s_prevent_self_chat",
                check=~models.Q(starter=models.F("receiver")),
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
            # User is not in the chat don't create message
            pass
        else:
            super().save(*args, **kwargs)
