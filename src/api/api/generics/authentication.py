from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import update_last_login

from rest_framework.authentication import TokenAuthentication as BaseAuthentication
from rest_framework.authentication import get_authorization_header
from rest_framework import exceptions

from seller.user import enums
from seller.vendor import enums as vendor_enums
from seller.authentication.models import Token


class TokenAuthentication(BaseAuthentication):
    model = Token

    def authenticate_credentials(self, key):
        model = self.model
        try:
            token = model.objects.select_related('user').get(key=key)
        except model.DoesNotExist:
            raise exceptions.AuthenticationFailed(
                _('You are logged out on another device with the same account. Please re-login and try again.'))

        if not token.user.is_active and token.user.user_type == 0:
            raise exceptions.AuthenticationFailed(
                _('You account has been blocked. For further information please contact Hawkker.'))

        if token.user.user_type == enums.VENDOR:
            if token.user.vendor.status == vendor_enums.INCOMPLETE:
                token.user.vendor.status = vendor_enums.INPROGRESS
                token.user.vendor.save()
        update_last_login(None, token.user)
        return (token.user, token)

    def authenticate(self, request):
        auth = get_authorization_header(request).split()

        if not auth or auth[0].lower() != b'token':
            return None

        if len(auth) == 1:
            msg = _('Invalid token header. No credentials provided.')
            raise exceptions.AuthenticationFailed(msg)
        elif len(auth) > 2:
            msg = _('Invalid token header. Token string should not contain spaces.')
            raise exceptions.AuthenticationFailed(msg)

        try:
            token = auth[1].decode()
        except UnicodeError:
            msg = _('Invalid token header. Token string should not contain invalid characters.')
            raise exceptions.AuthenticationFailed(msg)

        return self.authenticate_credentials(token)
