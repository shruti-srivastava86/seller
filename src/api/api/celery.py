from __future__ import absolute_import, unicode_literals
import os
import celery

from django.conf import settings

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'api.settings')

if settings.USE_SENTRY:
    import raven
    from raven.contrib.celery import register_signal, register_logger_signal


class Celery(celery.Celery):

    def on_configure(self):
        if not settings.USE_SENTRY:
            return

        client = raven.Client(settings.SENTRY_DSN)

        # register a custom filter to filter out duplicate logs
        register_logger_signal(client)

        # hook into the Celery error handler
        register_signal(client)


app = Celery('api', broker=settings.CELERY_BROKER_URL)
app.config_from_object('django.conf:settings')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
