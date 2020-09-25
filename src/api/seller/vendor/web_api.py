from datetime import timedelta, datetime

from django.db.models import Avg, Sum, Count, F
from django.utils import timezone
from rest_framework.generics import (
    ListAPIView
)
from rest_framework.response import Response
from rest_framework.settings import api_settings
from rest_framework.views import APIView

from api.generics.generics import (
    CustomRetrieveAPIView,
    DualSerializerUpdateAPIView,
)
from api.generics.permissions import ProfileIncompleteVendor, IsAVendor, IsASuperUser
from seller.chat.enums import CHAT_TYPES
from seller.dish.api import VendorListCreateDishView
from seller.dish.serializers import DishSerializer
from seller.vendor.utils import unread_count, LargeResultsSetPagination
from seller.purchase.models import Purchase, PurchaseItem
from seller.review.models import Rating
from seller.review.utils import vendor_total_average_ratings, vendor_total_average_wait_time, \
    vendor_total_average_wait_time_30
from seller.vendor import enums
from seller.vendor.api import MarketListView
from seller.vendor.dashboard_utils import vendor_profile_views, vendor_profile_views_30
from seller.vendor.models import Vendor, BusinessCheckinCheckout
from seller.vendor.utils import unread_count_conversation
from seller.vendor.web_filters import PurchaseFilter
from seller.vendor.web_serializers import (
    VendorIngredientSerializer,
    VendorAllergensUpdateSerializer,
    VendorBusinessInfoUpdateSerializer,
    VendorTradingInfoUpdateSerializer,
    VendorImageUpdateSerializer,
    VendorIngredientsUpdateSerializer,
    BusinessDetailSerializer,
    VendorLocationUpdateSerializer,
    VendorProfileUpdateSerializer,
    VendorSearchSerializer,
    VendorDashboardSerializer,
    VendorLatestTransactionSerializer,
    VendorCustomerTypeSerializer,
    VendorMostPurchasedDishes,
    VendorHighestRatedDishes,
    VendorAddressUpdateSerializer,
    ConversationDeatilsWeb, PurchaseSerializer)
from seller.vendor.web_serializers import (
    VendorOnboardingSerialzier,
    BusinessOnboardingRequestSerilaizer,
    VendorWebProfileSerilaizer)


class VendorOnboardingView(CustomRetrieveAPIView, DualSerializerUpdateAPIView):
    serializer_class = VendorOnboardingSerialzier
    request_serializer_class = BusinessOnboardingRequestSerilaizer
    response_serializer_class = VendorOnboardingSerialzier
    permission_classes = [ProfileIncompleteVendor]

    def get_object(self):
        if self.request.user.vendor.status == enums.INCOMPLETE:
            self.request.user.vendor.status = enums.INPROGRESS
            self.request.user.vendor.save()
        return self.request.user.vendor


class VendorIngredientsView(CustomRetrieveAPIView):
    serializer_class = VendorIngredientSerializer
    permission_classes = [IsAVendor]

    def get_object(self):
        return self.request.user.vendor.business


class VendorProfileView(CustomRetrieveAPIView, DualSerializerUpdateAPIView):
    """
        View for vendor profile page.
    """
    serializer_class = VendorWebProfileSerilaizer
    request_serializer_class = serializer_class
    response_serializer_class = BusinessDetailSerializer
    permission_classes = [IsAVendor]

    def get_object(self):
        return self.request.user.vendor.business


class VendorProfileUpdateView(CustomRetrieveAPIView, DualSerializerUpdateAPIView):
    """
        View for vendor profile details page.
    """
    serializer_class = VendorProfileUpdateSerializer
    request_serializer_class = serializer_class
    response_serializer_class = VendorOnboardingSerialzier
    permission_classes = [IsAVendor]

    def get_object(self):
        return self.request.user.vendor


class VendorAddressUpdateView(DualSerializerUpdateAPIView):
    request_serializer_class = VendorAddressUpdateSerializer
    response_serializer_class = VendorOnboardingSerialzier
    permission_classes = [IsAVendor]

    def get_object(self):
        return self.request.user.vendor


class VendorBusinessUpdateView(DualSerializerUpdateAPIView):
    request_serializer_class = VendorBusinessInfoUpdateSerializer
    response_serializer_class = BusinessDetailSerializer
    permission_classes = [IsAVendor]

    def get_object(self):
        return self.request.user.vendor.business


class VendorTradingUpdateView(DualSerializerUpdateAPIView):
    request_serializer_class = VendorTradingInfoUpdateSerializer
    response_serializer_class = BusinessDetailSerializer
    permission_classes = [IsAVendor]

    def get_object(self):
        return self.request.user.vendor.business


