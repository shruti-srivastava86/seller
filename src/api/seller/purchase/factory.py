"""
Created by Shruti on 28,August,2018
"""
import factory

from seller.eater.factory import EaterUserFactory
from seller.purchase.models import (
    PurchaseItem,
    Purchase,

)
from seller.vendor.factory import VendorUserFactory


class PurchaseFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Purchase

    eater = factory.SubFactory(EaterUserFactory)
    vendor = factory.SubFactory(VendorUserFactory)


class PurchaseItemFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = PurchaseItem
