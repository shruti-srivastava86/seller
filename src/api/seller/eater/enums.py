from django.utils.translation import ugettext_lazy as _

ACTIVE = 1
SUSPEND = 2

EATER_STATUS = (
    (ACTIVE, _('Active')),
    (SUSPEND, _('Suspend'))
)

EMAIL_SIGNUP = 0
FACEBOOK_SIGNUP = 1

TYPE_CHOICE = (
    (EMAIL_SIGNUP, "Email"),
    (FACEBOOK_SIGNUP, "Facebook"),
)
