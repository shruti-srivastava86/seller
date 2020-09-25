from django.urls import reverse

from seller.authentication.tests.base_auth_cases import (
    BaseLoginAPITestCase,
    BaseLogoutAPITestCase,
    BaseSignUpAPITestCase,
    BaseChangePasswordAPITestCase
)
from seller.vendor.factory import VendorUserFactory
from seller.notification.factory import EmailTemplateFactory


class LoginAPITestCase(BaseLoginAPITestCase):
    """
        API test case for testing the login endpoint for the Vendor web platform.
    """
    url = reverse('seller.web.vendor:login')
    password = 'Password123!'

    def setUp(self):
        self.user = VendorUserFactory()
        self.user.set_password(self.password)
        self.user.save()

    def test_successful_login(self):
        self._test_unsuccessful_login()

    def test_unsuccessful_login(self):
        self._test_unsuccessful_login()


class SignUpAPITestCase(BaseSignUpAPITestCase):
    """
        API test case for testing the sign up endpoint for the Vendor web platform.
    """
    url = reverse('seller.web.vendor:sign_up')
    password = 'Password123!'
    user_factory = VendorUserFactory
    business_name = 'xyz'

    def setUp(self):
        self.user = VendorUserFactory()
        self.user.set_password(self.password)
        self.user.save()
        EmailTemplateFactory()

    def test_successful_signup(self):
        self._test_successful_signup()

    def test_conflicting_signup(self):
        self._test_conflicting_signup()

    def test_unsuccessful_signup(self):
        self._test_unsuccessful_signup()


class LogoutAPITestCase(BaseLogoutAPITestCase):
    """
        API test case for testing the logout endpoint for the Vendor web platform.
    """
    url = reverse('seller.web.vendor:logout')

    def setUp(self):
        self.user = VendorUserFactory()

    def test_logout(self):
        self._test_logout()


class ChangePasswordAPITestCase(BaseChangePasswordAPITestCase):
    """
        API test case for testing the change password endpoint for the Vendor web platform.
    """
    url = reverse('seller.web.vendor:change_password')
    password = 'Password123!'

    def setUp(self):
        self.user = VendorUserFactory()
        self.user.set_password(self.password)
        self.user.save()

    def test_change_password(self):
        self._test_change_password()

    def test_incorrect_change_password(self):
        self._test_incorrect_change_password()

    def test_conflicting_change_password(self):
        self._test_conflicting_change_password()
