from rest_framework import serializers

from seller.purchase.models import Purchase
from seller.review.models import Rating
from seller.user.validators import Validations
from seller.vendor import enums
from seller.vendor.models import (
    Vendor,
    Business,
    OpeningHours,
    Image,
    VendorProfileViews
)
from seller.vendor.serializers import (
    BusinessDetailSerializer,
    VendorListSerializer,
    OpeningHoursSerializer)


class BusinessOnboardingSerializer(BusinessDetailSerializer):
    class Meta(BusinessDetailSerializer.Meta):
        exclude = BusinessDetailSerializer.Meta.exclude + ["open",
                                                           "check_out",
                                                           "offer_active",
                                                           "offer"]


class VendorOnboardingSerialzier(VendorListSerializer):
    business = BusinessOnboardingSerializer()
    location = serializers.SerializerMethodField()

    def get_location(self, obj):
        return {
            "lat": obj.location.y,
            "lng": obj.location.x
        } if obj.location else None

    class Meta:
        model = Vendor
        fields = [
            'id',
            'name',
            'email',
            'address',
            'location',
            'status',
            'onboarding_stage',
            'business',
        ]


class OnboardingPhotosSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=False)
    image = serializers.CharField(required=True)
    hero = serializers.BooleanField(required=True)


class BusinessOnboardingRequestSerilaizer(serializers.ModelSerializer):
    opening_hours = OpeningHoursSerializer(many=True)
    photos = OnboardingPhotosSerializer(many=True)
    allergens = serializers.ListField(required=False)
    name = serializers.CharField(required=True)

    def validate_name(self, obj):

        return Validations.validate_update_business_name(
            obj, self.context.get('request').user.vendor
        )

    def update_stage1(self, instance, validated_data):
        instance.business.biography = validated_data.get('biography')
        instance.business.tagline = validated_data.get('tagline')
        instance.business.social_links = validated_data.get('social_links')
        instance.business.description = validated_data.get('description')
        instance.business.name = validated_data.get('name')
        instance.business.social_links = validated_data.get('social_links')
        instance.business.cuisine.clear()
        instance.business.cuisine.add(*validated_data.get('cuisine'))
        instance.onboarding_stage = enums.STAGE2

    def update_stage2(self, instance, validated_data):
        instance.business.cash = validated_data.get('cash')
        instance.business.card = validated_data.get('card')

        for opening_hour in validated_data.get('opening_hours'):

            opening_hour_object = instance.business.opening_hours.filter(
                weekday=opening_hour.get('weekday')
            ).first()
            if opening_hour_object:
                opening_hour_object.from_hour = opening_hour.get('from_hour')
                opening_hour_object.to_hour = opening_hour.get('to_hour')
                opening_hour_object.open = opening_hour.get('open')
            else:
                opening_hour_object = OpeningHours(
                    business=instance.business,
                    weekday=opening_hour.get('weekday'),
                    from_hour=opening_hour.get('from_hour'),
                    to_hour=opening_hour.get('to_hour'),
                    open=opening_hour.get('open')
                )
            opening_hour_object.save()
        instance.onboarding_stage = enums.STAGE3

    def update_stage3(self, instance, validated_data):
        instance.business.home_market.clear()
        instance.business.home_market.add(*validated_data.get('home_market'))
        instance.onboarding_stage = enums.STAGE4

    def update_stage4(self, instance, validated_data):
        photos = self.initial_data.get('photos')
        Image.objects.filter(
            id__in=self.initial_data.get('delete_photos', [])
        ).delete()
        for photo in photos:
            if photo.get('id'):
                instance.business.photos.filter(
                    id=photo.get('id')
                ).update(hero=photo.get('hero'))
            else:
                instance.business.photos.add(
                    Image.objects.create(
                        image=photo.get('image'),
                        hero=photo.get('hero')
                    )
                )
        instance.onboarding_stage = enums.STAGE5

    def update_stage5(self, instance, validated_data):
        instance.business.ingredients = validated_data.get('ingredients')
        instance.onboarding_stage = enums.STAGE6

    def update_stage6(self, instance, validated_data):
        instance.business.allergens.clear()
        instance.business.allergens.add(*validated_data.get('allergens'))
        instance.status = enums.COMPLETED

    def update(self, instance, validated_data):
        onboarding_stage = self.initial_data.get('onboarding_stage')
        if onboarding_stage == enums.STAGE1:
            self.update_stage1(instance, validated_data)
        elif onboarding_stage == enums.STAGE2:
            self.update_stage2(instance, validated_data)
        elif onboarding_stage == enums.STAGE3:
            self.update_stage3(instance, validated_data)
        elif onboarding_stage == enums.STAGE4:
            self.update_stage4(instance, validated_data)
        elif onboarding_stage == enums.STAGE5:
            self.update_stage5(instance, validated_data)
        elif onboarding_stage == enums.STAGE6:
            self.update_stage6(instance, validated_data)

        instance.business.save()
        instance.save()
        return instance

    class Meta:
        model = Business
        exclude = [
            "vendor",
            "open",
            "check_out",
            "offer_active",
            "offer"
        ]


class VendorIngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Business
        fields = ['ingredients']


class VendorWebProfileSerilaizer(BusinessDetailSerializer):

    def update(self, instance, validated_data):
        instance.offer = validated_data.get('offer')
        instance.save()
        return instance

    class Meta:
        model = Business
        exclude = ['vendor']


class VendorProfileUpdateSerializer(serializers.ModelSerializer):

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name')
        instance.email = validated_data.get('email')
        instance.save()
        return instance

    class Meta:
        model = Vendor
        fields = ['name',
                  'email',
                  'address_line_1',
                  'address_line_2',
                  'city',
                  'county',
                  'postcode']


class VendorAddressUpdateSerializer(serializers.ModelSerializer):

    def update(self, instance, validated_data):
        instance.address_line_1 = validated_data.get('address_line_1')
        instance.address_line_2 = validated_data.get('address_line_2')
        instance.city = validated_data.get('city')
        instance.county = validated_data.get('county')
        instance.postcode = validated_data.get('postcode')
        instance.save()
        return instance

    class Meta:
        model = Vendor
        fields = ['address_line_1',
                  'address_line_2',
                  'city',
                  'county',
                  'postcode']


class VendorBusinessInfoUpdateSerializer(serializers.ModelSerializer):

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name')
        instance.biography = validated_data.get('biography')
        instance.tagline = validated_data.get('tagline')
        instance.social_links = validated_data.get('social_links')
        instance.cuisine.clear()
        instance.cuisine.add(*validated_data.get('cuisine'))
        instance.save()
        return instance

    class Meta:
        model = Business
        fields = ['name', 'tagline', 'biography', 'cuisine', 'social_links']


class VendorTradingInfoUpdateSerializer(serializers.ModelSerializer):
    opening_hours = OpeningHoursSerializer(many=True)

    def update(self, instance, validated_data):
        instance.cash = validated_data.get('cash')
        instance.card = validated_data.get('card')

        for opening_hour in validated_data.get('opening_hours'):

            opening_hour_object = instance.opening_hours.filter(
                weekday=opening_hour.get('weekday')
            ).first()
            if opening_hour_object:
                opening_hour_object.from_hour = opening_hour.get('from_hour')
                opening_hour_object.to_hour = opening_hour.get('to_hour')
                opening_hour_object.open = opening_hour.get('open')
            else:
                opening_hour_object = OpeningHours(
                    business=instance,
                    weekday=opening_hour.get('weekday'),
                    from_hour=opening_hour.get('from_hour'),
                    to_hour=opening_hour.get('to_hour'),
                    open=opening_hour.get('open')
                )
            opening_hour_object.save()
        instance.save()

        return instance

    class Meta:
        model = Business
        fields = ['opening_hours', 'cash', 'card']


class VendorAllergensUpdateSerializer(serializers.ModelSerializer):
    allergens = serializers.ListField(required=False)

    def update(self, instance, validated_data):
        instance.allergens.clear()
        instance.allergens.add(*validated_data.get('allergens'))
        instance.save()
        return instance

    class Meta:
        model = Business
        fields = ['id', 'allergens']


