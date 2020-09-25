from django.conf import settings
from rest_framework import serializers

from api.generics.generics import CustomSerializer
from seller.notification.constants import CHECKIN_CHECKOUT
from seller.notification.models import VendorPreference, EaterPreference
from seller.notification.utils import register_device, unregister_device, send_message_to_devices
from seller.user import enums


class DeviceRegistrationSerializer(CustomSerializer):
    token = serializers.CharField(required=True)
    uuid = serializers.CharField(required=True)
    type = serializers.CharField(required=True)

    def create(self, validated_data):
        try:
            user = self.context['request'].user
            register_device(user,
                            validated_data['token'],
                            validated_data['uuid'],
                            validated_data['type'])
            if user.user_type == enums.VENDOR and \
                    not user.vendor.notification_preference:
                user.vendor.notification_preference = VendorPreference.objects.create()
                user.vendor.save()
            return {"success": True}
        except Exception as e:
            return {"error": str(e)}


class DeviceUnRegistrationSerializer(CustomSerializer):
    token = serializers.CharField(required=True)
    uuid = serializers.CharField(required=False)

    def create(self, validated_data):
        try:
            user = self.context['request'].user
            unregister_device(user,
                              validated_data['token'],
                              validated_data.get('uuid', None))

            return {"success": True}
        except Exception as e:
            return {"error": str(e)}


class VendorPreferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = VendorPreference
        fields = [
            'id',
            'checkin_checkout',
            'marketing',
            'support'
        ]


class EaterPreferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = EaterPreference
        fields = [
            'id',
            'marketing',
            'review'
        ]


class TestNotificationSerializer(CustomSerializer):
    token = serializers.CharField(required=False)
    type = serializers.CharField(required=False)

    def create(self, validated_data):
        if settings.DEBUG is False:
            return {"error": str("Test endpoint not allowed on live")}

        try:
            user = self.context['request'].user
            notification_text = "This is a test notification"
            data = {
                "type": CHECKIN_CHECKOUT,
                "title": ""
            }
            send_message_to_devices(user.user_type,
                                    user.devices.all(),
                                    notification_text,
                                    data,
                                    1)
            return {"success": True}
        except Exception as e:
            return {"error": str(e)}