class VendorAllergensUpdateView(DualSerializerUpdateAPIView):
    request_serializer_class = VendorAllergensUpdateSerializer
    response_serializer_class = BusinessDetailSerializer
    permission_classes = [IsAVendor]

    def get_object(self):
        return self.request.user.vendor.business


class VendorIngredientsUpdateView(DualSerializerUpdateAPIView):
    request_serializer_class = VendorIngredientsUpdateSerializer
    response_serializer_class = BusinessDetailSerializer
    permission_classes = [IsAVendor]

    def get_object(self):
        return self.request.user.vendor.business


class VendorImagesUpdateView(DualSerializerUpdateAPIView):
    request_serializer_class = VendorImageUpdateSerializer
    response_serializer_class = BusinessDetailSerializer
    permission_classes = [IsAVendor]

    def get_object(self):
        return self.request.user.vendor.business


class VendorLocationUpdateView(DualSerializerUpdateAPIView):
    request_serializer_class = VendorLocationUpdateSerializer
    response_serializer_class = BusinessDetailSerializer
    permission_classes = [IsAVendor]

    def get_object(self):
        return self.request.user.vendor.business


class WebMarketListView(MarketListView):
    pagination_class = None


class VendorSearchView(ListAPIView):
    serializer_class = VendorSearchSerializer
    pagination_class = None
    permission_classes = [IsASuperUser]
    filter_backends = api_settings.DEFAULT_FILTER_BACKENDS
    search_fields = ['name']
    queryset = Vendor.filter.active(). \
        approved(). \
        with_business()


class VendorDashboardView(CustomRetrieveAPIView):
    """
        View for vendor profile page.
    """
    serializer_class = VendorDashboardSerializer

    permission_classes = [IsAVendor]

    def get_object(self):
        return self.request.user.vendor

    def get_serializer_context(self):
        num_days = 30
        requried_date = timezone.now() - timedelta(days=num_days)
        context = super().get_serializer_context()
        context['ratings'] = vendor_total_average_ratings(self.get_object())
        context['wait_time'] = vendor_total_average_wait_time(self.get_object(), requried_date)
        context['last_30_wait_time'] = vendor_total_average_wait_time_30(self.get_object(), requried_date)
        context['total_views'] = vendor_profile_views(self.get_object(), requried_date)
        context['last_30_total_views'] = vendor_profile_views_30(self.get_object(), requried_date)
        return context


class VendorLatestTransactionsView(ListAPIView):
    serializer_class = VendorLatestTransactionSerializer

    def get(self, request, *args, **kwargs):
        num_days = 14
        requried_date = timezone.now() - timedelta(days=num_days)

        pur = Purchase.objects.filter(
            vendor=self.request.user.vendor,
            created_at__date__gte=requried_date
        ).extra(
            {"date": "date_trunc('day',created_at)"}
        ).values(
            "date"
        ).order_by().annotate(
            wait_time=Avg('waiting_time'),
            sales=Sum('amount'),
            transactions=Count('id')
        )
        checkin = BusinessCheckinCheckout.objects.filter(
            business=self.request.user.vendor.business,
            created_at__date__gte=requried_date
        )
        data = []
        for x in range(0, num_days):
            temp = {}
            date = (timezone.now() - timedelta(days=x)).date()
            try:
                latest_purchase = pur.get(created_at__date=date)
                temp['date'] = date
                temp['wait_time'] = latest_purchase.get('wait_time')
                temp['sales'] = latest_purchase.get('sales')
                temp['transactions'] = latest_purchase.get('transactions')
            except Exception as e:
                temp['date'] = date
                temp['wait_time'] = None
                temp['sales'] = None
                temp['transactions'] = None
            try:
                latest_checkin = checkin.get(created_at__date=date)
                temp['check_in'] = latest_checkin.check_in
                temp['check_out'] = latest_checkin.check_out
            except Exception as e:
                temp['check_in'] = None
                temp['check_out'] = None

            data.append(temp)
        return Response(self.serializer_class(data, many=True).data)


