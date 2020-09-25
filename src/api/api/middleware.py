import pytz

from django.conf import settings
from django.utils import timezone
from django.utils.deprecation import MiddlewareMixin
from django.urls import reverse


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def show_toolbar(request):
    """
    Default function to determine whether to show the toolbar on a given page.
    """
    if get_client_ip(request) not in settings.INTERNAL_IPS:
        return False

    return bool(settings.DEBUG)


class TimezoneMiddleware(MiddlewareMixin):
    """
        App handles dates correctly form UTC. However, the Django Admin needs an activated timezone.

        Default this to GB which is where Hawkker (and their admins are based).

        Note this doesn't affect how data is stored, just how it is displayed in the Django Admin.
    """
    def process_request(self, request):
        if request.path.startswith(reverse('admin:index')):
            timezone.activate(pytz.timezone(settings.DEFAULT_ADMIN_TIME_ZONE))
