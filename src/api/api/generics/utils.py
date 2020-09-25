from django.conf import settings
from django.core.mail import get_connection, EmailMultiAlternatives
from rest_framework import status
from rest_framework.response import Response


if settings.USE_SENTRY:
    from raven.contrib.django.raven_compat.models import client
else:
    from unittest.mock import MagicMock
    client = MagicMock()


class Utils:
    @staticmethod
    def error_response_400(error):
        return Response({"error": error}, status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def message_response_200(message):
        return Response({"message": message}, status=status.HTTP_200_OK)

    @staticmethod
    def response_201():
        return Response(status=status.HTTP_201_CREATED)

    @staticmethod
    def validation_error(e):
        client.captureException()
        return Utils.error_response_400(str(e.args[0][list(e.args[0].keys())[0]][0]))

    @staticmethod
    def exception_error(e):
        client.captureException()
        return Utils.error_response_400(str(e))


def send_mail(subject, message, from_email, recipient_list=None, bcc=None,
              fail_silently=False, auth_user=None, auth_password=None,
              connection=None, html_message=None):
    """
    Easy wrapper for sending a single message to a recipient list. All members
    of the recipient list will see the other recipients in the 'To' field.

    If auth_user is None, the EMAIL_HOST_USER setting is used.
    If auth_password is None, the EMAIL_HOST_PASSWORD setting is used.

    Note: The API for this method is frozen. New code wanting to extend the
    functionality should use the EmailMessage class directly.
    """
    connection = connection or get_connection(
        username=auth_user,
        password=auth_password,
        fail_silently=fail_silently,
    )
    mail = EmailMultiAlternatives(subject, message, from_email, recipient_list, bcc, connection=connection)
    if html_message:
        mail.attach_alternative(html_message, 'text/html')

    return mail.send()
