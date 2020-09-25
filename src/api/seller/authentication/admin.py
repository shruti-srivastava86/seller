from django.contrib import admin

from seller.authentication.models import Token


@admin.register(Token)
class TokenAdmin(admin.ModelAdmin):
    list_display = ['key', 'user', ]
    raw_id_fields = ['user', ]
