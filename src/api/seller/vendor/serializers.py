from django.contrib.gis.geos import Point
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from rest_framework import serializers
from rest_framework.exceptions import ParseError

from api.generics.generics import CustomSerializer, CustomModelSerializer
from seller.authentication.serializers import SignUpSerializer
from seller.dish.serializers import (
    CuisineSerializer,
    AllergensSerializer,
    DietaryVendorSerializer
)
from seller.eater.utils import send_push_notification_eater
from seller.notification.models import Notifications
from seller.user import enums
from seller.user.models import Transaction
from seller.user.validators import Validations
from seller.vendor.models import (
    Vendor,
    Business,
    Image,
    OpeningHours,
    Market,
    BusinessCheckinCheckout)
from seller.vendor.utils import send_on_board_email


class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ('id', 'image', 'hero')


class MarketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Market
        fields = ['id', 'name']


class OpeningHoursSerializer(serializers.ModelSerializer):
    class Meta:
        model = OpeningHours
        fields = ["id", "weekday", "from_hour", "to_hour", "open"]


class BusinessListSerializer(serializers.ModelSerializer):
    photos = serializers.SerializerMethodField()
    check_out = serializers.SerializerMethodField()
    coins = serializers.SerializerMethodField()
    uuid = serializers.SerializerMethodField()

    def get_check_out(self, obj):
        if obj.check_out:
            return obj.check_out.strftime("%H:%M:%S")
        else:
            return None

    def get_photos(self, obj):
        return ImageSerializer(
            obj.photos.all(), many=True
        ).data

    def get_coins(self, obj):
        return obj.vendor.coins

    def get_uuid(self, obj):
        return obj.vendor.uuid

    class Meta:
        model = Business
        fields = [
            "id",
            "name",
            "tagline",
            "photos",
            "description",
            "open",
            "offer_active",
            "offer",
            "biography",
            "check_out",
            "opening_hours",
            "ingredients",
            "home_market",
            "allergens",
            "social_links",
            "coins",
            "uuid",
            "cash",
            "card"

        ]


class VendorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vendor
        fields = [
            "id",
            "name",
            "email",
            "coins",
            "address",
            "uuid",
            "address_line_1",
            "address_line_2",
            "city",
            "county",
            "postcode"
        ]


class BusinessDetailSerializer(BusinessListSerializer):
    allergens = AllergensSerializer(many=True)
    cuisine = CuisineSerializer(many=True)
    opening_hours = OpeningHoursSerializer(many=True)
    home_market = MarketSerializer(many=True)
    vendor = VendorSerializer()

    class Meta:
        model = Business
        exclude = ["created_at", "updated_at"]


class BusinessSerializer(serializers.ModelSerializer):
    photos = ImageSerializer(many=True)
    cuisine = CuisineSerializer(many=True)

    class Meta:
        model = Business
        fields = "__all__"


class VendorSignUpSerializer(SignUpSerializer):
    """
        Serializer for dealing with a Vendor Sign up post request.
    """
    business_name = serializers.CharField(
        required=True
    )

    def validate_business_name(self, obj):
        return Validations.validate_business_name(
            obj
        )

    def create(self, validated_data):
        business_name = validated_data.pop('business_name')
        vendor = Vendor.objects.create_user(**validated_data)
        Business.objects.create(vendor=vendor,
                                name=business_name)
        send_on_board_email(vendor)
        return vendor


class VendorListSerializer(serializers.ModelSerializer):
    """
        Serializer for Listing near by vendors.
    """
    distance = serializers.SerializerMethodField()
    dietary_information = serializers.SerializerMethodField()
    business = BusinessDetailSerializer()
    average_rating = serializers.SerializerMethodField()
    total_ratings = serializers.SerializerMethodField()

    def get_average_rating(self, obj):
        general_settings = Validations.validate_general_settings()
        if obj.total_ratings > general_settings.minimum_reviews_vendor:

            return obj.average_rating
        else:
            return None

    def get_total_ratings(self, obj):
        return obj.total_ratings

    def get_distance(self, obj):
        if hasattr(obj, "distance"):
            return round(obj.distance.mi, 2)
        return None

    def get_dietary_information(self, obj):
        try:
            dietary_information = obj.business.dishes.filter(
                dietary_information__name__isnull=False,
                active=True
            ).values(
                'dietary_information__id',
                'dietary_information__name',
            ).distinct()
            return DietaryVendorSerializer(dietary_information, many=True).data
        except ObjectDoesNotExist:
            return None

    def get_cuisines(self, obj):
        return CuisineSerializer(obj.business.cuisine.all(),
                                 many=True).data

    class Meta:
        model = Vendor
        fields = [
            'id',
            'name',
            'distance',
            'dietary_information',
            'business',
            'average_rating',
            'total_ratings',
            'uuid'
        ]