class VendorTransactionDetailsView(ListAPIView):
    serializer_class = VendorLatestTransactionSerializer

    def get(self, request, *args, **kwargs):
        num_days = 14
        requried_date = timezone.now() - timedelta(days=num_days)

        pur = Purchase.objects.filter(
            vendor=self.request.user.vendor,
            created_at__date__gte=requried_date
        ).extra(
            {"date": "date_trunc('day',created_at)"}
        ).values(
            "date"
        ).order_by().annotate(
            wait_time=Avg('waiting_time'),
            sales=Sum('amount'),
            transactions=Count('id')
        )
        checkin = BusinessCheckinCheckout.objects.filter(
            business=self.request.user.vendor.business,
            created_at__date__gte=requried_date
        )
        data = []
        for x in range(0, num_days):
            temp = {}
            date = (timezone.now() - timedelta(days=x)).date()
            try:
                latest_purchase = pur.get(created_at__date=date)
                temp['date'] = date
                temp['wait_time'] = latest_purchase.get('wait_time')
                temp['sales'] = latest_purchase.get('sales')
                temp['transactions'] = latest_purchase.get('transactions')
            except Exception as e:
                temp['date'] = date
                temp['wait_time'] = None
                temp['sales'] = None
                temp['transactions'] = None
            try:
                latest_checkin = checkin.get(created_at__date=date)
                temp['check_in'] = latest_checkin.check_in
                temp['check_out'] = latest_checkin.check_out
            except Exception as e:
                temp['check_in'] = None
                temp['check_out'] = None

            data.append(temp)
        return Response(self.serializer_class(data, many=True).data)


class VendorCustomerTypeView(APIView):
    serializer_class = VendorCustomerTypeSerializer

    def get(self, request, *args, **kwargs):
        data = {}
        num_days = 30
        requried_date = datetime.now() - timedelta(days=num_days)
        purchases = Purchase.objects.filter(
            vendor=self.request.user.vendor,
            created_at__date__gte=requried_date

        )
        old_customer = purchases.filter(
            eater__created_at__lt=requried_date
        ).values('eater').distinct().count()
        new_customer = purchases.filter(
            eater__created_at__gte=requried_date
        ).values('eater').distinct().count()

        if old_customer + new_customer > 0:

            data['old_customer'] = round(((old_customer / (old_customer + new_customer)) * 100), 2)

            data['new_customer'] = round(((new_customer / (old_customer + new_customer)) * 100), 2)
        else:
            data['old_customer'] = 0
            data['new_customer'] = 0

        return Response(self.serializer_class(data).data)


class VedorMostPurchasedDishesView(ListAPIView):
    serializer_class = VendorMostPurchasedDishes

    def get(self, request, *args, **kwargs):
        num_days = 30
        requried_date = datetime.now() - timedelta(days=num_days)
        purchase = PurchaseItem.objects.filter(
            purchase__vendor=self.request.user.vendor,
            created_at__date__gte=requried_date
        ).annotate(
            name=F('dishes__name'),
            dish_id=F('dishes__id')
        ).values(
            'name',
            'dish_id'
        ).annotate(
            qty=Sum('quantity')
        ).order_by(
            '-qty')

        highest_rated = Rating.objects.filter(
            purchase__vendor=self.request.user.vendor,
            created_at__date__gte=requried_date
        ).annotate(
            name=F('purchase__items__dishes__name'),
            dish_id=F('purchase__items__dishes__id')
        ).values(
            'name',
            'dish_id'
        ).annotate(
            rating=Avg('overall_rating')
        ).order_by(
            '-rating')
        print(highest_rated)
        return Response(self.serializer_class(purchase, many=True).data)


class VendorHighestRatedDishes(ListAPIView):
    serializer_class = VendorHighestRatedDishes

    def get(self, request, *args, **kwargs):
        num_days = 30
        requried_date = timezone.now() - timedelta(days=num_days)
        highest_rated = Rating.objects.filter(
            purchase__vendor=self.request.user.vendor,
            created_at__date__gte=requried_date
        ).annotate(
            name=F('purchase__items__dishes__name'),
            dish_id=F('purchase__items__dishes__id')
        ).values(
            'name',
            'dish_id'
        ).annotate(
            rating=Avg('overall_rating')
        ).order_by(
            '-rating')

        return Response(self.serializer_class(highest_rated, many=True).data)


class ConversationListDetailsWeb(ListAPIView):
    """
        For creating a new conversation and fetching all conversations
    """
    serializer_class = ConversationDeatilsWeb

    def get(self, request, *args, **kwargs):
        user = self.request.user
        data = {'unread': unread_count(user)}
        for chat in CHAT_TYPES:
            data[chat[1].replace(" ", "").lower()] = unread_count_conversation(user, chat[0])
        return Response(self.serializer_class(data).data)


class PurchaseDetails(ListAPIView):
    pagination_class = LargeResultsSetPagination
    serializer_class = PurchaseSerializer
    filter_backends = api_settings.DEFAULT_FILTER_BACKENDS + [
        PurchaseFilter

    ]

    def get_queryset(self):
        data = self.request.user.vendor.purchases.all() \
            .prefetch_related('rating') \
            .discount() \
            .order_by('-created_at')

        return data


class AllDishesView(VendorListCreateDishView):
    pagination_class = None
    serializer_class = DishSerializer
