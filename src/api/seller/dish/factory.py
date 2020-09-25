from decimal import Decimal

import factory

from seller.dish.models import (
    Dish,
    Dietary,
    Allergens,
    Cuisine)
from seller.vendor.factory import BusinessFactory


class DietaryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Dietary

    name = factory.Sequence(lambda n: 'Dietary #{}'.format(n))


class CuisineFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Cuisine

    name = factory.Sequence(lambda n: 'Cuisine #{}'.format(n))


class AllergensFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Allergens

    name = factory.Sequence(lambda n: 'Allergen #{}'.format(n))


class DishFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Dish

    name = factory.Faker('name')
    price = Decimal(10.00)
    business = factory.SubFactory(BusinessFactory)

    @factory.post_generation
    def dietary_information(self, create, extracted, **kwargs):
        if not create:
            return
        if extracted:
            for dietary_information_obj in extracted:
                self.dietary_information.add(dietary_information_obj)
