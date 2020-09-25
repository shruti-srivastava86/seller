from django.conf import settings
from django.utils.safestring import mark_safe
from django.utils.html import escape
from django.shortcuts import render

from django.contrib import admin

from seller.purchase.models import Purchase, PurchaseItem
from seller.utils import ExportCsvMixin


def _render(obj, template):
    return mark_safe(render(None, template, {
        'purchase': obj,
    }).content.decode('utf-8'))


class PurchaseAdmin(admin.ModelAdmin, ExportCsvMixin):
    search_fields = ['eater__email', 'vendor__email', 'eater__name', 'vendor__name']
    readonly_fields = ['dishes_details', 'price_paid', 'full_price_amount', 'has_special', ]
    list_select_related = ['vendor', 'eater', ]
    list_display = [
        'id', 'created_at', 'vendor_id', 'vendor_email', 'eater_id',
        'eater_email', 'waiting_time', 'items_bought', 'price_paid', 'full_price_amount',
        'has_special', 'amount', 'eater_location', 'vendor_locations', 'check_in']
    list_filter = ['vendor__business__name']
    actions = ['export_as_csv']
    ordering = ['-created_at']

    def items_bought(self, obj):

        return mark_safe(
            '<br/>'.join([escape(item.get('name')) for item in obj.details]))

    def vendor_email(self, obj):
        return obj.vendor.email

    def eater_email(self, obj):
        return obj.eater.email

    def get_readonly_fields(self, request, obj=None):
        if settings.DEBUG:
            return self.readonly_fields
        return ['eater', 'vendor'] + self.readonly_fields

    def get_exclude(self, request, obj=None):
        if settings.DEBUG:
            return []
        return ["details"]

    def dishes_details(self, instance):
        return _render(instance, 'admin/purchase/details.html')

    def eater_location(self, obj):

        location = obj.location
        try:
            if location:
                return "{},{}".format(location.x, location.y)
        except Exception as e:
            return None
        return None

    def vendor_locations(self, obj):

        location = obj.vendor_location
        try:
            if location:
                return "{},{}".format(location.x, location.y)
        except Exception as e:
            return None
        return None

    vendor_locations.short_description = "Vendor Location"
    dishes_details.short_description = 'Details'
    dishes_details.allow_tags = True


admin.site.register(Purchase, PurchaseAdmin)
admin.site.register(PurchaseItem)
