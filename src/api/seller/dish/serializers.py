from rest_framework import serializers

from api.generics.generics import CustomModelSerializer
from seller.dish.models import Dietary, Cuisine, Allergens, Dish


class DishSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dish
        fields = ["id", "name"]


class AllergensSerializer(serializers.ModelSerializer):
    class Meta:
        model = Allergens
        fields = ["id", "name"]


class DietarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Dietary
        fields = ['id', 'name']


class DietaryVendorSerializer(serializers.Serializer):
    id = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()

    def get_id(self, obj):
        return obj.get('dietary_information__id')

    def get_name(self, obj):
        return obj.get('dietary_information__name')


class CuisineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cuisine
        fields = ["id", "name"]


class AddDishSerializer(CustomModelSerializer):
    """
        Serializer for adding of dish to vendor

    """
    description = serializers.CharField(required=True)
    dietary_information = serializers.ListField(required=True)

    def create(self, validated_data):
        vendor = self.context.get('request').user.vendor
        if validated_data.get("special"):
            vendor.business.dishes.all().update(special=False)
        dish = Dish()
        dish.business = vendor.business
        dish.name = validated_data.get("name")
        dish.price = validated_data.get("price")
        dish.description = validated_data.get("description")
        dish.active = validated_data.get("active", True)
        dish.special = validated_data.get("special", False)
        dish.serial_id = validated_data.get("serial_id", 0)
        dish.save()
        dish.dietary_information.add(
            *self.initial_data.get('dietary_information', []))
        return dish

    class Meta:
        model = Dish
        exclude = [
            'id',
            'business',
            'temporary_price',
        ]


class ListDishSerializer(CustomModelSerializer):
    dietary_information = DietarySerializer(many=True, read_only=True)

    class Meta:
        model = Dish
        exclude = [
            'business'
        ]


class UpdateDishSerializer(ListDishSerializer):
    dietary_information = serializers.ListField(required=False)
    deleted_dietary_information = serializers.ListField(required=False)

    def update(self, instance, validated_data):

        vendor = self.context.get('request').user.vendor
        if validated_data.get('deleted_dietary_information'):
            instance.dietary_information.remove(*validated_data.get('deleted_dietary_information'))
        if validated_data.get('dietary_information'):
            instance.dietary_information.add(*validated_data.get('dietary_information'))

        if validated_data.get("special"):
            vendor.business.dishes.all().update(special=False)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if vendor.business.dishes.filter(temporary_price__gt=0).exists():
            vendor.business.discount_active = True
            vendor.business.save()
        else:
            vendor.business.discount_active = False
            vendor.business.save()

        return instance
