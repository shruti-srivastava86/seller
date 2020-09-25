from ajax_select.fields import AutoCompleteSelectMultipleField, AutoCompleteSelectField
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm
from django.contrib.gis.db import models
from django.db.models import Sum, Count
from django.forms import Textarea
from django.shortcuts import render
from django.utils.safestring import mark_safe

from seller.eater import enums
from seller.eater.models import Eater


class EaterForm(UserChangeForm):
    class Meta:
        model = Eater
        fields = '__all__'

    dietary_preference = AutoCompleteSelectMultipleField('allergens', required=False)
    favourite_vendors = AutoCompleteSelectMultipleField('vendors', required=False)
    home_market = AutoCompleteSelectField('markets', required=False)


def _render(obj, template, context=None):
    return mark_safe(render(None, template, {
        'eater': obj,
    }).content.decode('utf-8'))


class EaterAdmin(UserAdmin):
    list_display = [
        'id', 'name', 'email', 'created_at', 'last_login',
        'status', 'total_transactions', 'total_reviews',
        'last_order', 'coins', 'total_spent', 'review_notifications',
        'marketing_notifications', 'last_location', 'location']
    search_fields = ['name', 'email']
    list_filter = ['dietary_preference', 'favourite_vendors', 'status']
    actions = ['suspend_eater']
    list_select_related = ['notification_preference', ]
    form = EaterForm
    ordering = ['id', ]

    suit_form_tabs = (
        ('general', 'General Information'),
    )
    suit_form_includes = (
        ('admin/eater/stats.html', 'top', 'general'),
        ('admin/eater/search_terms.html', 'bottom', 'general'),

    )

    fieldsets = [
        ('Dietary Information', {
            'classes': ('suit-tab', 'suit-tab-general'),
            'fields': ('dietary_preference',),
        }),
        ('Basic Information', {
            'classes': ('suit-tab', 'suit-tab-general'),
            'fields': ('email', 'password', 'notes', 'created_at', 'last_login',
                       'status', 'location', 'home_market',)
        }),
        ('Preferences', {
            'classes': ('suit-tab', 'suit-tab-general'),
            'fields': ('get_notification_preference', 'favourite_vendors', 'is_dietary_preference')
        }),
        ('Location', {
            'classes': ('suit-tab', 'suit-tab-general'),
            'fields': ('location',)
        })

    ]
    readonly_fields = ['created_at', 'get_notification_preference', ]

    def suspend_eater(self, request, queryset):
        queryset.update(status=enums.SUSPEND)
        self.message_user(request, 'Users suspended')

    def last_order(self, obj):
        order = obj.purchases.all().last()
        if order:
            return order.created_at
        return None

    def total_spent(self, obj):
        return obj.total_spent

    total_spent.admin_order_field = 'total_spent'

    def total_transactions(self, obj):
        return obj.total_transactions  # Field not in model

    def total_reviews(self, obj):
        return obj.total_reviews  # Field not in total

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            total_transactions=Count('purchases'),
            total_reviews=Count('purchases__rating'),
            total_spent=Sum('purchases__amount')
        )

    def search_terms(self, obj):
        try:
            return obj.search.all().first().word
        except Exception as e:
            return None

    def last_location(self, obj):

        location = obj.location
        try:
            if location:
                return "{},{}".format(location.x, location.y)
        except Exception as e:
            return None
        return None

    def review_notifications(self, obj):
        try:
            return obj.notification_preference.review
        except AttributeError:
            return False

    review_notifications.boolean = True

    def marketing_notifications(self, obj):
        try:
            return obj.notification_preference.marketing
        except AttributeError:
            return False

    marketing_notifications.boolean = True

    def get_notification_preference(self, obj):
        return _render(obj, 'admin/eater/notification_preference.html')

    get_notification_preference.short_description = 'Notification Preference'

    formfield_overrides = {
        models.PointField: {'widget': Textarea}
    }


admin.site.register(Eater, EaterAdmin)
