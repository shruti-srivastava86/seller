from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from seller.eater.factory import EaterUserFactory
from seller.notification.factory import NotificationsFactory
from seller.vendor.factory import MarketFactory
from seller.vendor.tests import VendorListAPITest


class EaterApiTest(APITestCase):
    """
        Test cases for eater
    """

    def setUp(self):
        self.eater = EaterUserFactory()
        self.url = reverse("seller.mobile.eater:profile")
        self.client.force_authenticate(user=self.eater)
        self.market = MarketFactory()
        self.notifications = NotificationsFactory(
            user=self.eater,
            message="text",
            content_object=self.eater,
            context="test"
        )

    def test_get_eater_profile(self):
        """
            Test case for retrieving an eater profile
        :return:
        """
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue("name" in response.data)
        self.assertTrue("id" in response.data)
        self.assertTrue("email" in response.data)
        self.assertTrue("dietary_preference" in response.data)
        self.assertTrue("coins" in response.data)
        self.assertTrue("pounds" in response.data)

    def test_edit_eater_profile(self):
        """
            Test case for editing an eater profile
        :return:
        """
        self.name = "def"
        response = self.client.patch(self.url, {"name": self.name})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('name'), self.name)

    def test_eater_markets(self):
        """
        Test case for eatert markets
        :return:
        """
        self.url = reverse("seller.mobile.eater:markets")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue("name" in response.data[0])
        self.assertTrue("id" in response.data[0])

    def test_eater_notification(self):
        """

        :return:
        """
        self.url = reverse("seller.mobile.eater:notifications")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        if "results" in response.data:
            data = response.data['results'][0]
            self.assertTrue("created_at" in data)
            self.assertTrue("updated_at" in data)
            self.assertTrue("message" in data)
            self.assertTrue("read" in data)
            self.assertTrue("icon" in data)
            self.assertTrue("user" in data)
            self.assertTrue("notification_type" in data)
            self.assertTrue("image" in data)

    def test_eater_notification_read(self):
        """

        :return:
        """
        self.url = reverse("seller.mobile.eater:notifications-read",
                           kwargs={'pk': self.notifications.id})
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_eater_notification_preferences(self):
        """

        :return:
        """
        self.url = reverse("seller.mobile.eater:notification_preference")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue("id" in response.data)
        self.assertTrue("review" in response.data)
        self.assertTrue("marketing" in response.data)

    def test_eater_notification_unread(self):
        """

        :return:
        """
        self.url = reverse("seller.mobile.eater:unread")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue("unread" in response.data)


class EaterDishApiTestCase(VendorListAPITest):

    def test_eater_dishes(self):
        self.url = reverse("seller.mobile.eater:dishes")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('results' in response.data)
        if 'results' in response.data:
            data = response.data['results'][0]
            self.assertTrue('name' in data)
            self.assertTrue('description' in data)
            self.assertTrue('price' in data)
            self.assertTrue('temporary_price' in data)
            self.assertTrue('special' in data)
            self.assertTrue('dietary_information' in data)

    def test_eater_dietary(self):
        self.url = reverse("seller.mobile.eater:dietary")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('results' in response.data)
        if 'results' in response.data:
            data = response.data['results'][0]
            self.assertTrue('name' in data)
            self.assertTrue("id" in data)

    def test_eater_allergens(self):
        self.url = reverse("seller.mobile.eater:allergens")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('results' in response.data)
        if 'results' in response.data:
            data = response.data['results'][0]
            self.assertTrue('name' in data)
            self.assertTrue("id" in data)

    def test_eater_cuisines(self):
        self.url = reverse("seller.mobile.eater:cuisines")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('results' in response.data)
        if 'results' in response.data:
            data = response.data['results'][0]
            self.assertTrue('name' in data)
            self.assertTrue("id" in data)
