from django.utils.translation import ugettext_lazy as _

EATER = 0
VENDOR = 1
ADMIN = 2
GUEST = 3

USER_TYPES = [
    (EATER, 'Eater'),
    (VENDOR, 'Vendor'),
    (ADMIN, 'Admin'),
    (GUEST, 'Guest')
]

DEBIT = 0
CREDIT = 1

TRANSACTION_TYPES = [
    (DEBIT, _('Debit')),
    (CREDIT, _('Credit'))
]

EATER_REWARD = 0
POINTS_EXPENDITURE = 1
EATER_REVIEW = 2
EATER_QR_SCAN = 3
VENDOR_REDEEMED = 4
ADMIN_POINTS = 5
DIETARY_PREFERENCE = 6

TRANSACTION_REASONS = [
    (EATER_REWARD, _('Eater Reward')),
    (POINTS_EXPENDITURE, _('Points Expenditure')),
    (EATER_REVIEW, _('Eater Review')),
    (EATER_QR_SCAN, _('Eater Qr Scan')),
    (VENDOR_REDEEMED, _('Vendor Redeemed')),
    (ADMIN_POINTS, _('Admin Adjustment')),
    (DIETARY_PREFERENCE, _('Dietary Preference')),
]

PENDING = 0
SUCCESS = 1
FAILED = 2

TRANSACTION_STATUS = [
    (PENDING, _('Pending')),
    (SUCCESS, _('Success')),
    (FAILED, _('Failed')),
]
