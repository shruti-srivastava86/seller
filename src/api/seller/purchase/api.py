from rest_framework.generics import (
    ListCreateAPIView
)
from rest_framework.settings import api_settings

from api.generics.permissions import IsAnEater
from seller.purchase.models import Purchase
from seller.purchase.serializers import PurchaseListSerializer


class PurchaseListView(ListCreateAPIView):
    """
        View for retrieving all purchases for an eater
    """
    serializer_class = PurchaseListSerializer
    permission_classes = [IsAnEater]
    filter_backends = api_settings.DEFAULT_FILTER_BACKENDS
    ordering_fields = ['created_at']
    ordering = ['-created_at']

    def get_queryset(self):
        return Purchase.objects.select_related_rating(). \
            for_eater(self.request.user.eater)
