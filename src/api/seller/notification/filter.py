from rest_framework.filters import BaseFilterBackend


class ReviewFilter(BaseFilterBackend):
    """
        Allows filtering by vendors who have been added as favourite by eaters
    """

    def filter_queryset(self, request, queryset, view):
        notification_type = request.query_params.get('notification_type', None)
        if notification_type:
            queryset = queryset.for_review(notification_type)
        read = request.query_params.get('read', None)
        if read:
            queryset = queryset.with_unread() \
                if read in [0, "false", "False"] else \
                queryset.with_read()
        return queryset.distinct()
