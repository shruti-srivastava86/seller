from django.contrib.gis.geos import Point
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from seller.dish.factory import (
    CuisineFactory,
    AllergensFactory,
    DishFactory,
    DietaryFactory,

)
from seller.eater.factory import EaterUserFactory
from seller.vendor.factory import (
    VendorUserFactory,
    BusinessFactory,
    ImageFactory,
    MarketFactory
)
from seller.vendor import enums
from seller.user.factory import GeneralSettingsFactory


class VendorListAPITest(APITestCase):
    """
        API test case for testing Vendor list
    """
    lat = 12.97
    lng = 78.23
    url = reverse("seller.mobile.eater:vendors")

    def setUp(self):
        self.eater = EaterUserFactory()
        self.vendor = VendorUserFactory()
        self.dietary = DietaryFactory.create_batch(2)
        self.cuisines = CuisineFactory.create_batch(2)
        self.allergens = AllergensFactory.create_batch(3)
        self.market = MarketFactory.create_batch(3)
        self.image = ImageFactory.create_batch(2)
        self.dish = DishFactory.create(dietary_information=self.dietary)
        self.business = BusinessFactory.create(open=True,
                                               cuisine=self.cuisines,
                                               allergens=self.allergens,
                                               photos=self.image)
        self.vendor.location = Point(self.lng, self.lat, srid=4326)
        self.vendor.save()
        self.business.vendor = self.vendor
        self.business.save()
        self.dish.business = self.business
        self.dish.save()
        self.client.force_authenticate(user=self.eater)
        GeneralSettingsFactory()

    def test_vendor_list(self):
        response = self.client.get(self.url + "?point={},{}".format(self.lng, self.lat))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('results' in response.data)
        if 'results' in response.data:
            data = response.data['results'][0]
            business_data = data.get('business')
            self.assertTrue('name' in data)
            self.assertTrue('business' in data)
            self.assertTrue('distance' in data)
            self.assertTrue('open' in business_data)
            self.assertTrue('dietary_information' in data)
            self.assertTrue('average_rating' in data)
            self.assertTrue('total_ratings' in data)


