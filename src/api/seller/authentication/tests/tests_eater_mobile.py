from django.urls import reverse

from seller.authentication.tests.base_auth_cases import (
    BaseLoginAPITestCase,
    BaseLogoutAPITestCase,
    BaseSignUpAPITestCase,
    BaseChangePasswordAPITestCase,
    BaseDeleteAPITestCase
)
from seller.eater.factory import EaterUserFactory


class LoginAPITestCase(BaseLoginAPITestCase):
    """
        API test case for testing the login endpoint for the Eater mobile platform.
    """
    url = reverse('seller.mobile.eater:login')
    password = 'Password123!'

    def setUp(self):
        self.user = EaterUserFactory()
        self.user.set_password(self.password)
        self.user.save()

    def test_successful_login(self):
        self._test_unsuccessful_login()

    def test_unsuccessful_login(self):
        self._test_unsuccessful_login()


class SignUpAPITestCase(BaseSignUpAPITestCase):
    """
        API test case for testing the sign up endpoint for the Eater mobile platform.
    """
    url = reverse('seller.mobile.eater:sign_up')
    password = 'Password123!'
    user_factory = EaterUserFactory

    def setUp(self):
        self.user = EaterUserFactory()
        self.user.set_password(self.password)
        self.user.save()

    def test_successful_signup(self):
        self._test_successful_signup()

    def test_conflicting_signup(self):
        self._test_conflicting_signup()


class LogoutAPITestCase(BaseLogoutAPITestCase):
    """
        API test case for testing the logout endpoint for the Eater mobile platform.
    """
    url = reverse('seller.mobile.eater:logout')

    def setUp(self):
        self.user = EaterUserFactory()

    def test_logout(self):
        self._test_logout()


class DeleteAPITestCase(BaseDeleteAPITestCase):
    """
        API test case for testing the logout endpoint for the Eater mobile platform.
    """
    url = reverse('seller.mobile.eater:retrieve_delete')

    def setUp(self):
        self.user = EaterUserFactory()

    def test_delete(self):
        self._test_delete()


class ChangePasswordAPITestCase(BaseChangePasswordAPITestCase):
    """
        API test case for testing the change password endpoint for the Eater mobile platform.
    """
    url = reverse('seller.mobile.eater:change_password')
    password = 'Password123!'

    def setUp(self):
        self.user = EaterUserFactory()
        self.user.set_password(self.password)
        self.user.save()

    def test_change_password(self):
        self._test_change_password()

    def test_incorrect_change_password(self):
        self._test_incorrect_change_password()

    def test_conflicting_change_password(self):
        self._test_conflicting_change_password()
