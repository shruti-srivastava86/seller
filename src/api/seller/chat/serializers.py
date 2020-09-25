from rest_framework import serializers

from api.generics.generics import CustomModelSerializer
from seller.chat.models import Conversation, Message
from seller.notification.utils import send_message_to_devices
from seller.user import enums
from seller.user.models import User
from seller.user.serializers import VendorSerializer
from seller.vendor.utils import unread_count


def send_notifications(message, user):
    data = {
        "type": message.conversation.chat_type,
        "id": message.conversation.id,
        "title": message.conversation.title,
        "subtitle": message.conversation.title,
    }
    if user in message.conversation.users.all():
        unread = unread_count(message.conversation.initiator)
        send_message_to_devices(
            message.conversation.initiator.user_type,
            message.conversation.initiator.devices.all(),
            message.message,
            data,
            unread

        )
    else:
        for notify_user in message.conversation.users.all():
            unread = unread_count(notify_user)
            send_message_to_devices(
                notify_user.user_type,
                notify_user.devices.all(),
                message.message,
                data,
                unread

            )


class ConversationSerializer(serializers.ModelSerializer):
    """
        Model serializer for a Conversation object
    """

    last_message_text = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()
    last_message_date = serializers.SerializerMethodField()
    initiator = VendorSerializer()
    users = VendorSerializer(many=True)
    business_name = serializers.SerializerMethodField()

    def get_unread_count(
            self, obj):
        user = self.context.get('request').user
        return obj.conversation_messages.unread(user).count()

    def get_last_message_text(self, obj):
        last_message = obj.conversation_messages.all().first()
        if last_message:
            return last_message.message
        return None

    def get_last_message_date(self, obj):
        last_message = obj.conversation_messages.all().first()
        if last_message:
            return last_message.created_at
        return None

    def get_business_name(self, obj):
        if obj.initiator.user_type == enums.VENDOR:
            return obj.initiator.vendor.business.name
        else:
            return obj.users.all().first().vendor.business.name

    class Meta:
        model = Conversation
        fields = [
            'id',
            'initiator',
            'complete',
            'last_message_text',
            'title',
            'created_at',
            'chat_type',
            'unread_count',
            'last_message_date',
            'users',
            'business_name'
        ]


class MessageConversationSerializier(serializers.ModelSerializer):
    class Meta:
        model = Conversation
        fields = ['id']


class MessageSerializer(serializers.ModelSerializer):
    """
        Model Serializer for storing,retrieving and updating Messaging object
    """
    image = serializers.CharField(required=False)
    conversation = MessageConversationSerializier(required=False)

    def validate(self, attrs):
        if not self.partial:
            attrs.pop('read_by', None)
        return attrs

    def validate_image(self, obj):
        if obj:
            return "chat/" + obj.split('/')[-1]
        return None

    def create(self, validated_data):
        user = self.context.get('request').user
        validated_data['conversation_id'] = int(self.context.get('conversation'))
        validated_data['user'] = user
        message = Message.objects.create(**validated_data)
        send_notifications(message, user)

        return message

    def update(self, instance, validated_data):
        instance.mark_read_for_user(*validated_data.get('read_by'))
        return instance

    class Meta:
        model = Message
        extra_kwargs = {'conversation': {'required': False}}
        fields = '__all__'


class CreateConversationSerializers(CustomModelSerializer):

    def create_message(self, conversation):
        message = Message()
        message.user = self.context.get('request').user
        message.message = self.initial_data.get('message', None)
        image = self.initial_data.get('image', None)
        if image:
            message.image = "chat/" + image.split('/')[-1]
        message.conversation = conversation
        message.save()
        return message

    def create(self, validated_data):
        conversation = Conversation()
        conversation.initiator = self.context.get('request').user
        conversation.title = validated_data.get('title')
        conversation.chat_type = validated_data.get('chat_type')
        conversation.save()
        conversation.users.add(*User.objects.filter(is_superuser=True))
        self.create_message(conversation)
        return conversation

    class Meta:
        model = Conversation
        extra_kwargs = {'users': {'required': False}}
        exclude = [
            'initiator',

        ]


class ConversationDeatils(serializers.Serializer):
    chat_type = serializers.IntegerField()
    unread_count = serializers.IntegerField()
    chat_name = serializers.CharField()
