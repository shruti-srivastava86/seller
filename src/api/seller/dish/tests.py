from django.urls import reverse
from rest_framework import status

from seller.vendor.tests import VendorListAPITest


class DishApiTest(VendorListAPITest):

    def test_dish_information(self):
        """
            For testing retrieval of all dishes for eater
        :return:
        """
        self.url = reverse("seller.mobile.dish:dish")
        self.client.force_authenticate(user=self.eater)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('results' in response.data)
        if 'results' in response.data:
            data = response.data['results'][0]
            self.assertTrue('dietary_information' in data)
            self.assertTrue('name' in data)
            self.assertTrue('price' in data)
            self.assertTrue('temporary_price' in data)
            self.assertTrue('description' in data)
            self.assertTrue('special' in data)
            self.assertTrue('active' in data)

    def test_all_dietary(self):
        """
            For testing retrieval of all dietary for eater
        :return:
        """
        self.url = reverse("seller.mobile.dish:dietary")
        self.client.force_authenticate(user=self.eater)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('results' in response.data)
        if 'results' in response.data:
            data = response.data['results'][0]
            self.assertTrue('id' in data)
            self.assertTrue('name' in data)

    def test_all_allergens(self):
        """
             For testing retrieval of all allergens for eater
        :return:
        """
        self.url = reverse("seller.mobile.dish:allergens")
        self.client.force_authenticate(user=self.eater)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('results' in response.data)
        if 'results' in response.data:
            data = response.data['results'][0]
            self.assertTrue('id' in data)
            self.assertTrue('name' in data)

    def test_all_cuisines(self):
        """
             For testing retrieval of all cuisines for eater
        :return:
        """
        self.url = reverse("seller.mobile.dish:cuisines")
        self.client.force_authenticate(user=self.eater)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('results' in response.data)
        if 'results' in response.data:
            data = response.data['results'][0]
            self.assertTrue('id' in data)
            self.assertTrue('name' in data)

    def test_all_allergens_web(self):
        """
             For testing retrieval of all allergens for vendor web
        :return:
        """
        self.url = reverse("seller.web.dish:allergens")
        self.client.force_authenticate(user=self.vendor)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data[0]
        self.assertTrue('id' in data)
        self.assertTrue('name' in data)

    def test_all_cuisines_web(self):
        """
             For testing retrieval of all cuisines for vendor web
        :return:
        """
        self.url = reverse("seller.web.dish:cuisines")
        self.client.force_authenticate(user=self.vendor)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data[0]
        self.assertTrue('id' in data)
        self.assertTrue('name' in data)

    def test_all_dietary_web(self):
        """
            For testing retrieval of all dietary
        :return:
        """
        self.url = reverse("seller.web.dish:dietary")
        self.client.force_authenticate(user=self.vendor)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('results' in response.data)
        if 'results' in response.data:
            data = response.data['results'][0]
            self.assertTrue('id' in data)
            self.assertTrue('name' in data)
