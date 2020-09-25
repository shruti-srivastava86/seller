import binascii
import os

from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _


class Token(models.Model):
    """A token used for authentication

    The different here over DRF's builtin authtoken module is that these authtokens are not
    strictly 1 per user. A user can (and should) be allowed to login to multiple places at
    once
    """
    key = models.CharField(_("Key"), max_length=40, primary_key=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name='auth_token',
        on_delete=models.CASCADE, verbose_name=_("User")
    )

    created = models.DateTimeField(_("Created"), auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = self.generate_key()
        return super(Token, self).save(*args, **kwargs)

    def generate_key(self):
        return binascii.hexlify(os.urandom(20)).decode()

    def __str__(self):
        return self.key
