from django.db import models
from django.db.models import Q, Count, Subquery, Case, When, BooleanField, Max


class ConversationsQueryset(models.QuerySet):

    def active(self):
        return self.filter(complete=False)

    def with_id(self, id):
        return self.filter(id=id)

    def for_id(self, conversation_id):
        return self.filter(id=conversation_id)

    def with_chat_type(self, chat_type):
        return self.filter(chat_type=chat_type)

    def for_user(self, user):
        return self.filter((Q(initiator=user) | Q(users__in=[user])))

    def with_exisiting_conversation(self, initiator, user, product):
        queryset = self.with_user_count().filter(
            (Q(initiator=initiator) | Q(initiator=user)) &
            Q(participant_count=2) & Q(users__in=[user]))
        queryset = queryset.filter(Q(users__in=[initiator]))
        return queryset

    def with_messages(self):
        return self.annotate(
            message_count=Count('conversation_messages')
        ).filter(message_count__gt=0)

    def with_user_count(self):
        return self.annotate(participant_count=Count('users', distinct=True))

    def with_unread_message_count(self, subquery):
        unread_count = self.annotate(
            unread_count=Count(Subquery(subquery[:1]))
        )
        return unread_count.annotate(
            unread=Case(
                When(unread_count=0, then=False),
                default=True,
                output_field=BooleanField()
            )
        )

    def with_unread(self, subquery):

        return self.annotate(
            unread_count=Count(Subquery(subquery[:1]))
        )

    def with_last_message_time(self):
        return self.annotate(
            last_message_sent=Max('conversation_messages__created_at')
        )


class MessageQueryset(models.QuerySet):

    def with_prefetch(self):
        return self.select_related('user').prefetch_related('read_by')

    def for_conversation(self, conversation_id):
        return self.filter(conversation=conversation_id)

    def unread(self, user):
        return self.filter(~Q(read_by__in=[user]) & ~Q(user=user))

    def after_message_id(self, message_id):
        return self.filter(id__gt=message_id)

    def before_message_id(self, message_id):
        return self.filter(id__lt=message_id)

    def for_user(self, user):
        return self.filter((Q(conversation__initiator=user) | Q(conversation__users__in=[user])))
