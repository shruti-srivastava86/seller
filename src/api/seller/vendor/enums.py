from django.utils.translation import ugettext_lazy as _

WEEKDAYS = [
    (0, _("Monday")),
    (1, _("Tuesday")),
    (2, _("Wednesday")),
    (3, _("Thursday")),
    (4, _("Friday")),
    (5, _("Saturday")),
    (6, _("Sunday")),
]

INCOMPLETE = 0
INPROGRESS = 1
COMPLETED = 2
APPROVED = 3
REJECTED = 4
SUSPENDED = 5
DELETE = 6

VENDOR_STATUS = [
    (INCOMPLETE, _('Incomplete')),
    (INPROGRESS, _('In Progress')),
    (COMPLETED, _('Completed')),
    (APPROVED, _('Approved')),
    (REJECTED, _('Rejected')),
    (SUSPENDED, _('Suspended')),
    (DELETE, _('Delete')),
]

STAGE1 = 1
STAGE2 = 2
STAGE3 = 3
STAGE4 = 4
STAGE5 = 5
STAGE6 = 6
STAGE7 = 7

ONBOARDING_STAGE = [
    (STAGE1, _('Stage 1')),
    (STAGE2, _('Stage 2')),
    (STAGE3, _('Stage 3')),
    (STAGE4, _('Stage 4')),
    (STAGE5, _('Stage 5')),
    (STAGE6, _('Stage 6')),
    (STAGE7, _('Stage 7'))
]
