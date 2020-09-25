from django.contrib import admin

from seller.review.models import Rating


class RatingAdmin(admin.ModelAdmin):
    list_display = ['id', 'purchase_id', 'created_at', 'vendor_id', 'vendor_email', 'eater_id', 'eater_email',
                    'overall_rating', 'text']
    list_select_related = ['purchase__eater', 'purchase__vendor', ]
    list_filter = ['purchase__vendor__business__name', 'overall_rating']
    search_fields = ['purchase__vendor__business__name']
    raw_id_fields = ['purchase', ]

    def vendor_email(self, obj):
        return obj.purchase.vendor.email

    def eater_email(self, obj):
        return obj.purchase.eater.email

    def vendor_id(self, obj):
        return obj.purchase.vendor_id

    def eater_id(self, obj):
        return obj.purchase.eater_id

    def lookup_allowed(self, key, value):
        if key in ['purchase__vendor', 'purchase__eater']:
            return True
        return super().lookup_allowed(key, value)


admin.site.register(Rating, RatingAdmin)
