from django.contrib import admin

from seller.dish.models import (
    Dish,
    Allergens,
    Cuisine,
    Dietary
)
from seller.utils import ExportCsvMixin


class DishAdmin(admin.ModelAdmin, ExportCsvMixin):
    list_display = [
        'id',
        'name',
        'business',
        'price',
        'temporary_price',
        'serial_id',
        'active',
        'special',
        'deleted'
    ]
    list_filter = ['name', 'active', 'special', 'deleted']
    search_fields = ['name']
    actions = ['export_as_csv']


class AllergensAdmin(admin.ModelAdmin, ExportCsvMixin):
    list_display = ['name']
    search_fields = ['name']
    actions = ['export_as_csv']


class CuisineAdmin(admin.ModelAdmin, ExportCsvMixin):
    list_display = ['name']
    search_fields = ['name']
    actions = ['export_as_csv']


class DietaryAdmin(admin.ModelAdmin, ExportCsvMixin):
    list_display = ['name']
    search_fields = ['name']
    actions = ['export_as_csv']


admin.site.register(Dish, DishAdmin)
admin.site.register(Allergens, AllergensAdmin)
admin.site.register(Cuisine, CuisineAdmin)
admin.site.register(Dietary, DietaryAdmin)
