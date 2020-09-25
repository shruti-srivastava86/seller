from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase

from seller.vendor.factory import VendorUserFactory, BusinessFactory
from seller.eater.factory import EaterUserFactory
from seller.dish.factory import DishFactory
from seller.user.factory import GeneralSettingsFactory
from seller.purchase.factory import PurchaseFactory


class PurchaseTestCase(APITestCase):
    """Test a purchase
    """

    def setUp(self):
        self.vendor = VendorUserFactory()
        self.business = BusinessFactory(vendor=self.vendor)
        self.eater = EaterUserFactory()
        self.eater.coins = 1000
        self.eater.save()
        self.dish = DishFactory(business=self.business)
        self.url = reverse('seller.mobile.eater:purchase')
        self.scan_url = reverse('seller.mobile.eater:scan')
        self.transaction_url = reverse('seller.mobile.eater:transaction')
        self.purchase = PurchaseFactory.create(
            eater=self.eater,
            vendor=self.vendor,
            details=[
                {
                    "price": "5.00",
                    "id": self.dish.pk,
                    "name": "Something",
                    "quantity": 12
                },
            ],
            waiting_time=10,
            amount=100
        )
        GeneralSettingsFactory()
        self.client.force_authenticate(user=self.eater)

    def test_scan_vendor(self):
        response = self.client.get(self.scan_url,
                                   {"vendor_uuid": self.vendor.uuid}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue("id" in response.data)
        self.assertTrue("name" in response.data)
        self.assertTrue("dietary_information" in response.data)
        self.assertTrue("business" in response.data)

    def test_false_purchase(self):
        """Test sending in a false purchase with an invalid dish
        """

        self.client.force_authenticate(user=self.eater)
        resp = self.client.post(self.url, {
            'vendor_uuid': str(self.vendor.uuid),
            'details': [
                {
                    "price": "5.00",
                    "id": "99",
                    "name": "Something",
                    "quantity": 12
                },
            ],
            'waiting_time': 1
        }, format='json')

        self.assertEqual(
            resp.status_code,
            status.HTTP_400_BAD_REQUEST,
            'Invalid: {}'.format(resp.data))
        self.assertEqual(resp.data, {'details': [
            {'id': ['Invalid pk "99" - object does not exist.']}]})

    def test_purchase(self):
        """Test a normal success
        """

        self.client.force_authenticate(user=self.eater)
        resp = self.client.post(self.url, {
            'vendor_uuid': str(self.vendor.uuid),
            'details': [
                {
                    "price": "5.00",
                    "id": self.dish.pk,
                    "name": "Something",
                    "quantity": 12
                },
            ],
            'waiting_time': 1
        }, format='json')

        self.assertEqual(
            resp.status_code,
            status.HTTP_201_CREATED,
            'Invalid: {}'.format(resp.data))

    def test_eater_purchase_list(self):
        """
        Test for eater purchases list
        :return:
        """
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('results' in response.data)
        if 'results' in response.data:
            data = response.data['results'][0]
            self.assertTrue('id' in data)
            self.assertTrue('details' in data)
            self.assertTrue('vendor' in data)
            self.assertTrue('waiting_time' in data)
            self.assertTrue('dish_not_listed' in data)
            self.assertTrue('not_listed_dish' in data)
            self.assertTrue('created_at' in data)


class TransactionTestCase(PurchaseTestCase):
    """
        Test for eater transactions
    """

    def test_eater_create_transaction(self):
        response = self.client.post(self.transaction_url, {
            'coins': 100
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue('purchase' in response.data)
        self.assertTrue('qr_id' in response.data)
        self.assertTrue('coins' in response.data)
        self.assertTrue('amount' in response.data)
        self.assertTrue('status' in response.data)
        self.assertTrue('note' in response.data)
        self.assertTrue("id" in response.data)

    def test_eater_transactions(self):
        self.client.post(self.url, {
            'vendor_uuid': str(self.vendor.uuid),
            'details': [
                {
                    "price": "5.00",
                    "id": self.dish.pk,
                    "name": "Something",
                    "quantity": 12
                },
            ],
            'waiting_time': 1
        }, format='json')

        response = self.client.get(self.transaction_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('results' in response.data)
        if 'results' in response.data:
            data = response.data['results'][0]
            self.assertTrue('id' in data)
            self.assertTrue('purchase' in data)
            self.assertTrue('vendor' in data)
            self.assertTrue('qr_id' in data)
            self.assertTrue('coins' in data)
            self.assertTrue('amount' in data)
            self.assertTrue('balance' in data)
            self.assertTrue('type' in data)
            self.assertTrue('reason' in data)
            self.assertTrue('status' in data)
            self.assertTrue('note' in data)

    def test_vendor_create_transactions(self):
        """
            Test for creating and retrieveing transactions for vendor in mobile
        :return:
        """
        response = self.client.post(self.transaction_url, {
            'coins': 100
        }, format='json')
        self.url = reverse('seller.mobile.vendor:transaction')

        self.client.force_authenticate(user=self.vendor)
        self.client.post(self.url, {
            "qr_id": response.data.get("qr_id"),
            "note": "redeemed at stall"

        }, format="json")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('results' in response.data)
        if 'results' in response.data:
            data = response.data['results'][0]
            self.assertTrue('id' in data)
            self.assertTrue('purchase' in data)
            self.assertTrue('vendor' in data)
            self.assertTrue('qr_id' in data)
            self.assertTrue('coins' in data)
            self.assertTrue('amount' in data)
            self.assertTrue('balance' in data)
            self.assertTrue('type' in data)
            self.assertTrue('reason' in data)
            self.assertTrue('status' in data)
            self.assertTrue('note' in data)

    def test_vendor_web_create_transactions(self):
        """
            Test for creating and retrieveing transactions for vendor in web

        :return:
        """
        response = self.client.post(self.transaction_url, {
            'coins': 100
        }, format='json')
        self.url = reverse('seller.web.vendor:transaction')

        self.client.force_authenticate(user=self.vendor)
        self.client.post(self.url, {
            "qr_id": response.data.get("qr_id"),
            "note": "redeemed at stall"

        }, format="json")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('results' in response.data)
        if 'results' in response.data:
            data = response.data['results'][0]
            self.assertTrue('id' in data)
            self.assertTrue('purchase' in data)
            self.assertTrue('vendor' in data)
            self.assertTrue('qr_id' in data)
            self.assertTrue('coins' in data)
            self.assertTrue('amount' in data)
            self.assertTrue('balance' in data)
            self.assertTrue('type' in data)
            self.assertTrue('reason' in data)
            self.assertTrue('status' in data)
            self.assertTrue('note' in data)


class EaterRatingTest(PurchaseTestCase):
    """
        Test for creating and retrieving user ratings
    """

    def test_eater_check_review(self):
        """
            Test case for checking review
        :return:
        """
        self.rating_url = reverse('seller.mobile.eater:review_check')
        response = self.client.get(self.rating_url, {
            "purchase": self.purchase.id
        }, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_rating(self):
        """
            Test case for creating a review and retrieving
        :return:
        """
        self.rating_url = reverse('seller.mobile.eater:review')
        response = self.client.post(self.rating_url, {
            "purchase": self.purchase.id,
            "overall_rating": 3,
            "text": "test"
        }, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data.get('success'), True)
        response = self.client.get(self.rating_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('results' in response.data)
        if 'results' in response.data:
            data = response.data['results'][0]
            self.assertTrue("id" in data)
            self.assertTrue("purchase" in data)
            self.assertTrue("average_rating" in data)
            self.assertTrue("overall_rating" in data)

        self.rating_url = reverse('seller.mobile.eater:review_check')
        response = self.client.get(self.rating_url, {
            "purchase": self.purchase.id
        }, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue("id" in response.data)
        self.assertTrue("purchase" in response.data)
        self.assertTrue("overall_rating" in response.data)
        self.assertTrue("text" in response.data)
        self.assertTrue("created_at" in response.data)
        self.assertTrue("updated_at" in response.data)

    def test_vendor_ratings(self):
        self.rating_url = reverse('seller.mobile.eater:review')
        response = self.client.post(self.rating_url, {
            "purchase": self.purchase.id,
            "overall_rating": 3,
            "text": "test"
        }, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data.get('success'), True)
        self.client.force_authenticate(user=self.vendor)
        self.vendor_rating = reverse('seller.mobile.vendor:ratings')
        response = self.client.get(self.vendor_rating)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_vendor_web__ratings(self):
        self.rating_url = reverse('seller.mobile.eater:review')
        response = self.client.post(self.rating_url, {
            "purchase": self.purchase.id,
            "overall_rating": 3,
            "text": "test"
        }, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data.get('success'), True)
        self.client.force_authenticate(user=self.vendor)
        self.vendor_rating = reverse('seller.web.vendor:ratings')
        response = self.client.get(self.vendor_rating)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class VendorWebDashBoardTest(PurchaseTestCase):
    def test_dashboard(self):
        self.client.force_authenticate(user=self.vendor)
        self.dashboard_url = reverse("seller.web.vendor:dashboard")
        response = self.client.get(self.dashboard_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue("id" in response.data)
        self.assertTrue("name" in response.data)
        self.assertTrue("favourite" in response.data)
        self.assertTrue("overall_rating_average" in response.data)

    def test_latest_transactions(self):
        self.client.force_authenticate(user=self.vendor)
        self.dashboard_url = reverse("seller.web.vendor:latest_transactions")
        response = self.client.get(self.dashboard_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue("date" in response.data[0])
        self.assertTrue("transactions" in response.data[0])
        self.assertTrue("sales" in response.data[0])
        self.assertTrue("wait_time" in response.data[0])
        self.assertTrue("check_in" in response.data[0])

    def test_transactions_details(self):
        self.client.force_authenticate(user=self.vendor)
        self.dashboard_url = reverse("seller.web.vendor:transactions_details")
        response = self.client.get(self.dashboard_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue("date" in response.data[0])
        self.assertTrue("transactions" in response.data[0])
        self.assertTrue("sales" in response.data[0])
        self.assertTrue("wait_time" in response.data[0])
        self.assertTrue("check_in" in response.data[0])

    def test_customer_type(self):
        self.client.force_authenticate(user=self.vendor)
        self.dashboard_url = reverse("seller.web.vendor:customer_type")
        response = self.client.get(self.dashboard_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue("new_customer" in response.data)
        self.assertTrue("old_customer" in response.data)

    def test_purchases(self):
        self.client.force_authenticate(user=self.vendor)
        self.dashboard_url = reverse("seller.web.vendor:purchases")
        response = self.client.get(self.dashboard_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('results' in response.data)
        if 'results' in response.data:
            data = response.data['results'][0]
            self.assertTrue("id" in data)
            self.assertTrue("created_at" in data)
            self.assertTrue("rating" in data)
            self.assertTrue("details" in data)
            self.assertTrue("amount" in data)
            self.assertTrue("discount" in data)
