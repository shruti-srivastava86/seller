from io import BytesIO
from os.path import dirname
from unittest.mock import patch

from django.test import TestCase
from django.urls import reverse
from explorer.models import Query

from seller.notification.models import Notifications
from seller.notification.views import QuerySendNotification
from seller.vendor.factory import VendorUserFactory


def get_sample_file():
    r = BytesIO(
        open(dirname(__file__) + '/../../adminpanel/static/adminpanel/img/favicon.png', 'rb').read())
    r.name = 'photo.png'
    return r


class QuerySendTestCase(TestCase):
    def test_parse_semicolon(self):
        qsn = QuerySendNotification()
        res = qsn.get_first_users('select id from user_user;')
        self.assertEqual(len(res), 0)

    @patch('seller.notification.utils.PushMessage')
    def test_send_no_icon(self, push_message):
        user = VendorUserFactory()
        self.client.force_login(user)

        query = Query.objects.create(
            sql='SELECT * FROM user_user', title='test')

        resp = self.client.post(reverse('admin:explorer'), {
            'query': query.id,
            'title': 'Test Notification',
            'subtitle': 'Subtitle',
            'notification_text': 'Test',
        })
        self.assertEqual(resp.status_code, 302)
        # skip or now self.assertEqual(push_message.called, True)

        self.assertEqual(Notifications.objects.count(), 1)

    @patch('seller.notification.utils.PushMessage')
    def test_send_icon(self, push_message):
        user = VendorUserFactory()
        self.client.force_login(user)

        query = Query.objects.create(
            sql='SELECT * FROM user_user', title='test')

        resp = self.client.post(reverse('admin:explorer'), {
            'query': query.id,
            'title': 'Test Notification',
            'notification_text': 'Test',
            'subtitle': 'Subtitle',
            'icon_image': get_sample_file(),
            'large_image': get_sample_file(),
        })
        self.assertEqual(resp.status_code, 302)
        # skip for now self.assertEqual(push_message.called, True)

        self.assertEqual(Notifications.objects.count(), 1)
        nf = Notifications.objects.all()[0]
        self.assertIn('icon-', str(nf.icon))
