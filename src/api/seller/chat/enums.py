from django.utils.translation import ugettext_lazy as _

SUPPORT = 1
NOTIFICATIONS = 2
HAWKKER_CONNECT = 3
NEW_MESSAGES = 0
OLD_MESSAGES = 1

CHAT_TYPES = [
    (SUPPORT, _("Support")),
    (NOTIFICATIONS, _("Notifications")),
    (HAWKKER_CONNECT, _("Hawkker Connect"))
]
