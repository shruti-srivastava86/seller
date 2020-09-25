from rest_framework.generics import (
    ListAPIView,
    RetrieveAPIView
)
from rest_framework.settings import api_settings

from api.generics.generics import (
    DualSerializerCreateAPIView,
    DualSerializerUpdateDeleteAPIView,
    CustomListAPIView
)
from api.generics.permissions import IsAVendor, IsAnEater
from seller.dish.models import (
    Cuisine,
    Allergens,
    Dish,
    Dietary
)
from seller.dish.serializers import (
    DishSerializer,
    AddDishSerializer,
    ListDishSerializer,
    DietarySerializer,
    AllergensSerializer,
    CuisineSerializer,
    UpdateDishSerializer
)


class DishListView(CustomListAPIView):
    """
        View for listing all active dishes
    """
    serializer_class = ListDishSerializer
    permission_classes = [IsAnEater]
    queryset = Dish.objects.is_active()
    filter_backends = api_settings.DEFAULT_FILTER_BACKENDS
    filter_fields = ['active']
    ordering_fields = ['serial_id', 'special']
    ordering = ['serial_id', '-created_at', '-special']
    search_fields = ['name']


class VendorListCreateDishView(DishListView, DualSerializerCreateAPIView):
    """
        View for creating new dish, listing active and inactive dishes for a vendor
    """
    request_serializer_class = AddDishSerializer
    response_serializer_class = DishSerializer
    permission_classes = [IsAVendor]
    filter_fields = ['active', 'deleted']

    def get_queryset(self):
        return self.request.user.vendor.business.dishes.prefetch_dietary().all()


class VendorDishRetrieveUpdateDeleteView(RetrieveAPIView, DualSerializerUpdateDeleteAPIView):
    """
        View for retrieving and updating a dish for a vendor
    """
    serializer_class = ListDishSerializer
    request_serializer_class = UpdateDishSerializer
    response_serializer_class = serializer_class
    permission_classes = [IsAVendor]

    def get_queryset(self):
        return self.request.user.vendor.business.dishes.prefetch_dietary().all()


class DietaryListView(ListAPIView):
    """
        View for getting all Dietaries
    """
    serializer_class = DietarySerializer
    queryset = Dietary.objects.all()
    ordering = 'name'


class CuisinesListView(ListAPIView):
    """
        View for getting all Ingredients
    """
    serializer_class = CuisineSerializer
    queryset = Cuisine.objects.all()
    ordering = 'name'


class AllergenListView(ListAPIView):
    """
        View for getting all Allergens
    """
    serializer_class = AllergensSerializer
    queryset = Allergens.objects.all()
    ordering = 'name'


class WebAllergenListView(AllergenListView):
    """
        View for getting all allergens without pagination for web
    """
    pagination_class = None


class WebCuisinesListView(CuisinesListView):
    """
        View for getting all cuisines without pagination for web
    """
    pagination_class = None
