import factory

from seller.user import enums
from seller.user.factory import BaseUserFactory
from seller.vendor import enums as vendor_enums
from seller.vendor.models import (
    Vendor,
    Business,
    Image,
    Market
)


class VendorUserFactory(BaseUserFactory):
    """
        Factory for creating a Vendor user.
    """

    class Meta:
        model = Vendor

    user_type = enums.VENDOR
    status = vendor_enums.APPROVED


class ImageFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Image


class BusinessFactory(factory.django.DjangoModelFactory):
    """
        Factory for creating a Business for a vendor.
    """

    class Meta:
        model = Business

    name = factory.Faker('name')
    vendor = factory.SubFactory(VendorUserFactory)
    social_links = {"facebook": "abc"}
    ingredients = ["salt, pepper"]

    @factory.post_generation
    def cuisine(self, create, extracted, **kwargs):
        if not create:
            return
        if extracted:
            for cuisine in extracted:
                self.cuisine.add(cuisine)

    @factory.post_generation
    def allergens(self, create, extracted, **kwargs):
        if not create:
            return
        if extracted:
            for allergen in extracted:
                self.allergens.add(allergen)

    @factory.post_generation
    def photos(self, create, extracted, **kwargs):
        if not create:
            return
        if extracted:
            for photos in extracted:
                self.photos.add(photos)


class MarketFactory(factory.django.DjangoModelFactory):
    """
        Factory for creating markets
    """

    class Meta:
        model = Market

    name = factory.Sequence(lambda n: 'Market #{}'.format(n))
