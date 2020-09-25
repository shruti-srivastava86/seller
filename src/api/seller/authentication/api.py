from rest_framework.generics import (
    DestroyAPIView
)
from rest_framework.permissions import AllowAny

from api.generics.generics import (
    DualSerializerCreateAPIView,
    DualSerializerUpdateAPIView,
    CustomCreateAPIView
)
from api.generics.utils import Utils
from seller.authentication.serializers import (
    SignUpSerializer,
    LoginSerializer,
    UserTokenSerializer,
    ChangePasswordSerializer,
    ForgotPasswordSerializer,
    EaterLoginSerializer,
    VendorLoginSerializer
)
from seller.authentication.token import get_token, regenerate_token
from seller.user.models import User
from seller.user.serializers import UserSerializer
from seller.user.utils import send_forgot_password_email
from seller.vendor import enums


class BaseSignUpView(DualSerializerCreateAPIView):
    """
        View for signing up a User to the system.
    """
    permission_classes = [AllowAny]
    request_serializer_class = SignUpSerializer
    response_serializer_class = UserTokenSerializer

    def perform_create(self, serializer):
        """
            Validate and create a new User.
            Return the User with their newly created token.
        """
        user = super(BaseSignUpView, self).perform_create(serializer)
        token = get_token(user)
        return {'user': user, 'token': token.key}


class LoginView(DualSerializerCreateAPIView):
    """
        View for logging a User into the system.
    """
    permission_classes = [AllowAny]
    request_serializer_class = LoginSerializer
    response_serializer_class = UserTokenSerializer

    def perform_create(self, serializer):
        """
            Validate the credentials passed in and retrieve the related User.
            Return the User with their token (this will be created if the User does not have a token).
        """
        user = serializer.validated_data['user']
        token = regenerate_token(user)
        return {'user': user, 'token': token.key}


class EaterLoginView(LoginView):
    request_serializer_class = EaterLoginSerializer


class VendorLoginView(LoginView):
    request_serializer_class = VendorLoginSerializer


class LogoutView(DestroyAPIView):
    """
        View for logging out a User from the system.
    """

    def get_object(self):
        """
            Delete the token currently used
        """
        return self.request.auth


class DeleteView(DestroyAPIView):
    """
        View for logging out a User from the system.
    """

    def get_object(self):
        """
            Delete a User's token.
        """
        user = self.request.user
        user.vendor.status = enums.DELETE
        user.vendor.is_active = False
        user.vendor.save()
        return get_token(user)


class ChangePasswordView(DualSerializerUpdateAPIView):
    """
        View for changing a User's password.
    """
    request_serializer_class = ChangePasswordSerializer
    response_serializer_class = UserSerializer

    def get_object(self):
        return self.request.user


class ForgotPasswordView(CustomCreateAPIView):
    """
        View for changing a User's password.
    """
    request_serializer_class = ForgotPasswordSerializer
    response_serializer_class = UserSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        user = User.filter.with_email(self.request.data.get('email')).first()
        if not user:
            return Utils.error_response_400("No user with this email exists")
        send_forgot_password_email(user)
        return Utils.message_response_200("Successful")
