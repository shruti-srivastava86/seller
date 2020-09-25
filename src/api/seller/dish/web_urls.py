from django.conf.urls import url

from seller.dish.api import (
    DishListView,
    DietaryListView,
    WebCuisinesListView,
    WebAllergenListView
)

dish_web_urls = [
    url(r'^$', DishListView.as_view(), name="dish"),
    url(r'^dietary/$', DietaryListView.as_view(), name="dietary"),
    url(r'^cuisines/$', WebCuisinesListView.as_view(), name="cuisines"),
    url(r'^allergens/$', WebAllergenListView.as_view(), name="allergens"),
]
