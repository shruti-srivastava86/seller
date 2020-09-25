from django.utils.translation import ugettext_lazy as _

ONBOARDING = 0
FORGOT_PASSWORD = 1
APPROVE_EMAIL = 2
PROMOTIONAL_EMAIL = 3
REJECT_EMAIL = 4
REMIND_COMPLETE = 5
REPORT_VENDOR = 6
SUPPORT = 7

EMAIL_TYPE = [
    (ONBOARDING, _('Onboarding')),
    (FORGOT_PASSWORD, _('Forgot Password')),
    (APPROVE_EMAIL, _('Approve Email')),
    (REJECT_EMAIL, _('Rejection Email')),
    (REMIND_COMPLETE, _('Remind Completion Email')),
    (PROMOTIONAL_EMAIL, _('Promotional Email')),
    (REPORT_VENDOR, _('Report Vendor')),
    (SUPPORT, _('Support')),
]
