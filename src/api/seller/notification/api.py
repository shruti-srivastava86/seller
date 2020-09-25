from api.generics.generics import (
    DualSerializerCreateAPIView,
    SuccessResponseSerializer,
    CustomRetrieveUpdateAPIView
)
from api.generics.permissions import IsAVendor, IsAnEater
from seller.notification.models import VendorPreference, EaterPreference
from seller.notification.serializers import (
    DeviceRegistrationSerializer,
    DeviceUnRegistrationSerializer,
    VendorPreferenceSerializer,
    TestNotificationSerializer,
    EaterPreferenceSerializer)


class DeviceRegister(DualSerializerCreateAPIView):
    """
        View for registering device token
    """
    request_serializer_class = DeviceRegistrationSerializer
    response_serializer_class = SuccessResponseSerializer


class DeviceUnregister(DeviceRegister):
    """
        View for un registering device token
    """
    request_serializer_class = DeviceUnRegistrationSerializer


class VendorPreferences(CustomRetrieveUpdateAPIView):
    """
        View for retrieving and updating vendor push notification settings
    """
    serializer_class = VendorPreferenceSerializer
    permission_classes = [IsAVendor]

    def get_object(self):
        notification_preference = self.request.user.vendor.notification_preference
        if not notification_preference:
            notification_preference = VendorPreference.objects.create()
            self.request.user.vendor.notification_preference = notification_preference
            self.request.user.vendor.save()
        return notification_preference


class EaterPreferences(CustomRetrieveUpdateAPIView):
    """
        View for retrieving and updating eater push notification settings
    """
    serializer_class = EaterPreferenceSerializer
    permission_classes = [IsAnEater]

    def get_object(self):
        notification_preference = self.request.user.eater.notification_preference
        if not notification_preference:
            notification_preference = EaterPreference.objects.create()
            self.request.user.eater.notification_preference = notification_preference
            self.request.user.eater.save()
        return notification_preference


class TestNotification(DualSerializerCreateAPIView):
    """
        View to send a test notification to user's devices
    """
    request_serializer_class = TestNotificationSerializer
    response_serializer_class = SuccessResponseSerializer
