from rest_framework import status, viewsets
from rest_framework.generics import RetrieveDestroyAPIView, CreateAPIView, get_object_or_404
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.settings import api_settings
from rest_framework.decorators import detail_route
from rest_framework.views import APIView

from api.generics.generics import (
    DualSerializerUpdateAPIView,
    CustomListAPIView,
    DualSerializerCreateAPIView,
    RetrieveAPIView,
    SuccessResponseSerializer,
    CustomCreateAPIView)
from api.generics.permissions import IsAnEater
from api.generics.utils import Utils
from seller.authentication.api import BaseSignUpView
from seller.authentication.serializers import UserTokenSerializer
from seller.authentication.token import regenerate_token
from seller.eater import enums
from seller.eater.serializers import (
    EaterSignUpSerializer,
    EaterSerializer,
    EaterUpdateSerializer,
    EaterTransactionCreateSerializer,
    GeneralSettingsSerializer,
    ReportVendorSerializer,
    ReportSerializer,
    SupportEaterSerializer,
    EaterNotificationSerializer, FacebookSignupSerializer, EaterReviewCheckSerializer)
from seller.notification.filter import ReviewFilter
from seller.notification.models import Notifications
from seller.review.models import Rating
from seller.user import enums as user_enums
from seller.user.models import ReportVendorList, User, Transaction
from seller.user.serializers import UserTransactionSerializer
from seller.user.validators import Validations


class EaterSignUpView(BaseSignUpView):
    """
        Overrides the BaseSignUpView to Sign up a User as an Eater.
    """
    request_serializer_class = EaterSignUpSerializer


class EaterRetrieveDelete(RetrieveDestroyAPIView):
    """
        View or Deleting an Eater from the system.
    """
    serializer_class = EaterSerializer
    permission_classes = [IsAnEater]

    def get_object(self):
        """
            Retrieve an Eater's account.
        """
        return self.request.user.eater


class EaterProfileView(EaterRetrieveDelete, DualSerializerUpdateAPIView):
    """
        View for eater profile page.
    """
    request_serializer_class = EaterUpdateSerializer
    response_serializer_class = EaterRetrieveDelete.serializer_class
    permission_classes = [IsAnEater]


class EaterTransactionListCreateView(CustomListAPIView, DualSerializerCreateAPIView):
    """
        View to list and create transactions for eater.
    """
    serializer_class = UserTransactionSerializer
    request_serializer_class = EaterTransactionCreateSerializer
    response_serializer_class = EaterTransactionCreateSerializer
    filter_backends = api_settings.DEFAULT_FILTER_BACKENDS
    permission_classes = [IsAnEater]
    ordering = ['-created_at']

    def get_serializer_context(self):
        context = super(EaterTransactionListCreateView, self).get_serializer_context()
        context["credit_transactions"] = Transaction.objects.filter(
            type=user_enums.CREDIT
        )
        return context

    def get_queryset(self):
        return self.request.user.transactions.all()


class EaterGeneralSettingsView(RetrieveAPIView):
    """
        View for getting general setting for eater
    """
    serializer_class = GeneralSettingsSerializer

    def get_object(self):
        return Validations.validate_general_settings()


class ReportListView(CustomListAPIView):
    serializer_class = ReportSerializer


class ReportVendorView(CustomListAPIView, DualSerializerCreateAPIView):
    serializer_class = ReportSerializer
    request_serializer_class = ReportVendorSerializer
    response_serializer_class = SuccessResponseSerializer
    permission_classes = [IsAnEater]

    def get_queryset(self):
        return ReportVendorList.objects.all()


class SupportEaterView(DualSerializerCreateAPIView):
    serializer_class = SupportEaterSerializer
    request_serializer_class = SupportEaterSerializer
    response_serializer_class = SuccessResponseSerializer
    permission_classes = [IsAnEater]


class EaterNotificationsView(viewsets.ReadOnlyModelViewSet):
    serializer_class = EaterNotificationSerializer
    filter_backends = api_settings.DEFAULT_FILTER_BACKENDS + [
        ReviewFilter
    ]
    ordering = ['-created_at']

    def get_queryset(self):
        return self.request.user.notifications.all()

    @detail_route(methods=['post', ])
    def read(self, request, pk):
        obj = self.get_object()
        obj.read = True
        obj.save()
        return Response(status=status.HTTP_200_OK)


class FacebookSignup(CustomCreateAPIView):
    """
    A user can signup using Facebook
    """

    permission_classes = [AllowAny]
    serializer_class = FacebookSignupSerializer

    def create(self, request, *args, **kwargs):
        if Validations.verify_facebook_signup(self.request.data.get('facebook_token'),
                                              self.request.data.get('facebook_id')):
            serializer = self.serializer_class(data=self.request.data)
            serializer.is_valid(raise_exception=True)
            user = serializer.save()
            token = regenerate_token(user)
            return Response(UserTokenSerializer({"user": user, "token": token}).data, status=status.HTTP_200_OK)
        return Utils.error_response_400("Invalid facebook account")


class FacebookLogin(CreateAPIView):
    """
    A user can login using Facebook
    """

    permission_classes = [AllowAny]
    serializer_class = FacebookSignupSerializer

    def create(self, request, *args, **kwargs):
        if Validations.verify_facebook_signup(self.request.data.get('facebook_token'),
                                              self.request.data.get('facebook_id')):
            try:

                eater = User.objects.get(email=self.request.data.get('email'))
                if not eater.user_type == user_enums.EATER:
                    return Response({"error": "Email already exists"}, status=status.HTTP_400_BAD_REQUEST)

            except Exception as e:
                serializer = self.serializer_class(data=self.request.data)
                serializer.is_valid(raise_exception=True)
                eater = serializer.save()

            if eater.eater.status == enums.SUSPEND:
                return Response({"error": "Unauthorised"}, status=status.HTTP_403_FORBIDDEN)
            token = regenerate_token(eater)
            return Response(UserTokenSerializer({"user": eater, "token": token}).data, status=status.HTTP_200_OK)
        return Utils.error_response_400("Invalid facebook account")


class UnreadMessages(APIView):

    def get(self, request, *args, **kwargs):
        message_count = Notifications.objects.for_user(self.request.user).with_unread().count()
        return Response({'unread': message_count})


class EaterReviewCheckApi(RetrieveAPIView):
    serializer_class = EaterReviewCheckSerializer

    def get_object(self):
        return get_object_or_404(Rating, purchase=self.request.GET.get('purchase'))
