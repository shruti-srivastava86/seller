from django.db import models

from seller.chat import enums
from seller.chat.managers import ConversationsQueryset, MessageQueryset
from seller.chat.utils import chat_photo
from seller.models import TimestampedModel


class Message(TimestampedModel):
    """
        Model for storing a conversation message
    """
    objects = MessageQueryset.as_manager()

    user = models.ForeignKey(
        'user.User',
        related_name='user_message',
        null=True,
        blank=True
    )
    conversation = models.ForeignKey(
        'chat.Conversation',
        related_name='conversation_messages'
    )
    message = models.TextField(
        blank=True,
        null=True
    )
    image = models.ImageField(
        upload_to=chat_photo,
        blank=True,
        null=True
    )
    read_by = models.ManyToManyField(
        'user.User',
        blank=True,
        related_name='users_read_messages'
    )

    def mark_read_for_user(self, user):
        self.read_by.add(user)
        return self

    def __str__(self):
        string = "Message: {}".format(str(self.id))
        if self.user:
            string += " -- User: {}".format(self.user.email)
        return string

    class Meta:
        verbose_name = 'Message'
        verbose_name_plural = 'Message'
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['conversation']),
        ]
        ordering = ['-created_at']


class Conversation(TimestampedModel):
    """
        Model for storing a conversation
    """
    objects = ConversationsQueryset.as_manager()

    initiator = models.ForeignKey(
        'user.User',
        related_name='initiator_conversations'
    )
    users = models.ManyToManyField(
        'user.User',
        related_name='users_conversations'
    )
    title = models.CharField(
        max_length=255,
        null=True,
        blank=True
    )
    left_by = models.ManyToManyField(
        'user.User',
        blank=True,
        related_name='users_deleted_conversation'
    )
    complete = models.BooleanField(
        default=False
    )
    chat_type = models.PositiveSmallIntegerField(
        choices=enums.CHAT_TYPES,
        default=enums.SUPPORT
    )

    def __str__(self):
        return "Conversation: " + str(self.id)

    class Meta:
        verbose_name = 'Conversation'
        verbose_name_plural = 'Conversation'
        indexes = [
            models.Index(fields=['initiator']),
            models.Index(fields=['complete']),
        ]
