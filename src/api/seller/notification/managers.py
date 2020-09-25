from django.db import models


class NotificationQuerySet(models.QuerySet):

    def unread_count(self):
        return self.filter(read=False).count()

    def for_review(self, type):
        return self.filter(notification_type=type)

    def with_unread(self):
        return self.filter(read=False)

    def with_read(self):
        return self.filter(read=True)

    def for_user(self, user):
        return self.filter(user=user)
