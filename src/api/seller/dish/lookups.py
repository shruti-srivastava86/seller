from ajax_select import register, LookupChannel

from seller.dish.models import Allergens, Cuisine


@register('allergens')
class AllergenChannel(LookupChannel):
    model = Allergens

    def get_query(self, q, request):
        return Allergens.objects.filter(name__icontains=q)

    def format_item_display(self, obj):
        return obj.name

    def format_match(self, obj):
        return obj.name


@register('cuisines')
class CuisineChannel(LookupChannel):
    model = Cuisine

    def get_query(self, q, request):
        return Cuisine.objects.filter(name__icontains=q)

    def format_item_display(self, obj):
        return obj.name

    def format_match(self, obj):
        return obj.name
