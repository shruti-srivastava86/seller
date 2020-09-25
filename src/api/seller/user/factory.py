import factory

from seller.user.models import User, GeneralSettings, ReportVendorList


class GeneralSettingsFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = GeneralSettings

    one_coin_to_pounds = 1
    minimum_coins_redeemable = 10
    maximum_coins_redeemable = 100
    coins_incremental_value = 1
    review_points = 50
    scan_qr_points = 50
    eater_review_reminder = 10
    vendor_checkin_reminder_before_time = 10
    vendor_checkin_reminder_after_time = 10
    dietary_preference = 10
    minimum_reviews_vendor = 10


class BaseUserFactory(factory.django.DjangoModelFactory):
    """
        Factory for creating a User object.
    """

    class Meta:
        model = User

    name = factory.Faker('name')
    email = factory.LazyAttribute(
        lambda a: '{0}.{1}@xyz.com'.format(
            a.name.split(" ")[0],
            a.name.split(" ")[1]).lower()
    )


class ReportVendorFactory(factory.django.DjangoModelFactory):
    """
        Factory for creating Report vendor list
    """

    class Meta:
        model = ReportVendorList

    name = factory.Faker('name')