class VendorDetailsAPITest(VendorListAPITest):
    """
        API test case for testing Vendor details
    """

    def test_vendor_details(self):
        url = reverse("seller.mobile.eater:vendor", kwargs={'pk': self.vendor.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('name' in response.data)
        self.assertTrue('address' in response.data)
        self.assertTrue('dietary_information' in response.data)
        self.assertTrue('business' in response.data)
        if 'business' in response.data:
            business_data = response.data.get('business')
            self.assertTrue('allergens' in business_data)
            self.assertTrue('cuisine' in business_data)
            self.assertTrue('photos' in business_data)
            self.assertTrue('opening_hours' in business_data)
            self.assertTrue('name' in business_data)
            self.assertTrue('description' in business_data)
            self.assertTrue('cash' in business_data)
            self.assertTrue('card' in business_data)
            self.assertTrue('open' in business_data)


class VendorDishAPITest(VendorListAPITest):
    """
        API test case for testing Vendor dishes
    """

    def test_vendor_dishes(self):
        url = reverse("seller.mobile.eater:vendors_dishes", kwargs={'pk': self.vendor.id})
        response = self.client.get(url)
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


class VendorFavouriteAPITest(VendorListAPITest):
    """
        API test case for testing favourite and unfavourite vendor
    """

    def test_favourite_dish(self):
        url = reverse("seller.mobile.eater:vendor_favourite", kwargs={'pk': self.vendor.id})
        response = self.client.patch(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('success'), True)
        response = self.client.get(self.url + "?favourite={}".format('true'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('results' in response.data)
        if 'results' in response.data:
            data = response.data['results'][0]
            business_data = data.get('business')
            self.assertTrue('name' in data)
            self.assertTrue('business' in data)
            self.assertTrue('distance' in data)
            self.assertTrue('open' in business_data)
            self.assertTrue('dietary_information' in data)
            self.assertTrue('average_rating' in data)
            self.assertTrue('total_ratings' in data)

    def test_unfavourite_vendor(self):
        url = reverse("seller.mobile.eater:vendors_unfavourite", kwargs={'pk': self.vendor.id})
        response = self.client.patch(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('success'), True)


class VendorProfileAPITest(APITestCase):
    '''
        Test cases for test
    '''
    lat = 12.97
    lng = 78.23
    url = reverse("seller.mobile.vendor:profile")

    def setUp(self):
        self.vendor = VendorUserFactory()
        self.dietary = DietaryFactory.create_batch(2)
        self.cuisines = CuisineFactory.create_batch(2)
        self.allergens = AllergensFactory.create_batch(3)
        self.image = ImageFactory.create_batch(2)
        self.market = MarketFactory.create_batch(3)
        self.dish = DishFactory.create(dietary_information=self.dietary)
        self.business = BusinessFactory.create(open=True,
                                               cuisine=self.cuisines,
                                               allergens=self.allergens,
                                               photos=self.image)
        self.vendor.location = Point(self.lng, self.lat, srid=4326)
        self.vendor.save()
        self.business.vendor = self.vendor
        self.business.save()
        self.dish.business = self.business
        self.dish.save()
        self.client.force_authenticate(user=self.vendor)

    def test_vendor_profile(self):
        """
            Test case for profile mobile
        :return:
        """
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data
        self.assertTrue('name' in data)
        self.assertTrue('business' in data)
        self.assertTrue('distance' in data)
        business_data = data.get('business')
        self.assertTrue('open' in business_data)
        self.assertTrue('dietary_information' in data)
        self.assertTrue('average_rating' in data)
        self.assertTrue('total_ratings' in data)
        self.assertTrue('uuid' in data)

    def test_vendor_profile_web(self):
        """
            Test case for profile web
        :return:
        """
        self.url = reverse("seller.web.vendor:profile")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data
        self.assertTrue("id" in data)
        self.assertTrue('name' in data)
        self.assertTrue('photos' in data)
        self.assertTrue('check_out' in data)
        self.assertTrue('cash' in data)
        self.assertTrue('allergens' in data)
        self.assertTrue('cuisine' in data)
        self.assertTrue('opening_hours' in data)
        self.assertTrue('home_market' in data)
        self.assertTrue('description' in data)
        self.assertTrue('biography' in data)
        self.assertTrue('tagline' in data)

    def test_update_vendor_profile(self):
        response = self.client.patch(self.url, {"business": {"offer_active": True, "offer": "20% discount on all items",
                                                             "tagline": "this is the best you can find"}},
                                     format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('success'), True)
        response = self.client.get(self.url)
        data = response.data
        business_data = data.get('business')
        self.assertEqual(business_data.get('offer_active'), True)
        self.assertEqual(business_data.get('offer'), '20% discount on all items')
        self.assertEqual(business_data.get('tagline'), 'this is the best you can find')

    def test_vendor_update_profile_web(self):
        """
            Test case for profile web
        :return:
        """
        self.url = reverse("seller.web.vendor:update_profile")
        self.name = "def"
        self.email = "def+vendor88@xyz.com"
        response = self.client.patch(self.url, {
            "name": self.name,
            "email": self.email
        }, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data
        self.assertTrue('name' in data)
        self.assertTrue('business' in data)
        business_data = data.get('business')
        self.assertTrue('id' in business_data)
        self.assertTrue('uuid' in business_data)
        self.assertTrue('email' in data)
        self.assertTrue('address' in data)
        self.assertTrue('location' in data)
        self.assertTrue('status' in data)
        self.assertEqual(data.get('name'), self.name)
        self.assertEqual(data.get('email'), self.email)

    def test_vendor_update_business_web(self):
        """
            Test case for business profile web
        :return:
        """
        self.url = reverse("seller.web.vendor:update_business")
        self.name = "katy",
        self.description = "ajkvbkfbhisdvhidhvs",
        self.biography = "jvbkjdvbiljlojLCJNOIDJOIHVLNVDLLNB",
        self.tagline = "DISHLVDst",
        response = self.client.patch(self.url, {
            "name": "katy",
            "description": "ajkvbkfbhisdvhidhvs",
            "biography": "jvbkjdvbiljlojLCJNOIDJ OIHVLNVDL LNB",
            "tagline": "DISHLVD st",
            "cuisine": [self.cuisines[0].id],
            "social_links": {"facebook": "facebbok", "twitter": "twittwer", "insta": "insta"}
        }, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data

        self.assertTrue('name' in data)
        self.assertTrue('vendor' in data)
        vendor_data = data.get('vendor')
        self.assertTrue('id' in vendor_data)
        self.assertTrue('uuid' in vendor_data)
        self.assertTrue('email' in vendor_data)
        self.assertTrue('address' in vendor_data)
        self.assertTrue("id" in data)
        self.assertTrue('name' in data)
        self.assertTrue('photos' in data)
        self.assertTrue('check_out' in data)
        self.assertTrue('cash' in data)
        self.assertTrue('allergens' in data)
        self.assertTrue('cuisine' in data)
        self.assertTrue('opening_hours' in data)
        self.assertTrue('home_market' in data)
        self.assertTrue('description' in data)
        self.assertTrue('biography' in data)
        self.assertTrue('tagline' in data)

    def test_vendor_update_trading_web(self):
        """
            Test case for profile web
        :return:
        """
        self.url = reverse("seller.web.vendor:update_trading")
        self.cash = True
        self.card = True
        response = self.client.patch(self.url, {

            "cash": True,
            "card": True,
            "opening_hours": [
                {
                    "id": 8,
                    "weekday": 1,
                    "from_hour": "05:30:00",
                    "to_hour": "06:30:00",
                    "open": True
                },
                {
                    "id": 9,
                    "weekday": 2,
                    "from_hour": "00:00:00",
                    "to_hour": "00:00:00",
                    "open": False
                },
                {
                    "id": 10,
                    "weekday": 3,
                    "from_hour": "05:30:00",
                    "to_hour": "06:30:00",
                    "open": True
                },
                {
                    "id": 11,
                    "weekday": 4,
                    "from_hour": "05:30:00",
                    "to_hour": "06:30:00",
                    "open": True
                },
                {
                    "id": 12,
                    "weekday": 5,
                    "from_hour": "05:30:00",
                    "to_hour": "06:30:00",
                    "open": True
                },
                {
                    "id": 13,
                    "weekday": 6,
                    "from_hour": "05:30:00",
                    "to_hour": "06:30:00",
                    "open": True
                },
                {
                    "id": 14,
                    "weekday": 0,
                    "from_hour": "01:30:00",
                    "to_hour": "06:30:00",
                    "open": True
                }
            ]
        }, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data
        self.assertTrue('name' in data)
        self.assertTrue('vendor' in data)
        vendor_data = data.get('vendor')
        self.assertTrue('id' in vendor_data)
        self.assertTrue('uuid' in vendor_data)
        self.assertTrue('email' in vendor_data)
        self.assertTrue('address' in vendor_data)
        self.assertTrue("id" in data)
        self.assertTrue('name' in data)
        self.assertTrue('photos' in data)
        self.assertTrue('check_out' in data)
        self.assertTrue('cash' in data)
        self.assertTrue('allergens' in data)
        self.assertTrue('cuisine' in data)
        self.assertTrue('opening_hours' in data)
        self.assertTrue('home_market' in data)
        self.assertTrue('description' in data)
        self.assertTrue('biography' in data)
        self.assertTrue('tagline' in data)

    def test_vendor_update_allergens_web(self):
        """
            Test case for editibg allegens web
        :return:
        """
        self.url = reverse("seller.web.vendor:update_allergens")
        self.name = "katy",
        self.description = "ajkvbkfbhisdvhidhvs",
        self.biography = "jvbkjdvbiljlojLCJNOIDJOIHVLNVDLLNB",
        self.tagline = "DISHLVDst",
        response = self.client.patch(self.url, {
            "allergens": [self.allergens[0].id]
        }, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data

        self.assertTrue('name' in data)
        self.assertTrue('vendor' in data)
        vendor_data = data.get('vendor')
        self.assertTrue('id' in vendor_data)
        self.assertTrue('uuid' in vendor_data)
        self.assertTrue('email' in vendor_data)
        self.assertTrue('address' in vendor_data)
        self.assertTrue("id" in data)
        self.assertTrue('name' in data)
        self.assertTrue('photos' in data)
        self.assertTrue('check_out' in data)
        self.assertTrue('cash' in data)
        self.assertTrue('allergens' in data)
        self.assertTrue('cuisine' in data)
        self.assertTrue('opening_hours' in data)
        self.assertTrue('home_market' in data)
        self.assertTrue('description' in data)
        self.assertTrue('biography' in data)
        self.assertTrue('tagline' in data)

    def test_vendor_update_ingredients_web(self):
        """
            Test case for editing ingredients web
        :return:
        """
        self.url = reverse("seller.web.vendor:update_ingredients")
        self.name = "katy",
        self.description = "ajkvbkfbhisdvhidhvs",
        self.biography = "jvbkjdvbiljlojLCJNOIDJOIHVLNVDLLNB",
        self.tagline = "DISHLVDst",
        response = self.client.patch(self.url, {
            "ingredients": ["uvw1"]
        }, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data

        self.assertTrue('name' in data)
        self.assertTrue('vendor' in data)
        vendor_data = data.get('vendor')
        self.assertTrue('id' in vendor_data)
        self.assertTrue('uuid' in vendor_data)
        self.assertTrue('email' in vendor_data)
        self.assertTrue('address' in vendor_data)
        self.assertTrue("id" in data)
        self.assertTrue('name' in data)
        self.assertTrue('photos' in data)
        self.assertTrue('check_out' in data)
        self.assertTrue('cash' in data)
        self.assertTrue('allergens' in data)
        self.assertTrue('cuisine' in data)
        self.assertTrue('opening_hours' in data)
        self.assertTrue('home_market' in data)
        self.assertTrue('description' in data)
        self.assertTrue('biography' in data)
        self.assertTrue('tagline' in data)

    def test_vendor_update_photos_web(self):
        """
            Test case for editing photos web
        :return:
        """
        self.url = reverse("seller.web.vendor:update_photos")
        self.name = "katy",
        self.description = "ajkvbkfbhisdvhidhvs",
        self.biography = "jvbkjdvbiljlojLCJNOIDJOIHVLNVDLLNB",
        self.tagline = "DISHLVDst",
        response = self.client.patch(self.url, {
            "photos": [
                {

                    "image": "https://4b5a-9011-f705c310f854.jpg",
                    "hero": True
                },
                {

                    "image": "https://4b5a-9011-f705c310f854.jpg",
                    "hero": False
                },
                {

                    "image": "https://4b5a-9011-f705c310f854.jpg",
                    "hero": False
                },

            ]
        }, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data

        self.assertTrue('name' in data)
        self.assertTrue('vendor' in data)
        vendor_data = data.get('vendor')
        self.assertTrue('id' in vendor_data)
        self.assertTrue('uuid' in vendor_data)
        self.assertTrue('email' in vendor_data)
        self.assertTrue('address' in vendor_data)
        self.assertTrue("id" in data)
        self.assertTrue('name' in data)
        self.assertTrue('photos' in data)
        self.assertTrue('check_out' in data)
        self.assertTrue('cash' in data)
        self.assertTrue('allergens' in data)
        self.assertTrue('cuisine' in data)
        self.assertTrue('opening_hours' in data)
        self.assertTrue('home_market' in data)
        self.assertTrue('description' in data)
        self.assertTrue('biography' in data)
        self.assertTrue('tagline' in data)

    def test_vendor_update_location_web(self):
        """
            Test case for editing location web
        :return:
        """
        self.url = reverse("seller.web.vendor:update_location")
        self.name = "katy",
        self.description = "ajkvbkfbhisdvhidhvs",
        self.biography = "jvbkjdvbiljlojLCJNOIDJOIHVLNVDLLNB",
        self.tagline = "DISHLVDst",
        response = self.client.patch(self.url, {
            "home_market": [self.market[0].id]
        }, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data

        self.assertTrue('name' in data)
        self.assertTrue('vendor' in data)
        vendor_data = data.get('vendor')
        self.assertTrue('id' in vendor_data)
        self.assertTrue('uuid' in vendor_data)
        self.assertTrue('email' in vendor_data)
        self.assertTrue('address' in vendor_data)
        self.assertTrue("id" in data)
        self.assertTrue('name' in data)
        self.assertTrue('photos' in data)
        self.assertTrue('check_out' in data)
        self.assertTrue('cash' in data)
        self.assertTrue('allergens' in data)
        self.assertTrue('cuisine' in data)
        self.assertTrue('opening_hours' in data)
        self.assertTrue('home_market' in data)
        self.assertTrue('description' in data)
        self.assertTrue('biography' in data)
        self.assertTrue('tagline' in data)

    def test_vendor_update_address_web(self):
        """
            Test case for editing address web
        :return:
        """
        self.url = reverse("seller.web.vendor:update_address")
        response = self.client.patch(self.url, {
            "address_line_1": "tescsa vewlihdilbst",
            "address_line_2": "teddlwj;ofepjskndlknst2",
            "city": "hyde;sdojfopjffjdb",
            "county": "countcpepajofodkcsry",
            "postcode": "ne1apojfsamclsa2la"

        }, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data

        self.assertTrue('name' in data)
        self.assertTrue('business' in data)
        business_data = data.get('business')
        self.assertTrue('id' in business_data)
        self.assertTrue('uuid' in business_data)
        self.assertTrue('email' in data)
        self.assertTrue('address' in data)
        self.assertTrue('location' in data)
        self.assertTrue('status' in data)


class VendorCheckinAPITest(VendorProfileAPITest):
    def test_checkin_vendor(self):
        url = reverse("seller.mobile.vendor:checkin")
        response = self.client.patch(url, {"lng": self.lng, "lat": self.lat, "checkout_time": "17:30"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('success'), True)
        checkout_url = reverse("seller.mobile.vendor:checkout")
        response = self.client.get(checkout_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class VendorCheckoutAPITest(VendorProfileAPITest):
    def test_checkin_vendor(self):
        url = reverse("seller.mobile.vendor:checkout")
        response = self.client.patch(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('success'), True)


class VendorActiveDishAPITest(VendorListAPITest):
    def test_vendor_active_dishes(self):
        """
            Test case for fetching active dishes mobile
        :return:
        """
        self.client.force_authenticate(self.vendor)
        url = reverse("seller.mobile.vendor:dishes")
        response = self.client.get(url + "?active=true")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('results' in response.data)
        if 'results' in response.data:
            data = response.data['results'][0]
            self.assertEqual(data.get('active'), True)
            self.assertTrue('name' in data)
            self.assertTrue('price' in data)
            self.assertTrue('temporary_price' in data)
            self.assertTrue(('dietary_information' in data))

    def test_vendor_active_dishes_web(self):
        """
            Test case for fetching active dishes web
        :return:
        """
        self.client.force_authenticate(self.vendor)
        url = reverse("seller.web.vendor:dishes")
        response = self.client.get(url + "?active=true")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('results' in response.data)
        if 'results' in response.data:
            data = response.data['results'][0]
            self.assertEqual(data.get('active'), True)
            self.assertTrue('name' in data)
            self.assertTrue('price' in data)
            self.assertTrue('temporary_price' in data)
            self.assertTrue(('dietary_information' in data))

    def test_vendor_edit_dish(self):
        '''
            Editing a dish and making it inactive
        :return:
        '''
        self.client.force_authenticate(self.vendor)
        name = "dish_edit"
        price = 10
        temporary_price = 10
        active = 0
        description = "edit description"
        special = 0
        url = reverse("seller.mobile.vendor:dish", kwargs={"pk": self.dish.id})
        response = self.client.patch(url, {"name": name,
                                           "price": price,
                                           "temporary_price": temporary_price,
                                           "active": active,
                                           "description": description,
                                           "special": special
                                           })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('name'), name)
        self.assertEqual(response.data.get('price'), "10.00")
        self.assertEqual(response.data.get('active'), False)
        self.assertEqual(response.data.get('description'), description)
        # tests for getting inactive dishes
        url = reverse("seller.mobile.vendor:dishes")
        response = self.client.get(url + "?active=false")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('results' in response.data)
        if 'results' in response.data:
            data = response.data['results'][0]
            self.assertEqual(data.get('active'), False)
            self.assertTrue('name' in data)
            self.assertTrue('price' in data)
            self.assertTrue('temporary_price' in data)
            self.assertTrue(('dietary_information' in data))

    def test_vendor_dish_details(self):
        self.client.force_authenticate(self.vendor)
        url = reverse("seller.mobile.vendor:dish", kwargs={"pk": self.dish.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data
        self.assertTrue('name' in data)
        self.assertTrue('price' in data)
        self.assertTrue('temporary_price' in data)
        self.assertTrue(('dietary_information' in data))
        self.assertTrue('active' in data)

    def test_vendor_edit_dish_web(self):
        '''
            Editing a dish and making it inactive web
        :return:
        '''
        self.client.force_authenticate(self.vendor)
        name = "dish_edit"
        price = 10
        temporary_price = 10
        active = 0
        description = "edit description"
        special = 0
        url = reverse("seller.web.vendor:dish", kwargs={"pk": self.dish.id})
        response = self.client.patch(url, {"name": name,
                                           "price": price,
                                           "temporary_price": temporary_price,
                                           "active": active,
                                           "description": description,
                                           "special": special
                                           })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('name'), name)
        self.assertEqual(response.data.get('price'), "10.00")
        self.assertEqual(response.data.get('active'), False)
        self.assertEqual(response.data.get('description'), description)
        # tests for getting inactive dishes
        url = reverse("seller.mobile.vendor:dishes")
        response = self.client.get(url + "?active=false")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('results' in response.data)
        if 'results' in response.data:
            data = response.data['results'][0]
            self.assertEqual(data.get('active'), False)
            self.assertTrue('name' in data)
            self.assertTrue('price' in data)
            self.assertTrue('temporary_price' in data)
            self.assertTrue(('dietary_information' in data))

    def test_vendor_dish_details_web(self):
        """
            Test for vendor dish details web
        :return:
        """
        self.client.force_authenticate(self.vendor)
        url = reverse("seller.web.vendor:dish", kwargs={"pk": self.dish.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data
        self.assertTrue('name' in data)
        self.assertTrue('price' in data)
        self.assertTrue('temporary_price' in data)
        self.assertTrue(('dietary_information' in data))
        self.assertTrue('active' in data)

    def test_vendor_all_dishes_web(self):
        """
            Test for vendor dish details web
        :return:
        """
        self.client.force_authenticate(self.vendor)
        url = reverse("seller.web.vendor:all_dishes")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data[0]
        self.assertTrue('name' in data)
        self.assertTrue("id" in data)


class VendorMarketApiTest(VendorListAPITest):

    def test_vendor_markets(self):
        self.url = reverse("seller.web.vendor:markets")
        self.client.force_authenticate(self.vendor)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data[0]
        self.assertTrue('id' in data)
        self.assertTrue('name' in data)


class VendorWebOnboardingApiTest(VendorListAPITest):

    def test_vendor_web_onboarding_stage_1(self):
        self.vendor.status = enums.INPROGRESS
        self.vendor.save()
        self.url = reverse("seller.web.vendor:onboarding")
        self.client.force_authenticate(self.vendor)
        response = self.client.patch(self.url, {
            "name": "business 18",
            "description": "ajkvbkfbhisdvhidhvs",
            "biography": "jvbkjdvbiljlojLCJNOIDJ OIHVLNVDL LNB",
            "tagline": "DISHLVD st",
            "cuisine": [self.cuisines[0].id],
            "social_links": ["test", "test2"],
            "onboarding_stage": 1
        }, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data
        self.assertTrue('name' in data)
        self.assertTrue('business' in data)
        business_data = data.get('business')
        self.assertTrue('id' in business_data)
        self.assertTrue('uuid' in business_data)
        self.assertTrue('email' in data)
        self.assertTrue('address' in data)
        self.assertTrue('location' in data)
        self.assertTrue('status' in data)

    def test_vendor_web_onboarding_stage_2(self):
        self.vendor.status = enums.INPROGRESS
        self.vendor.save()
        self.url = reverse("seller.web.vendor:onboarding")
        self.client.force_authenticate(self.vendor)
        response = self.client.patch(self.url, {

            "cash": True,
            "card": True,
            "opening_hours": [
                {
                    "id": 8,
                    "weekday": 1,
                    "from_hour": "05:30:00",
                    "to_hour": "06:30:00",
                    "open": True
                },
                {
                    "id": 9,
                    "weekday": 2,
                    "from_hour": "00:00:00",
                    "to_hour": "00:00:00",
                    "open": False
                },
                {
                    "id": 10,
                    "weekday": 3,
                    "from_hour": "05:30:00",
                    "to_hour": "06:30:00",
                    "open": True
                },
                {
                    "id": 11,
                    "weekday": 4,
                    "from_hour": "05:30:00",
                    "to_hour": "06:30:00",
                    "open": True
                },
                {
                    "id": 12,
                    "weekday": 5,
                    "from_hour": "05:30:00",
                    "to_hour": "06:30:00",
                    "open": True
                },
                {
                    "id": 13,
                    "weekday": 6,
                    "from_hour": "05:30:00",
                    "to_hour": "06:30:00",
                    "open": True
                },
                {
                    "id": 14,
                    "weekday": 0,
                    "from_hour": "01:30:00",
                    "to_hour": "06:30:00",
                    "open": True
                }
            ],
            "onboarding_stage": 2
        }, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data
        self.assertTrue('name' in data)
        self.assertTrue('business' in data)
        business_data = data.get('business')
        self.assertTrue('id' in business_data)
        self.assertTrue('uuid' in business_data)
        self.assertTrue('email' in data)
        self.assertTrue('address' in data)
        self.assertTrue('location' in data)
        self.assertTrue('status' in data)

    def test_vendor_web_onboarding_stage_3(self):
        self.vendor.status = enums.INPROGRESS
        self.vendor.save()
        self.url = reverse("seller.web.vendor:onboarding")
        self.client.force_authenticate(self.vendor)
        response = self.client.patch(self.url, {
            "home_market": [self.market[0].id],
            "onboarding_stage": 3
        }, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data
        self.assertTrue('name' in data)
        self.assertTrue('business' in data)
        business_data = data.get('business')
        self.assertTrue('id' in business_data)
        self.assertTrue('uuid' in business_data)
        self.assertTrue('email' in data)
        self.assertTrue('address' in data)
        self.assertTrue('location' in data)
        self.assertTrue('status' in data)

    def test_vendor_web_onboarding_stage_4(self):
        self.vendor.status = enums.INPROGRESS
        self.vendor.save()
        self.url = reverse("seller.web.vendor:onboarding")
        self.client.force_authenticate(self.vendor)
        response = self.client.patch(self.url, {
            "photos": [
                {

                    "image": "https:/6-4b5a-9011-f705c310f854.jpg",
                    "hero": True
                },
                {

                    "image": "https:/6-4b5a-9011-f705c310f854.jpg",
                    "hero": False
                },
            ],
            "onboarding_stage": 4
        }, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data
        self.assertTrue('name' in data)
        self.assertTrue('business' in data)
        business_data = data.get('business')
        self.assertTrue('id' in business_data)
        self.assertTrue('uuid' in business_data)
        self.assertTrue('email' in data)
        self.assertTrue('address' in data)
        self.assertTrue('location' in data)
        self.assertTrue('status' in data)

    def test_vendor_web_onboarding_stage_5(self):
        self.vendor.status = enums.INPROGRESS
        self.vendor.save()
        self.url = reverse("seller.web.vendor:onboarding")
        self.client.force_authenticate(self.vendor)
        response = self.client.patch(self.url, {
            "ingredients": ["uvw1"],
            "onboarding_stage": 5
        }, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data
        self.assertTrue('name' in data)
        self.assertTrue('business' in data)
        business_data = data.get('business')
        self.assertTrue('id' in business_data)
        self.assertTrue('uuid' in business_data)
        self.assertTrue('email' in data)
        self.assertTrue('address' in data)
        self.assertTrue('location' in data)
        self.assertTrue('status' in data)

    def test_vendor_web_onboarding_stage_6(self):
        self.vendor.status = enums.INPROGRESS
        self.vendor.save()
        self.url = reverse("seller.web.vendor:onboarding")
        self.client.force_authenticate(self.vendor)
        response = self.client.patch(self.url, {
            "allergens": [self.allergens[0].id],
            "onboarding_stage": 6
        }, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data
        self.assertTrue('name' in data)
        self.assertTrue('business' in data)
        business_data = data.get('business')
        self.assertTrue('id' in business_data)
        self.assertTrue('uuid' in business_data)
        self.assertTrue('email' in data)
        self.assertTrue('address' in data)
        self.assertTrue('location' in data)
        self.assertTrue('status' in data)
