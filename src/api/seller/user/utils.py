import os
import uuid

from django.conf import settings
from django.urls import reverse

from seller.authentication.token import regenerate_token
from seller.user import enums
from seller.user.models import ForgotPassword
from seller.notification.email import HawkkerEmailMessage
from seller.notification import enums as notification_enums


class UserUtils(object):

    @staticmethod
    def generate_random_token():
        return uuid.uuid4().hex


def vendor_photo(instance, filename):
    extension = os.path.splitext(str(filename))[1]
    filename = str(uuid.uuid4()) + extension
    return 'vendor/{}/'.format(instance.id) + filename


def business_photo(instance, filename):
    extension = os.path.splitext(str(filename))[1]
    filename = str(uuid.uuid4()) + extension
    return 'vendor/business/' + filename


def create_forgot_password_object(user, token):
    forgot_password, created = ForgotPassword.objects.get_or_create(user=user)
    forgot_password.token = token
    forgot_password.save()


def send_forgot_password_email(user):
    token = regenerate_token(user)
    create_forgot_password_object(user, token.key)
    if user.user_type == enums.EATER:
        url = settings.BASE_URL + reverse(
            'seller.mobile.eater:forgot_password',
            kwargs={'token': token}
        )
    elif user.user_type == enums.VENDOR:
        url = settings.BASE_URL + reverse(
            'seller.mobile.vendor:forgot_password',
            kwargs={'token': token}
        )
    else:
        url = settings.BASE_URL + reverse(
            'forgot_password',
            kwargs={'token': token}
        )

    HawkkerEmailMessage(
        email_type=notification_enums.FORGOT_PASSWORD,
        template_name='templated_email/forgot_password.email',
        context={
            'link': url,
            'user': user,
        }).send(to=[user.email])
