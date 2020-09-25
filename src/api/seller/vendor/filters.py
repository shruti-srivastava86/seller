from django.conf import settings
from rest_framework.filters import BaseFilterBackend
from rest_framework_gis.filters import DistanceToPointFilter

from seller.user.models import GeneralSettings

MILE_TO_METERS = 1609.34


class DistanceFilter(DistanceToPointFilter):
    """
        Runs the distance query, and then annotates the distance into the queryset and orders on it.
    """

    def filter_queryset(self, request, queryset, view):
        point = self.get_filter_point(request)
        if point is None:
            return queryset
        point.srid = settings.DEFAULT_SRID  # The filter point doesn't get an SRID set by default
        user = request.user
        user.location = point
        user.save()
        general_settings = GeneralSettings.objects.get_settings()
        if general_settings:
            search_radius_in_miles = general_settings.search_radius_in_miles
        else:
            search_radius_in_miles = settings.DEFAULT_SEARCH_RANGE_IN_MILES
        return queryset.annotate_distance(point).distance_lte(
            float(search_radius_in_miles * 1609.34)
        )


class FavouriteVendorsFilter(BaseFilterBackend):
    """
        Allows filtering by vendors who have been added as favourite by eaters
    """

    def filter_queryset(self, request, queryset, view):
        favourite = request.query_params.get('favourite', None)
        if favourite is None:
            return queryset
        return queryset.favourite_for(request.user.eater) \
            if favourite in [1, "true", "True"] else \
            queryset.not_favourite_for(request.user.eater)


class VendorFilter(BaseFilterBackend):
    """
        Allows filtering by vendors by:
        favourite vendors
        cuisine types
        dietary information
        cash
        card
        offer
    """

    def filter_queryset(self, request, queryset, view):
        favourite = request.query_params.get('favourite', None)
        if favourite:
            queryset = queryset.favourite_for(request.user.eater) \
                if favourite in [1, "true", "True"] else \
                queryset.not_favourite_for(request.user.eater)

        cuisines = request.query_params.get('cuisines', None)
        if cuisines:
            queryset = queryset.with_cuisines(cuisines.split(","))
        dietary = request.query_params.get('prefs', None)
        if dietary:
            queryset = queryset.with_dietary(dietary.split(","))

        cash = request.query_params.get('cash', None)

        card = request.query_params.get('card', None)

        if cash and card:
            queryset = queryset.with_cash_card()
        else:
            if cash:
                queryset = queryset.with_cash() \
                    if cash in [1, "true", "True"] else \
                    queryset.without_cash()
            if card:
                queryset = queryset.with_card() \
                    if card in [1, "true", "True"] else \
                    queryset.without_card()

        offer = request.query_params.get('offer', None)
        if offer:
            queryset = queryset.with_offer() \
                if offer in [1, "true", "True"] else \
                queryset.without_offer()

        discount = request.query_params.get('discount', None)
        if discount:
            queryset = queryset.with_discount() \
                if discount in [1, "true", "True"] else \
                queryset.without_discount()

        rating = request.query_params.get('rating', None)
        if rating:
            ratings = rating.split(",")
            ratings.sort()
            queryset = queryset.with_rating(ratings)
        return queryset.distinct()


class OrderingFilter(BaseFilterBackend):
    """
       Ordering on the queryset returned by the system
    """
    ORDERING_TYPES = {
        "distance": "distance",
        "highestrating": "-average_rating",
        "lowestrating": "average_rating",
        "highesttotalratings": "-total_ratings",
        "lowestlessratings": "total_ratings",
    }

    def filter_queryset(self, request, queryset, view):
        ordering_parameter = request.query_params.get('ordering', None)
        if ordering_parameter is None:
            return queryset.order_by('-business__open', '-pk')

        ordering_value = self.ORDERING_TYPES.get(ordering_parameter, None)
        if ordering_value is None:
            return queryset.distinct()

        if ordering_value == 'distance':
            if 'location' not in request.query_params and \
                    'point' not in request.query_params:
                return queryset.distinct()

        return queryset.order_by('-business__open', ordering_value, '-pk')
