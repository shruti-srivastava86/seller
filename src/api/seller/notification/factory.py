import factory

from seller.notification.models import EmailTemplate, Notifications
from seller.notification import enums


class EmailTemplateFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = EmailTemplate

    type = enums.ONBOARDING
    content = factory.Faker('name')


class NotificationsFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Notifications
