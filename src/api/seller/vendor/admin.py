from datetime import datetime

from django.conf.urls import url
from django.contrib import admin, messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.gis.db import models
from django.contrib.auth.forms import UserChangeForm
from django.contrib.auth.admin import UserAdmin
from django.forms import Textarea
from django import forms
from django.db.models import Count, Avg, Exists, OuterRef
from django.http import Http404
from django.shortcuts import render, redirect
from django.views.generic import View

from django.utils.safestring import mark_safe

from ajax_select.fields import AutoCompleteSelectMultipleField

from seller.utils import ExportCsvMixin
from seller.vendor import enums
from seller.vendor.models import (
    Vendor,
    Business,
    Image,
    OpeningHours,
    Market,
    BusinessCheckinCheckout,
    VendorProfileViews
)
from seller.vendor.utils import send_account_approved_email, send_account_rejected_email
from seller.dish.models import Dish
from seller.user.models import Transaction
from seller.user.enums import DEBIT, CREDIT, ADMIN_POINTS, SUCCESS


class BusinessAdmin(admin.ModelAdmin, ExportCsvMixin):
    list_display = ['id', 'name', 'vendor', 'cash', 'card', 'open', 'check_out']
    list_filter = ['open', 'vendor__is_active']
    search_fields = ['name', 'vendor__name', 'vendor__email']
    actions = ['export_as_csv']
    raw_id_fields = ['vendor', 'home_market', 'cuisine', 'allergens', 'photos', ]


def _render(obj, template, context=None):
    return mark_safe(render(None, template, {
        'business': obj,
    }).content.decode('utf-8'))


class BAInlineForm(forms.ModelForm):
    class Meta:
        model = Business
        exclude = ['photos', 'social_links', ]

    home_market = AutoCompleteSelectMultipleField('markets', required=False)
    allergens = AutoCompleteSelectMultipleField('allergens', required=False)
    cuisine = AutoCompleteSelectMultipleField('cuisines')


class VendorActionView(View):
    """View to action things about a vendor. Only used in a post situation
    """
    def success(self, msg):
        messages.success(self.request, msg)
        return redirect('../change/')

    def post(self, request, user_id):
        v = Vendor.objects.get(pk=user_id)
        action = request.POST.get('action')
        if action == 'approved':
            v.status = enums.APPROVED
            v.save()
            send_account_approved_email([v])
            return self.success('Vendor approved. An email was sent to the vendor')
        elif action == 'reject':
            v.status = enums.REJECTED
            v.save()
            send_account_rejected_email([v])
            return self.success('Vendor rejected. An email was sent to the vendor')
        elif action == 'suspend':
            v.status = enums.SUSPENDED
            v.save()
            return self.success('Vendor Suspended. No email was sent')
        else:
            raise ValueError('{} is not a valid action'.format(action))


class BAInline(admin.StackedInline):
    model = Business
    suit_classes = 'suit-tab suit-tab-general'
    readonly_fields = ['opening_hours', 'images', 'get_social_links', ]
    form = BAInlineForm

    def opening_hours(self, obj):
        # Render data out to template
        return _render(obj, 'admin/vendor/opening_hours.html')

    def images(self, obj):
        # Render data out to template
        return _render(obj, 'admin/vendor/photos.html')

    def get_social_links(self, obj):
        return _render(obj, 'admin/vendor/social_links.html')

    get_social_links.short_description = 'Social Links'


