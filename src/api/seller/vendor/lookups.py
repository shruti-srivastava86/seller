from ajax_select import register, LookupChannel

from django.db.models import Q

from seller.vendor.models import Vendor, Market


@register('vendors')
class VendorChannel(LookupChannel):
    model = Vendor

    def get_query(self, q, request):
        return Vendor.objects.filter(
            Q(name__icontains=q) | Q(business__name__icontains=q)).select_related('business')

    def _name(self, obj):
        if obj.business:
            return obj.business.name

    def format_item_display(self, obj):
        return self._name(obj)

    def format_match(self, obj):
        return self._name(obj)

    def get_objects(self, ids):
        return Vendor.objects.filter(id__in=ids)


@register('markets')
class MarketChannel(LookupChannel):
    model = Market

    def get_query(self, q, request):
        return Market.objects.filter(name__icontains=q)

    def format_item_display(self, obj):
        return obj.name

    def format_match(self, obj):
        return obj.name
