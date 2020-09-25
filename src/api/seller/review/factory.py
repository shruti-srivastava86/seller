"""
Created by Shruti on 25,August,2018
"""
import factory
from seller.review.models import Rating
from seller.purchase.factory import PurchaseFactory


class RatingFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Rating
    purchase = PurchaseFactory
