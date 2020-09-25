from rest_framework import serializers

from api.generics.generics import CustomModelSerializer
from seller.purchase.models import Purchase
from seller.purchase.serializers import PurchaseRatingSerilaizer
from seller.review.models import Rating
from seller.user import enums
from seller.user.models import Transaction, GeneralSettings
from seller.user.validators import Validations


class RatingSerializer(CustomModelSerializer):
    class Meta:
        model = Rating
        fields = "__all__"


class VendorRatingSerializer(serializers.ModelSerializer):
    purchase = PurchaseRatingSerilaizer(read_only=True)
    average_rating = serializers.SerializerMethodField()

    def get_average_rating(self, obj):
        return obj.average_rating

    class Meta:
        model = Rating
        fields = "__all__"


class RatingCreateSerializer(RatingSerializer):
    purchase = serializers.IntegerField(required=True)

    def create_transaction(self, user, purchase):
        general_settings = Validations.validate_general_settings()
        user.coins += general_settings.review_points
        user.save()
        transaction = Transaction(user=user,
                                  purchase=purchase,
                                  coins=general_settings.review_points,
                                  amount=GeneralSettings.objects.get_convert_to_pounds(
                                      general_settings.review_points),
                                  balance=user.coins,
                                  type=enums.CREDIT,
                                  reason=enums.EATER_REVIEW,
                                  status=enums.SUCCESS,
                                  note="Added points for reviewing ")
        transaction.save()
        return transaction

    def create(self, validated_data):
        try:
            purchase = Purchase.objects.get(
                id=validated_data.pop('purchase'),
                eater=self.context['request'].user.eater
            )

            try:
                Rating.objects.get(purchase=purchase)
            except Exception as e:

                Rating.objects.create(
                    purchase=purchase,
                    **validated_data
                )
            self.create_transaction(self.context['request'].user,
                                    purchase)
            return {"success": True}
        except Exception as e:
            return {"error": str(e)}