class VendorProfileSerializer(VendorListSerializer):
    """
        Serializer for retrieving vendor profile.
    """
    overall_rating_average = serializers.SerializerMethodField()
    special = serializers.SerializerMethodField()

    def get_special(self, obj):

        return obj.business.dishes.is_special()

    def get_overall_rating_average(self, obj):
        return round(self.context.get('ratings').get('overall_rating_average'), 2)

    def get_average_rating(self, obj):
        return round(self.context.get('ratings').get('average_rating'), 2)

    def get_total_ratings(self, obj):
        return round(self.context.get('ratings').get('total_ratings'), 2)

    def update_business(self, instance, data):
        for key, value in data.items():
            setattr(instance.business, key, value)
        instance.business.save()

    def update_notification_preference(self, instance, data):
        for key, value in data.items():
            setattr(instance.notification_preference, key, value)
        instance.notification_preference.save()

    def update_time_offset(self, instance, data):
        for key, value in data.items():
            setattr(instance.time_offset, key, value)
        instance.time_offset.save()

    def update(self, instance, validated_data):
        try:
            if "business" in validated_data:
                self.update_business(
                    instance,
                    validated_data.pop('business')
                )
            if "notification_preference" in validated_data:
                self.update_notification_preference(
                    instance,
                    validated_data.pop("notification_preference")
                )
            if "time_offset" in validated_data:
                instance.time_offset = validated_data.get("time_offset")
                instance.save()

            return {"success": True}
        except Exception as e:
            return {"error": str(e)}

    class Meta(VendorListSerializer.Meta):
        fields = VendorListSerializer.Meta.fields + ['coins',
                                                     'address',
                                                     'address_line_1',
                                                     'address_line_2',
                                                     'city',
                                                     'county',
                                                     'postcode',
                                                     'overall_rating_average',
                                                     'special',
                                                     'time_offset']


class VendorDetailSerializer(serializers.ModelSerializer):
    """
        Serializer for updating a Vendor details.
    """
    dietary_information = serializers.SerializerMethodField()
    business = BusinessDetailSerializer()
    location = serializers.SerializerMethodField()

    def get_dietary_information(self, obj):
        try:
            dietary_information = obj.business.dishes.filter(
                dietary_information__name__isnull=False,
                active=True
            ).values(
                'dietary_information__id',
                'dietary_information__name',
            ).distinct()
            return DietaryVendorSerializer(dietary_information, many=True).data
        except ObjectDoesNotExist:
            return None

    def get_location(self, obj):
        return {
            "lat": obj.location.y,
            "lng": obj.location.x
        } if obj.location else None

    class Meta:
        model = Vendor
        fields = ['id',
                  'name',
                  'address',
                  'dietary_information',
                  'business',
                  'location',
                  'address_line_1',
                  'address_line_2',
                  'city',
                  'county',
                  'postcode'
                  ]


class VendorFavouriteSerializer(serializers.ModelSerializer):
    """
        Serializer for make a vendor favourite.
    """

    class Meta:
        model = Vendor
        fields = '__all__'

    def update(self, instance, validated_data):
        try:
            self.context.get('request').user.eater.favourite_vendors.add(
                instance
            )
            return {"success": True}
        except Exception as e:
            return {"error": str(e)}


class VendorUnFavouriteSerializer(serializers.ModelSerializer):
    """
        Serializer to un favourite a vendor.
    """

    class Meta:
        model = Vendor
        fields = '__all__'

    def update(self, instance, validated_data):
        try:
            self.context.get('request').user.eater.favourite_vendors.remove(
                instance
            )
            return {"success": True}
        except Exception as e:
            return {"error": str(e)}


