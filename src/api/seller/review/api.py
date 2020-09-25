from rest_framework.settings import api_settings

from api.generics.generics import (
    CustomListAPIView,
    DualSerializerCreateAPIView,
    SuccessResponseSerializer
)
from api.generics.permissions import IsAVendor, IsAnEater
from seller.eater.serializers import EaterRatingSerializer
from seller.review.models import Rating
from seller.review.serializers import (
    VendorRatingSerializer,
    RatingCreateSerializer
)


class VendorRatingListView(CustomListAPIView):
    """
        View for retrieving all ratings for a vendor
    """
    serializer_class = VendorRatingSerializer
    permission_classes = [IsAVendor]
    filter_backends = api_settings.DEFAULT_FILTER_BACKENDS
    ordering_fields = ['created_at']
    ordering = ['-created_at']

    def get_queryset(self):
        return Rating.objects.select_related_vendor(). \
            with_average_rating(). \
            for_vendor(self.request.user.vendor)


class EaterRatingCreateView(CustomListAPIView, DualSerializerCreateAPIView):
    """
        View for posting a rating for a particular purchase
    """
    serializer_class = EaterRatingSerializer
    request_serializer_class = RatingCreateSerializer
    response_serializer_class = SuccessResponseSerializer
    permission_classes = [IsAnEater]
    ordering_fields = ['created_at']
    ordering = ['-created_at']

    def get_queryset(self):
        return Rating.objects.select_related_eater(). \
            with_average_rating(). \
            for_eater(self.request.user.eater)
