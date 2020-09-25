import factory
from seller.vendor.factory import VendorUserFactory
from seller.chat.models import Conversation, Message


class ConversationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Conversation

    title = factory.Faker('name')
    initiator = factory.SubFactory(VendorUserFactory)

    @factory.post_generation
    def users(self, create, extracted, **kwargs):
        if not create:
            return
        if extracted:
            for user in extracted:
                self.users.add(user)


class MessageFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Message

    message = factory.Faker('name')
    conversation = factory.SubFactory(ConversationFactory)
    user = factory.SubFactory(VendorUserFactory)

    @factory.post_generation
    def read_by(self, create, extracted, **kwargs):
        if not create:
            return
        if extracted:
            for user in extracted:
                self.users.add(user)