class VendorAdmin(UserAdmin):
    list_display = [
        'id', 'status', 'name', 'business_name', 'email', 'created_at', 'home_market', 'open',
        'specials_on',
        'is_active', 'uuid', 'chalkboard_on', 'discount_on', 'coins', 'total_transactions',
        'total_reviews', 'average_rating',
        'checkin_reminders_on', 'marketing_messages_on',
        'support_messages_on', 'time_offset']
    list_filter = ['status', 'is_active']
    list_select_related = ['business', 'notification_preference', ]
    search_fields = ['name', 'email', 'business__name', ]
    formfield_overrides = {
        models.PointField: {'widget': Textarea}
    }
    inlines = [BAInline, ]
    actions = [
        'approve_vendor',
        'reject_vendor',
        'suspend_vendor',
        'activate_vendor',
        'delete_vendor',
        'set_loyalty_points'
    ]
    readonly_fields = ['get_notification_preference', 'devices', 'status', ]

    form = UserChangeForm
    suit_form_tabs = (
        ('general', 'General Information'),
        ('menu', 'Menu'),
    )
    suit_form_includes = (
        ('admin/vendor/stats.html', 'top', 'general'),
        ('admin/vendor/menu.html', 'top', 'menu'),
    )
    change_list_template = 'admin/vendor/list.html'

    # Override UserAdmin
    ordering = ['id', ]
    fieldsets = [
        ('General', {
            'classes': ('suit-tab', 'suit-tab-general',),
            'fields': [
                'name', 'email', 'password', 'location',
                'devices', 'address', 'status', 'onboarding_stage',
                'get_notification_preference', 'notes',
            ]})
    ]

    def set_loyalty_points(self, request, queryset):
        points = request.POST.get('points')
        if not points:
            raise Http404('No points')
        points = int(points)

        trans = []
        notes = 'Admin Loyalty Point Adjustment on {} by {}'.format(
            str(datetime.now()), str(request.user))
        for vendor in queryset:
            amount = -1
            type = None
            if vendor.coins > points:
                amount = vendor.coins - points
                type = DEBIT
            elif vendor.coins < points:
                amount = points - vendor.coins
                type = CREDIT
            else:
                continue
            trans.append(Transaction(
                type=type,
                coins=amount,
                reason=ADMIN_POINTS,
                status=SUCCESS,
                balance=points,
                user=vendor,
                note=notes))
        # Update all cached balances
        queryset.update(coins=points)
        Transaction.objects.bulk_create(trans)
        self.message_user(request, "Points set for selected vendors")

    def open(self, obj):
        return obj.business.open

    open.boolean = True

    def marketing_messages_on(self, obj):
        if not obj.notification_preference_id:
            return False
        return obj.notification_preference.marketing

    marketing_messages_on.boolean = True

    def checkin_reminders_on(self, obj):
        if not obj.notification_preference_id:
            return False
        return obj.notification_preference.checkin_checkout

    checkin_reminders_on.boolean = True

    def support_messages_on(self, obj):
        if not obj.notification_preference_id:
            return False
        return obj.notification_preference.support

    support_messages_on.boolean = True

    def chalkboard_on(self, obj):
        return obj.business.offer_active

    chalkboard_on.boolean = True

    def discount_on(self, obj):
        return obj.business.discount_active

    discount_on.boolean = True

    def home_market(self, obj):
        r = [str(h) for h in obj.business.home_market.all()]
        if len(r) == 0:
            return "None"
        return r

    def total_transactions(self, obj):
        return obj.total_transactions  # Not normally a field

    def average_rating(self, obj):
        try:
            return "{0:.2f}".format(obj.average_rating)  # Not normally a field
        except TypeError:
            return "N/A"

    def business_name(self, obj):
        return obj.business.name

    def total_reviews(self, obj):
        return obj.total_reviews  # Not normally a field

    def approve_vendor(self, request, queryset):
        queryset.update(status=enums.APPROVED, is_active=True)
        send_account_approved_email(queryset)
        self.message_user(request, 'Selected vendors have been approved and emails sent to them')

    def reject_vendor(self, request, queryset):
        queryset.update(status=enums.REJECTED)
        send_account_rejected_email(queryset)
        self.message_user(request, 'Selected vendors have been rejected and emails sent to them')

    def suspend_vendor(self, request, queryset):
        queryset.update(status=enums.SUSPENDED, is_active=False)
        self.message_user(request, 'Selected vendors have been marked as suspended')

    def delete_vendor(self, request, queryset):
        queryset.update(status=enums.DELETE, is_active=False)
        self.message_user(request, 'Selected vendors have been marked as deleted')

    def activate_vendor(self, request, queryset):
        queryset.update(status=enums.APPROVED, is_active=True)
        self.message_user(request, 'Selected vendors have been marked as approved (no email sent)')

    approve_vendor.short_description = "Approve selected Vendors"
    reject_vendor.short_description = "Reject selected Vendors"
    suspend_vendor.short_description = "Set selected Vendors as suspended"
    activate_vendor.short_description = "Set selected Vendors as activated without email"
    delete_vendor.short_description = "Set selected vendors to deleted"

    def specials_on(self, obj):
        return obj.specials_on

    specials_on.boolean = True

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            total_transactions=Count('purchases'),
            total_reviews=Count('purchases__rating'),
            average_rating=Avg('purchases__rating__overall_rating'),
            specials_on=Exists(Dish.objects.filter(
                special=True, business__vendor=OuterRef('pk'))))

    def get_notification_preference(self, obj):
        return _render(obj, 'admin/vendor/notification_preference.html')

    get_notification_preference.short_description = 'Notification Preference'

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            url(r'^(?P<user_id>.+)/action_vendor/$',
                staff_member_required(VendorActionView.as_view()),
                name='action-vendor'),
        ]
        return my_urls + urls


class OpeningHoursAdmin(admin.ModelAdmin, ExportCsvMixin):
    list_filter = ['business__name', 'open']
    actions = ['export_as_csv']


admin.site.register(Vendor, VendorAdmin)
admin.site.register(Business, BusinessAdmin)
admin.site.register(Image)
admin.site.register(OpeningHours, OpeningHoursAdmin)
admin.site.register(Market)
admin.site.register(BusinessCheckinCheckout)
admin.site.register(VendorProfileViews)
