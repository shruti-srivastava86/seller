from django.conf import settings
from django.contrib.gis.geos import Point
from django.db import transaction as atomic_transaction
from rest_framework import serializers, status
from rest_framework.exceptions import APIException

from api.generics.generics import CustomModelSerializer
from seller.dish.models import Dish
from seller.dish.serializers import DishSerializer
from seller.purchase.models import Purchase, PurchaseItem
from seller.review.models import Rating
from seller.user import enums
from seller.user.models import Transaction, GeneralSettings
from seller.user.validators import Validations
from seller.vendor.models import Vendor


class PurchaseRatingSerializer(CustomModelSerializer):
    class Meta:
        model = Rating
        fields = ['purchase']


class VendorSerializer(serializers.ModelSerializer):
    business_name = serializers.SerializerMethodField()

    def get_business_name(self, obj):
        return obj.business.name

    class Meta:
        model = Vendor
        fields = ['id', 'name', 'business_name']


class PurchaseFailure(APIException):
    """Exception thrown when purchase cannot be completed
    """
    status_code = status.HTTP_400_BAD_REQUEST


class PKField(serializers.PrimaryKeyRelatedField):
    """Overridden PrimaryKeyField which returns the primary key
    if needed
    """

    def to_representation(self, value):
        if hasattr(value, 'pk'):
            return super().to_representation(value)
        return value


class PurchaseDetailsSerializer(serializers.Serializer):
    id = PKField(
        queryset=Dish.objects.all(),
        pk_field=serializers.IntegerField())
    price = serializers.DecimalField(max_digits=8, decimal_places=2)
    quantity = serializers.IntegerField()
    name = serializers.CharField()


class PurchaseItemSerializer(serializers.ModelSerializer):
    dishes = DishSerializer()

    class Meta:
        model = PurchaseItem
        fields = ["id",
                  "quantity",
                  "price",
                  "special",
                  "is_discounted",
                  "current_price",
                  "total_price_paid",
                  "purchase",
                  "dishes"
                  ]


class PurchaseSerializer(serializers.ModelSerializer):
    vendor = VendorSerializer(read_only=True)

    details = PurchaseDetailsSerializer(many=True)

    def update_transaction_purchase(self, purchase, transactions):
        transactions.purchase = purchase
        transactions.save()

    def create_transaction(self, user, purchase):
        general_settings = Validations.validate_general_settings()
        user.coins += general_settings.scan_qr_points
        user.save()
        transaction = Transaction(user=user,
                                  purchase=purchase,
                                  coins=general_settings.scan_qr_points,
                                  amount=GeneralSettings.objects.get_convert_to_pounds(
                                      general_settings.scan_qr_points),
                                  balance=user.coins,
                                  type=enums.CREDIT,
                                  reason=enums.EATER_QR_SCAN,
                                  status=enums.SUCCESS,
                                  note="Added points for scanning Qr")
        transaction.save()
        return transaction

    def _process_item(self, item):
        """Returns an improved dict based on serialized data
        """

        dish = item['id']
        item['id'] = dish.id  # Only return id!
        item['name'] = dish.name

        item['current_price'] = dish.current_price
        # Save this in case it changes
        item['is_discounted'] = dish.has_temporary_price
        # Again, save this in case it changes
        item['total_price_paid'] = dish.current_price * item['quantity']
        item['full_price'] = dish.price
        item['special'] = dish.special
        return item

    def create_purchase_items(self, purchase, details):

        for item in details:
            dish = Dish.objects.get(id=item.get('id'))
            PurchaseItem.objects.create(
                purchase=purchase,
                dishes=dish,
                quantity=item.get('quantity'),
                price=dish.price,
                current_price=dish.price,
                total_price_paid=item.get('total_price_paid'),
                is_discounted=item.get('is_discounted'),
                special=item.get('special')
            )

    def create(self, validated_data):
        user = self.context.get('request').user
        vendor = Validations.validate_vendor(self.initial_data.get('vendor_uuid'))
        validated_data['eater_id'] = user.id
        # Reserialize for the database
        validated_data['details'] = [
            self._process_item(item) for item in validated_data['details']]

        validated_data['amount'] = sum(
            (float(x['current_price']) * int(x['quantity'])) for x in validated_data.get('details'))
        validated_data['vendor'] = vendor
        lat = self.initial_data.get('lat', None)
        lng = self.initial_data.get('lng', None)
        validated_data['vendor_location'] = vendor.location
        if Purchase.objects.filter(vendor=vendor, eater=user.eater).first():
            validated_data['eater_type'] = False

        if lat and lng:

            validated_data['location'] = Point(lng,
                                               lat,
                                               srid=4326)
            user.location = Point(lng,
                                  lat,
                                  srid=4326)
            user.save()
        else:
            validated_data['location'] = vendor.location
            user.location = vendor.location
            user.save()
        validated_data['check_in'] = vendor.business.open

        try:
            transaction = Transaction.objects.get(id=self.initial_data.get('transaction'))
        except Exception as e:
            transaction = None

        try:
            with atomic_transaction.atomic():
                purchase = Purchase.objects.create(**validated_data)
                if transaction:
                    self.update_transaction_purchase(purchase, transaction)
                self.create_transaction(user, purchase)
                self.create_purchase_items(purchase, validated_data['details'])

            return purchase
        except Exception as e:
            error = "Unable to create transaction for user. "
            if settings.DEBUG:
                error = "Error {}".format(str(e))
            raise PurchaseFailure(error, code=str(e))

    class Meta:
        model = Purchase
        extra_kwargs = {'vendor': {'required': False}}
        fields = ["id", "details", "vendor", "waiting_time", "dish_not_listed", "not_listed_dish"]


class PurchaseListSerializer(PurchaseSerializer):
    rating = PurchaseRatingSerializer(read_only=True)

    class Meta(PurchaseSerializer.Meta):
        fields = PurchaseSerializer.Meta.fields + [
            'created_at',
            'rating'
        ]


class PurchaseRatingSerilaizer(PurchaseSerializer):
    items = PurchaseItemSerializer(many=True)

    class Meta(PurchaseSerializer.Meta):
        fields = PurchaseSerializer.Meta.fields + [
            'items'
        ]
