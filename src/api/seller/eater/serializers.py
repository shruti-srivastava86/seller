import json

from rest_framework import serializers

from api.generics.generics import CustomModelSerializer
from seller.authentication.serializers import SignUpSerializer
from seller.dish.serializers import DietarySerializer
from seller.eater import enums as eater_enums
from seller.eater.models import Eater
from seller.eater.utils import send_report_vendor_email, send_support_vendor_email
from seller.notification.models import Notifications
from seller.purchase.serializers import PurchaseRatingSerilaizer
from seller.review.models import Rating
from seller.user import enums
from seller.user.models import (
    Transaction,
    GeneralSettings,
    ReportVendor,
    ReportVendorList,
    SupportEater)
from seller.user.utils import UserUtils
from seller.user.validators import Validations
from seller.vendor.models import Market


class EaterMarketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Market
        fields = ['id', 'name']


class EaterSignUpSerializer(SignUpSerializer):
    """
        Serializer for dealing with a Eater Sign up post request.
    """

    def create(self, validated_data):
        return Eater.objects.create_user(**validated_data)


class EaterSerializer(serializers.ModelSerializer):
    dietary_preference = DietarySerializer(many=True)
    pounds = serializers.SerializerMethodField()
    home_market = EaterMarketSerializer()

    def get_pounds(self, obj):
        if obj.coins != 0:
            return GeneralSettings.objects.get_convert_to_pounds(obj.coins)
        else:
            return 0

    class Meta:
        model = Eater
        fields = ['id',
                  'name',
                  'email',
                  'coins',
                  'dietary_preference',
                  'pounds',
                  'home_market']
        read_only_fields = ['coins']


class EaterUpdateSerializer(serializers.ModelSerializer):
    dietary_preference = serializers.ListField(required=False)

    def create_transaction(self, user):
        general_settings = Validations.validate_general_settings()
        user.eater.coins += general_settings.dietary_preference
        user.eater.save()
        transaction = Transaction(user=user,
                                  coins=general_settings.dietary_preference,
                                  amount=GeneralSettings.objects.get_convert_to_pounds(
                                      general_settings.dietary_preference),
                                  balance=user.coins,
                                  type=enums.CREDIT,
                                  reason=enums.DIETARY_PREFERENCE,
                                  status=enums.SUCCESS,
                                  note="Added points for saving dietary preferences")
        transaction.save()
        return transaction

    def update(self, instance, validated_data):
        user = self.context.get('request').user
        if "dietary_preference" in validated_data:
            if not instance.is_dietary_preference:
                instance.is_dietary_preference = True
                self.create_transaction(user)

            instance.dietary_preference.clear()
            instance.dietary_preference.add(*validated_data.pop('dietary_preference'))
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

    class Meta:
        model = Eater
        fields = ['name',
                  'email',
                  'dietary_preference',
                  'home_market']


class EaterTransactionCreateSerializer(CustomModelSerializer):
    coins = serializers.IntegerField(required=True)

    def create_transaction(self, user, validated_data):
        validated_data['type'] = enums.DEBIT
        validated_data['reason'] = enums.EATER_REWARD
        validated_data['balance'] = user.coins
        validated_data['status'] = enums.PENDING
        transaction = Transaction(user=user, **validated_data)
        transaction.save()
        return transaction

    def create(self, validated_data):
        general_settings = Validations.validate_general_settings()
        Validations.validate_min_max_coins_limit(
            general_settings,
            validated_data.get('coins')
        )

        Validations.validate_user_coins(
            self.context.get('request').user,
            validated_data.get('coins')
        )

        validated_data['amount'] = general_settings.one_coin_to_pounds * validated_data.get('coins')
        transaction = self.create_transaction(
            self.context.get('request').user,
            validated_data
        )
        return transaction

    class Meta:
        model = Transaction
        exclude = [
            'user',
            'type',
            'reason',
            'balance'
        ]


class EaterRatingSerializer(serializers.ModelSerializer):
    purchase = PurchaseRatingSerilaizer(read_only=True)
    average_rating = serializers.SerializerMethodField()

    def get_average_rating(self, obj):
        return obj.average_rating

    class Meta:
        model = Rating
        fields = "__all__"


class GeneralSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = GeneralSettings
        fields = ['minimum_coins_redeemable',
                  'maximum_coins_redeemable',
                  'one_coin_to_pounds',
                  'coins_incremental_value',
                  'scan_qr_points',
                  'review_points',
                  'search_radius_in_miles']


class ReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportVendorList
        fields = ['id', 'name']


class ReportVendorSerializer(CustomModelSerializer):

    def create(self, validated_data):
        validated_data['eater'] = self.context.get('request').user.eater
        send_report_vendor_email(validated_data.get('report').name, validated_data.get('message'),
                                 validated_data.get('vendor'), validated_data['eater'])
        return ReportVendor.objects.create(**validated_data)

    class Meta:
        extra_kwargs = {'eater': {'required': False}}
        model = ReportVendor
        fields = "__all__"


class SupportEaterSerializer(CustomModelSerializer):

    def create(self, validated_data):
        eater = self.context.get('request').user.eater
        validated_data['eater'] = eater
        users_email = [self.context.get('request').user.email]
        send_support_vendor_email("support", validated_data.get('message'), users_email, eater)
        return SupportEater.objects.create(**validated_data)

    class Meta:
        extra_kwargs = {'eater': {'required': False}}
        model = SupportEater
        fields = "__all__"


class EaterNotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notifications
        fields = "__all__"

    context = serializers.SerializerMethodField()

    def get_context(self, obj):
        try:
            return json.loads(obj.context)
        except Exception:
            return None


class FacebookSignupSerializer(CustomModelSerializer):
    facebook_token = serializers.CharField(required=True)
    name = serializers.CharField(required=True)
    facebook_id = serializers.CharField(required=True)

    def validate_email(self, obj):
        return Validations.validate_email(obj)

    def validate_facebook_id(self, obj):
        return Validations.validate_facebook_id(obj)

    def create(self, validated_data):
        validated_data.pop('facebook_token')
        validated_data.pop('facebook_id')
        validated_data['password'] = UserUtils.generate_random_token()
        validated_data['user_type'] = enums.EATER
        validated_data['type'] = eater_enums.FACEBOOK_SIGNUP
        return super(FacebookSignupSerializer, self).create(validated_data)

    class Meta:
        model = Eater
        fields = ['id',
                  'name',
                  'email',
                  'facebook_token',
                  'facebook_id',
                  'type']


class EaterReviewCheckSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rating
        fields = "__all__"
