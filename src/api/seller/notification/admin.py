from django.contrib import admin

from seller.notification.models import VendorPreference, Notifications, EmailTemplate

admin.site.register(VendorPreference)
admin.site.register(Notifications)


@admin.register(EmailTemplate)
class ETAdmin(admin.ModelAdmin):
    list_display = ['type', 'content', ]
