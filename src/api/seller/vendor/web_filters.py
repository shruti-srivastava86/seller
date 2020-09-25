from rest_framework.filters import BaseFilterBackend


class PurchaseFilter(BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        rating = request.query_params.get('rating', None)
        default_days = 7
        if rating:
            queryset = queryset.with_rating(rating)

        dish = request.query_params.get('dish', None)
        if dish:
            queryset = queryset.with_dishes(dish)

        days = request.query_params.get('days', None)
        if days:
            if days != "all":
                queryset = queryset.with_days(days)
        else:
            queryset = queryset.with_days(default_days)

        return queryset.distinct()