class VendorImageUpdateSerializer(serializers.ModelSerializer):
    photos = OnboardingPhotosSerializer(many=True)

    def update(self, instance, validated_data):
        photos = self.initial_data.get('photos')
        Image.objects.filter(
            id__in=self.initial_data.get('delete_photos', [])
        ).delete()
        for photo in photos:
            if photo.get('id'):
                instance.photos.filter(
                    id=photo.get('id')
                ).update(hero=photo.get('hero'))
            else:
                instance.photos.add(
                    Image.objects.create(
                        image=photo.get('image'),
                        hero=photo.get('hero')
                    )
                )
        instance.save()
        return instance

    class Meta:
        model = Business
        fields = ['id', 'photos']


class VendorIngredientsUpdateSerializer(serializers.ModelSerializer):

    def update(self, instance, validated_data):
        instance.ingredients = validated_data.get('ingredients')
        instance.save()
        return instance

    class Meta:
        model = Business
        fields = ['id', 'ingredients']


class VendorLocationUpdateSerializer(serializers.ModelSerializer):

    def update(self, instance, validated_data):
        instance.home_market.clear()
        instance.home_market.add(*validated_data.get('home_market'))
        instance.save()
        return instance

    class Meta:
        model = Business
        fields = ['id', 'home_market']


class VendorSearchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vendor
        fields = ['id', 'name']


class VendorProfileViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = VendorProfileViews
        fields = ['count']


class VendorDashboardSerializer(serializers.ModelSerializer):
    overall_rating_average = serializers.SerializerMethodField()
    favourite = serializers.SerializerMethodField()
    wait_time = serializers.SerializerMethodField()
    last_30_wait_time = serializers.SerializerMethodField()
    total_views = serializers.SerializerMethodField()
    last_30_total_views = serializers.SerializerMethodField()

    def get_favourite(self, obj):
        return obj.favourite_by.all().count()

    def get_overall_rating_average(self, obj):
        return round(self.context.get('ratings').get('overall_rating_average'), 2)

    def get_wait_time(self, obj):
        return round(self.context.get('wait_time').get('average_wait_time'), 2)

    def get_last_30_wait_time(self, obj):
        return round(self.context.get('last_30_wait_time').get('average_wait_time'), 2)

    def get_total_views(self, obj):
        return self.context.get('total_views').get('total_views')

    def get_last_30_total_views(self, obj):
        return self.context.get('last_30_total_views').get('total_views')

    class Meta:
        model = Vendor
        fields = [
            'id',
            'name',
            'overall_rating_average',
            'favourite',
            'wait_time',
            'last_30_wait_time',
            'total_views',
            'last_30_total_views'
        ]


class VendorLatestTransactionSerializer(serializers.Serializer):
    date = serializers.DateTimeField()
    transactions = serializers.IntegerField()
    sales = serializers.IntegerField()
    wait_time = serializers.CharField()
    check_in = serializers.CharField()
    check_out = serializers.CharField()


class VendorCustomerTypeSerializer(serializers.Serializer):
    new_customer = serializers.DecimalField(max_digits=8, decimal_places=2)
    old_customer = serializers.DecimalField(max_digits=8, decimal_places=2)


class VendorMostPurchasedDishes(serializers.Serializer):
    name = serializers.CharField()
    qty = serializers.IntegerField()
    dish_id = serializers.IntegerField()


class VendorHighestRatedDishes(serializers.Serializer):
    name = serializers.CharField()
    rating = serializers.DecimalField(max_digits=8, decimal_places=2)
    dish_id = serializers.IntegerField()


class ConversationDeatilsWeb(serializers.Serializer):
    unread = serializers.IntegerField()
    support = serializers.IntegerField()
    notifications = serializers.IntegerField()
    sellerconnect = serializers.IntegerField()


class PurchaseRatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rating
        fields = "__all__"


class PurchaseSerializer(serializers.ModelSerializer):
    rating = PurchaseRatingSerializer(read_only=True)
    new_customer = serializers.SerializerMethodField()
    discount = serializers.SerializerMethodField()

    def get_new_customer(self, obj):
        return obj.eater_type

    def get_discount(self, obj):
        return obj.discount

    class Meta:
        model = Purchase
        fields = ['id',
                  'created_at',
                  'new_customer',
                  'rating',
                  'details',
                  'waiting_time',
                  'amount',
                  'discount',
                  'eater_type'
                  ]
