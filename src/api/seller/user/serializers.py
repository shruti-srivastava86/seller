from rest_framework import serializers

from api.generics.generics import CustomModelSerializer
from seller.purchase.serializers import PurchaseSerializer
from seller.user import enums
from seller.user.models import (
    User,
    Transaction,
)


class UserSerializer(serializers.ModelSerializer):
    """
        Serializer for use with the User model for the current user.
    """
    photo = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()

    def get_photo(self, obj):
        try:
            if obj.vendor.photo.url:
                return obj.vendor.photo.url
            return None
        except Exception as e:
            return None

    def get_status(self, obj):
        status = None

        try:
            if obj.user_type == enums.VENDOR:
                status = obj.vendor.status
            elif obj.user_type == enums.EATER:
                status = obj.eater.status

        except Exception as e:
            status = None

        return status

    class Meta:
        model = User
        fields = ['id', 'user_type', 'name', 'email', 'photo', 'status']


class VendorSerializer(UserSerializer):
    business_name = serializers.SerializerMethodField()

    def get_business_name(self, obj):
        return obj.vendor.business.name if obj.user_type == enums.VENDOR else None

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + ['business_name']


class UserTransactionSerializer(CustomModelSerializer):
    purchase = PurchaseSerializer(read_only=True)
    user = UserSerializer()
    vendor = serializers.SerializerMethodField()

    def get_vendor(self, obj):
        try:
            if obj.type == enums.DEBIT:
                trans = self.context.get('credit_transactions').filter(
                    qr_id=obj.qr_id
                ).first()
                if trans:
                    return trans.user.vendor.business.name
                else:
                    return None
            else:
                return None
        except Exception as e:
            return None

    class Meta:
        model = Transaction
        fields = [
            'id',
            'created_at',
            'user',
            'purchase',
            'vendor',
            'qr_id',
            'coins',
            'amount',
            'balance',
            'type',
            'reason',
            'status',
            'note'

        ]
