from datetime import datetime

from django.contrib import admin
from django.contrib.gis.db import models
from django.contrib.auth.admin import UserAdmin as DUserAdmin
from django.contrib.auth.forms import UserCreationForm as DUserCreationForm
from django.core.exceptions import ValidationError
from django.forms import Textarea, ModelForm, Form, IntegerField
from django.contrib.admin.views.decorators import staff_member_required
from django.conf.urls import url
from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic import FormView

from seller.user import enums
from seller.user.models import (
    User,
    ForgotPassword,
    Transaction,
    GeneralSettings,
    ReportVendorList,
    ReportVendor,
    TransactionLogView,
    SearchTerms
)
from seller.utils import ExportCsvMixin


class AmendLoyaltyPointsForm(Form):
    points = IntegerField(label='New Points Balance')


class AmendLoyaltyPointsView(FormView):
    form_class = AmendLoyaltyPointsForm
    template_name = 'admin/amend_loyalty.html'

    def get_context_data(self, **kwargs):
        cd = super().get_context_data(**kwargs)
        cd['user'] = User.objects.get(pk=self.kwargs['user_id'])
        return cd

    def form_valid(self, form):
        points = int(form.cleaned_data['points'])
        amount = -1
        type = None
        user = User.objects.get(pk=self.kwargs['user_id'])
        notes = 'Admin Loyalty Point Adjustment on {} by {}'.format(
            str(datetime.now()), str(self.request.user))
        if user.coins > points:
            amount = user.coins - points
            type = enums.DEBIT
        elif user.coins < points:
            amount = points - user.coins
            type = enums.CREDIT
        if amount != -1:
            Transaction.objects.create(
                type=type,
                coins=amount,
                reason=enums.ADMIN_POINTS,
                status=enums.SUCCESS,
                balance=points,
                user=user,
                note=notes)
        user.coins = points
        user.save()
        if user.user_type == enums.EATER:
            return redirect(reverse(
                'admin:eater_eater_change', args=[user.pk]))
        elif user.user_type == enums.VENDOR:
            return redirect(reverse(
                'admin:vendor_vendor_change', args=[user.pk]))


class UserCreationForm(DUserCreationForm):
    class Meta:
        model = User
        fields = ('email', )


class UserAdmin(DUserAdmin):
    list_display = ['id', 'name', 'email', 'coins', 'is_active', 'user_type']
    list_filter = ['is_active', 'user_type']
    search_fields = ['name', 'email']
    formfield_overrides = {
        models.PointField: {'widget': Textarea}
    }
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2'),
        }),
    )
    add_form = UserCreationForm
    ordering = ['id']
    fieldsets = None

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            url(r'^(?P<user_id>.+)/amend_loyalty/$',
                staff_member_required(AmendLoyaltyPointsView.as_view()),
                name='amend_loyalty_points'),
        ]
        return my_urls + urls


class TransactionForm(ModelForm):

    def clean(self):
        data = self.cleaned_data
        if self.cleaned_data['user'].user_type != enums.VENDOR:
            raise ValidationError("Not a valid vendor")

        if self.cleaned_data['user'].coins < self.cleaned_data['coins']:
            raise ValidationError("Sufficient coins are not avaliable")

        return data

    class Meta:
        model = Transaction
        fields = ['user', 'coins', 'purchase', 'amount', 'balance', 'type', 'reason', 'status', 'note']


class TransactionAdmin(admin.ModelAdmin, ExportCsvMixin):
    search_fields = ['user__email']
    raw_id_fields = ['user', 'purchase', ]
    list_display = [
        'id', 'created_at', 'user', 'coins', 'amount', 'balance', 'type', 'reason', 'status', 'qr_id', ]
    list_filter = ['type', 'reason', 'status']
    ordering = ['-created_at']
    actions = ['export_as_csv']
    form = TransactionForm
    autocomplete_lookup_fields = {
        'fk': ['user'],
    }

    def save_model(self, request, obj, form, change):
        user = obj.user
        user.coins = user.coins - obj.coins
        user.save()
        obj.amount = GeneralSettings.objects.get_convert_to_pounds(obj.coins)
        obj.balance = user.coins
        obj.type = enums.DEBIT
        obj.reason = enums.VENDOR_REDEEMED
        obj.status = enums.SUCCESS
        obj.note = "Points redeemed by vendor"
        super().save_model(request, obj, form, change)

    def lookup_allowed(self, key, value):
        if key in ['purchase__vendor', 'purchase__eater']:
            return True
        return super().lookup_allowed(key, value)


@admin.register(TransactionLogView)
class TransactionLogAdmin(admin.ModelAdmin, ExportCsvMixin):
    actions = ['export_as_csv']
    list_display = [
        'created_at',
        'debit_id',
        'debit_amount',
        'debit_reason',
        'debit_user',
        'credit_id',
        'credit_amount',
        'credit_reason',
        'credit_user',
    ]
    list_select_related = ['credit_user', 'debit_user', ]
    change_list_template = 'admin/transaction/list.html'
    raw_id_fields = ['debit', 'credit', 'debit_user', 'credit_user', ]

    def get_actions(self, request):
        return []


class GeneralSettingsAdmin(admin.ModelAdmin):
    list_display = ['search_radius_in_miles',
                    'incomplete_profile_email_reminder_days',
                    'one_coin_to_pounds',
                    'minimum_coins_redeemable',
                    'maximum_coins_redeemable',
                    'coins_incremental_value',
                    'scan_qr_points',
                    'review_points',
                    'eater_review_reminder',
                    'dietary_preference',
                    'minimum_reviews_vendor']
    change_list_template = 'admin/general_settings_list.html'


class ReportVendorListAdmin(admin.ModelAdmin):
    list_display = ['name']


class ReportVendorAdmin(admin.ModelAdmin, ExportCsvMixin):
    search_fields = ['vendor__name', 'report__name']
    list_display = [
        'vendor_name', 'eater', 'report', 'message',
        'processed', ]
    list_filter = ['vendor', 'report', 'processed', ]
    actions = ['export_as_csv', 'process_reports']
    raw_id_fields = ['vendor', 'eater', ]
    list_select_related = ['vendor__business', 'eater', ]

    def process_reports(self, request, queryset):
        queryset.update(processed=True)

    def vendor_name(self, obj):
        return obj.vendor.business.name


admin.site.register(User, UserAdmin)
admin.site.register(ForgotPassword)
admin.site.register(Transaction, TransactionAdmin)
admin.site.register(GeneralSettings, GeneralSettingsAdmin)
admin.site.register(ReportVendorList, ReportVendorListAdmin)
admin.site.register(ReportVendor, ReportVendorAdmin)
admin.site.register(SearchTerms)
