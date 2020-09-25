from rest_framework import status
from rest_framework.test import APITestCase

from seller.authentication.models import Token


class BaseLoginAPITestCase(APITestCase):
    """
        Base API test case for testing the login endpoint.
    """
    url = None
    user = None
    password = None

    def _test_successful_login(self):
        data = {'email': self.user.email, 'password': self.password}
        response = self.client.post(self.url, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue('token' in response.data)
        self.assertTrue('user' in response.data)

    def _test_unsuccessful_login(self):
        incorrect_password = '%s%s' % (self.password, '123')
        data = {'email': self.user.email, 'password': incorrect_password}
        response = self.client.post(self.url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class BaseSignUpAPITestCase(APITestCase):
    """
        Base API test case for testing the sign up endpoint.
    """
    url = None
    user = None
    password = None
    user_factory = None
    business_name = None

    def _test_successful_signup(self):
        data = {
            'email': 'clay.Clay@xyz.com',
            'password': self.password,
            'name': 'Clay Clay',
        }
        if self.business_name:
            data['business_name'] = self.business_name
        response = self.client.post(self.url, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue('token' in response.data)
        self.assertTrue('user' in response.data)

    def _test_conflicting_signup(self):
        self.user_factory(email='clay.Clay@xyz.com')
        data = {
            'email': 'clay.Clay@xyz.com',
            'password': self.password,
            'name': 'Clay Clay',
        }
        if self.business_name:
            data['business_name'] = self.business_name
        response = self.client.post(self.url, data)

        self.assertEqual(response.data['error'], 'User with this email already exists')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def _test_unsuccessful_signup(self):
        self.user_factory(email='clay.clay@xyz.com')
        data = {
            'email': 'clay.clay@xyz.com',
            'password': self.password,
            'name': 'Clay Clay',
        }
        if self.business_name:
            data['business_name'] = self.business_name
        response = self.client.post(self.url, data)

        self.assertTrue('error' in response.data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class BaseLogoutAPITestCase(APITestCase):
    """
        Base API test case for testing the logout endpoint.
    """
    url = None
    user = None

    def _test_logout(self):
        token = Token.objects.get_or_create(user=self.user)
        self.client.force_authenticate(user=self.user, token=token[0])
        self.assertIsNotNone(token)

        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        token = Token.objects.filter(user=self.user).first()
        self.assertIsNone(token)


class BaseDeleteAPITestCase(APITestCase):
    """
        Base API test case for testing the delete endpoint.
    """
    url = None
    user = None

    def _test_delete(self):
        self.client.force_authenticate(user=self.user)
        token = Token.objects.get_or_create(user=self.user)
        self.assertIsNotNone(token)

        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        token = Token.objects.filter(user=self.user).first()
        self.assertIsNone(token)


class BaseChangePasswordAPITestCase(APITestCase):
    """
        Base API test case for testing the change password endpoint.
    """
    url = None
    user = None
    password = None

    def _test_change_password(self):
        self.client.force_authenticate(user=self.user)

        new_password = '%s%s' % (self.password, '123')
        data = {'old_password': self.password, 'password': new_password}
        response = self.client.patch(self.url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def _test_incorrect_change_password(self):
        self.client.force_authenticate(user=self.user)

        incorrect_password = '%s%s' % (self.password, '123')
        data = {'old_password': incorrect_password, 'password': 'Password123!'}
        response = self.client.patch(self.url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def _test_conflicting_change_password(self):
        self.client.force_authenticate(user=self.user)

        data = {'old_password': self.password, 'password': self.password}
        response = self.client.patch(self.url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
