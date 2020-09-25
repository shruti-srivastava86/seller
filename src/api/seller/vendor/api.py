from django.db import models
from django.db.models import Subquery
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework.generics import (
    ListAPIView,
    RetrieveUpdateAPIView,
    RetrieveAPIView
)
from rest_framework.settings import api_settings

from api.generics.generics import (
    DualSerializerUpdateAPIView,
    SuccessResponseSerializer,
    CustomRetrieveAPIView,
    CustomListAPIView,
    DualSerializerCreateAPIView
)
from api.generics.permissions import (
    IsAnEater,
    IsAVendor
)
from seller.authentication.api import BaseSignUpView
from seller.dish.api import DishListView
from seller.dish.models import Dish
from seller.review.models import Rating
from seller.review.utils import vendor_total_average_ratings
from seller.user.models import SearchTerms
from seller.user.serializers import (
    UserTransactionSerializer
)
from seller.vendor.filters import (
    DistanceFilter,
    OrderingFilter,
    VendorFilter
)
from seller.vendor.models import Vendor, Market, VendorProfileViews
from seller.vendor.serializers import (
    VendorSignUpSerializer,
    VendorListSerializer,
    VendorDetailSerializer,
    VendorFavouriteSerializer,
    VendorUnFavouriteSerializer,
    VendorCheckInSerializer,
    VendorCheckOutSerializer,
    VendorProfileSerializer,
    VendorTransactionCreateSerializer,
    MarketSerializer,
    VendorNotificationSerializer)


class VendorSignUpView(BaseSignUpView):
    """
        Overrides the BaseSignUpView to Sign up a User as a Vendor.
    """
    request_serializer_class = VendorSignUpSerializer


class VendorProfileView(CustomRetrieveAPIView, DualSerializerUpdateAPIView):
    """
        View for vendor profile page.
    """
    serializer_class = VendorProfileSerializer
    request_serializer_class = serializer_class
    response_serializer_class = SuccessResponseSerializer
    permission_classes = [IsAVendor]

    def get_object(self):
        return self.request.user.vendor

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['ratings'] = vendor_total_average_ratings(self.get_object())
        return context


class VendorCheckIn(DualSerializerUpdateAPIView):
    """
        View for vendor to check-in near a location
    """
    request_serializer_class = VendorCheckInSerializer
    response_serializer_class = SuccessResponseSerializer
    permission_classes = [IsAVendor]

    def get_object(self):
        return self.request.user.vendor


class VendorCheckOut(RetrieveAPIView, VendorCheckIn):
    """
        View to retrieve vendor checkout time and to check-out from a location
    """
    serializer_class = VendorCheckOutSerializer
    request_serializer_class = serializer_class


class VendorListView(ListAPIView):
    """
        View for listing near by Vendors with respect to an Eater
    """

    serializer_class = VendorListSerializer
    permission_classes = [IsAnEater]
    filter_backends = api_settings.DEFAULT_FILTER_BACKENDS + [
        DistanceFilter,
        OrderingFilter,
        VendorFilter
    ]
    distance_filter_field = 'location'
    search_fields = ['name', 'business__cuisine__name', 'business__name']

    def get_queryset(self):
        search = self.request.GET.get('search', None)
        if search:
            SearchTerms.objects.create(user=self.request.user,
                                       word=search)
        queryset = Vendor.filter.active(). \
            approved(). \
            with_business(). \
            with_active_dishes(). \
            select_related_business(). \
            prefetch_related_dietary(). \
            prefetch_related_cuisine(). \
            annotate(
            average_rating=Subquery(
                Rating.objects.average_rating_subquery(),
                output_field=models.FloatField()
            ),
            total_ratings=Subquery(
                Rating.objects.total_rating_subquery(),
                output_field=models.IntegerField()
            )
        )

        return queryset


class VendorRetrieveUpdateView(RetrieveUpdateAPIView):
    """
        View for retrieving and updating a vendor
    """
    serializer_class = VendorDetailSerializer

    def get_queryset(self):
        queryset = Vendor.filter.active(). \
            with_active_dishes(). \
            select_related_business(). \
            prefetch_related_dietary(). \
            prefetch_related_cuisine()

        vendor = Vendor.objects.get(id=self.kwargs['pk'])
        try:

            profile_view = VendorProfileViews.objects.get(
                vendor=vendor,
                created_at__date=timezone.now().date()
            )
            if self.request.user.name == "Guest User":
                profile_view.guest_count += 1
            else:
                profile_view.count += 1
            profile_view.save()
        except Exception as e:
            profile_view = VendorProfileViews()
            profile_view.vendor = vendor
            if self.request.user.name == "Guest User":
                profile_view.guest_count = 1
            else:
                profile_view.count = 1

            profile_view.save()

        return queryset

    def get_permissions(self):
        if self.request.method == "GET":
            return [IsAnEater()]
        return [IsAVendor()]


class VendorRetrieveView(VendorRetrieveUpdateView):

    def get_object(self):
        return get_object_or_404(Vendor, uuid=self.request.GET.get('vendor_uuid'))


class VendorTransactionListCreateView(CustomListAPIView, DualSerializerCreateAPIView):
    """
        View to list and create transactions for vendor.
    """
    serializer_class = UserTransactionSerializer
    request_serializer_class = VendorTransactionCreateSerializer
    response_serializer_class = VendorTransactionCreateSerializer
    filter_backends = api_settings.DEFAULT_FILTER_BACKENDS
    permission_classes = [IsAVendor]
    ordering = ['-created_at']

    def get_queryset(self):
        return self.request.user.transactions.all()


class FavouriteVendor(DualSerializerUpdateAPIView):
    """
        View to favourite a vendor
    """
    request_serializer_class = VendorFavouriteSerializer
    response_serializer_class = SuccessResponseSerializer
    queryset = Vendor.objects.all()


class UnFavouriteVendor(FavouriteVendor):
    """
        View to un-favourite a vendor
    """
    request_serializer_class = VendorUnFavouriteSerializer


class VendorDishesList(DishListView):
    """
        View to list all dishes of a vendor
    """

    def get_queryset(self):
        return Dish.objects.is_active().for_vendor(
            self.kwargs['pk']
        )


class MarketListView(ListAPIView):
    """
        View to list all markets for vendor
    """

    serializer_class = MarketSerializer
    queryset = Market.objects.all()
    ordering = 'name'


class VendorNotificationsView(CustomListAPIView):
    serializer_class = VendorNotificationSerializer
    ordering = ['-created_at']

    def get_queryset(self):
        return self.request.user.notifications.all()