class VendorCheckInSerializer(CustomSerializer):
    """
        Serializer for a vendor to check in at a particular location.
    """
    lat = serializers.FloatField(required=True)
    lng = serializers.FloatField(required=True)
    checkout_time = serializers.CharField(required=True)

    def validate(self, attrs):
        lat = Validations.validate_lat(attrs.get('lat'))
        lng = Validations.validate_lng(attrs.get('lng'))
        checkout_time = Validations.required_field(attrs.get('checkout_time'))
        attrs['location'] = Point(lng,
                                  lat,
                                  srid=4326)
        attrs['checkout'] = timezone.now().replace(
            hour=int(checkout_time.split(":")[0]),
            minute=int(checkout_time.split(":")[1]),
            second=0
        )
        return attrs

    def update(self, instance, validated_data):
        try:
            instance.location = validated_data.get('location')
            instance.save()
            instance.business.check_out = validated_data.get('checkout')
            instance.business.open = True
            instance.business.save()
            try:
                vendor_checkin = BusinessCheckinCheckout.objects.get(created_at__date=timezone.now().date())
                vendor_checkin.check_in = timezone.now().time()
                vendor_checkin.check_out = validated_data.get('checkout')
                vendor_checkin.save()
            except Exception as e:
                vendor_checkin = BusinessCheckinCheckout()
                vendor_checkin.business = instance.business
                vendor_checkin.check_in = timezone.now().time()
                vendor_checkin.check_out = validated_data.get('checkout')
                vendor_checkin.save()
            return {"success": True}
        except Exception as e:
            return {"error": str(e)}


class VendorCheckOutSerializer(serializers.Serializer):
    """
        Serializer for a vendor to check out from a particular location.
        Serializer to fetch vendors current day checkout time.
    """
    checkout_time = serializers.SerializerMethodField()

    def get_checkout_time(self, obj):
        opening_hours = obj.business.opening_hours.filter(
            weekday=timezone.now().weekday()
        )
        if opening_hours:
            return opening_hours.first().to_hour.strftime("%H:%M")
        return None

    def update(self, instance, validated_data):
        try:
            instance.business.check_out = None
            instance.business.open = False
            instance.business.offer_active = False
            instance.business.discount_active = False
            instance.business.save()
            instance.business.dishes.update(temporary_price=0)
            return {"success": True}
        except Exception as e:
            return {"error": str(e)}


class VendorTransactionCreateSerializer(CustomModelSerializer):
    qr_id = serializers.UUIDField(required=True)

    def update_eater_transaction(self, transaction):
        transaction.user.coins -= transaction.coins
        transaction.user.save()
        transaction.balance = transaction.user.coins
        transaction.status = enums.SUCCESS
        transaction.save()

    def create_vendor_transaction(self, user, eater_transaction, note):
        user.coins += eater_transaction.coins
        user.save()
        transaction = Transaction(user=user,
                                  qr_id=eater_transaction.qr_id,
                                  coins=eater_transaction.coins,
                                  amount=eater_transaction.amount,
                                  balance=user.coins,
                                  type=enums.CREDIT,
                                  reason=eater_transaction.reason,
                                  note=note)
        transaction.save()

        return transaction

    def create(self, validated_data):
        general_settings = Validations.validate_general_settings()

        eater_transaction = Validations.validate_transaction(
            validated_data.get('qr_id'),
        )

        Validations.validate_min_max_coins_limit(
            general_settings,
            eater_transaction.coins
        )

        Validations.validate_user_coins(
            eater_transaction.user,
            eater_transaction.coins
        )

        validated_data['amount'] = eater_transaction.amount
        try:
            self.update_eater_transaction(
                eater_transaction,
            )
            send_push_notification_eater(
                self.context.get('request').user,
                eater_transaction
            )
            transaction = self.create_vendor_transaction(
                self.context.get('request').user,
                eater_transaction,
                validated_data.get('note')
            )
            return transaction
        except Exception as e:
            raise ParseError(
                str(e)
            )

    class Meta:
        model = Transaction
        exclude = [
            'user',
            'type',
            'reason'
        ]


class VendorNotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notifications
        fields = "__all__"
