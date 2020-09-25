from django.conf.urls import url

from seller.dish.api import (
    DishListView,
    DietaryListView,
    CuisinesListView,
    AllergenListView
)

dish_mobile_urls = [
    url(r'^$', DishListView.as_view(), name="dish"),
    url(r'^dietary/$', DietaryListView.as_view(), name="dietary"),
    url(r'^cuisines/$', CuisinesListView.as_view(), name="cuisines"),
    url(r'^allergens/$', AllergenListView.as_view(), name="allergens"),
]
