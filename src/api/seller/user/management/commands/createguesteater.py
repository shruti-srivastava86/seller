from django.conf import settings
from django.core.management.base import BaseCommand

from seller.authentication.token import create_guest_token
from seller.eater.models import Eater


class Command(BaseCommand):
    help = 'To create a guest eater'

    def handle(self, *args, **options):
        guest_email = settings.DEFAULT_FROM_EMAIL.replace('@', '+guest@')
        guest_user = Eater.objects.filter(email=guest_email).first()
        if not guest_user:
            guest_user = Eater.objects.create_guest_user(email=guest_email,
                                                         name='Guest Eater')
        token = create_guest_token(guest_user)
        self.stdout.write(
            'Guest auth token created with Token: {}'.format(token.key)
        )
