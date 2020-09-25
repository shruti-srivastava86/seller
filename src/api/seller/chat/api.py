from django.db.models import OuterRef, Q
from django.shortcuts import get_object_or_404
from rest_framework.generics import (
    ListCreateAPIView,
)
from rest_framework.response import Response
from rest_framework.views import APIView

from api.generics.generics import (
    DualSerializerCreateUpdateAPIView,
    DualSerializerCreateUpdateDeleteAPIView
)
from seller.chat.enums import NEW_MESSAGES, OLD_MESSAGES, CHAT_TYPES
from seller.chat.models import Message, Conversation
from seller.chat.serializers import (
    ConversationSerializer,
    CreateConversationSerializers,
    MessageSerializer,
    ConversationDeatils)
from seller.vendor.utils import unread_count, unread_count_conversation


class ConversationList(ListCreateAPIView, DualSerializerCreateUpdateAPIView):
    """
        For creating a new conversation and fetching all conversations
    """
    serializer_class = ConversationSerializer
    request_serializer_class = CreateConversationSerializers
    response_serializer_class = CreateConversationSerializers

    def get_queryset(self):
        user = self.request.user
        chat_type = self.request.GET.get('chat_type')
        subquery = Message.objects.with_prefetch() \
            .for_conversation(OuterRef('pk')) \
            .unread(user) \
            .values('id')
        queryset = Conversation.objects.for_user(user) \
            .with_chat_type(chat_type) \
            .select_related('initiator') \
            .prefetch_related('users') \
            .prefetch_related('conversation_messages') \
            .prefetch_related('conversation_messages__read_by') \
            .prefetch_related('conversation_messages__user') \
            .with_messages() \
            .with_last_message_time() \
            .with_unread_message_count(subquery) \
            .order_by('-last_message_sent', '-created_at', '-unread', )
        return queryset


class ConversationListDetails(ListCreateAPIView):
    """
        For creating a new conversation and fetching all conversations
    """
    serializer_class = ConversationDeatils

    def get_queryset(self):
        user = self.request.user
        data = []
        for x in CHAT_TYPES:
            temp = {'chat_type': x[0],
                    'chat_name': x[1],
                    'unread_count': unread_count_conversation(user, x[0])}
            data.append(temp)
        return data


class MessageList(DualSerializerCreateUpdateDeleteAPIView):
    """
        For creating new message and fetching all messages in conversations
    """
    serializer_class = MessageSerializer
    request_serializer_class = serializer_class
    response_serializer_class = serializer_class

    pagination_count = 10

    def get(self, request, *args, **kwargs):
        message_ordering = int(self.request.query_params.get('message_ordering', NEW_MESSAGES))
        message_id = self.request.query_params.get('message_id', None)
        conversation_id = self.kwargs.get('pk', None)
        conversation = get_object_or_404(Conversation, pk=conversation_id)

        messages = Message.objects.for_conversation(conversation) \
            .with_prefetch() \
            .select_related('conversation')

        user = self.request.user

        for message in messages.filter(~Q(read_by__in=[user])):
            message = message.mark_read_for_user(user)

        if message_id is None:
            messages = messages.order_by('-id')[:self.pagination_count]
        elif message_ordering == NEW_MESSAGES:
            messages = messages.after_message_id(message_id).order_by('id')[:self.pagination_count]
        elif message_ordering == OLD_MESSAGES:
            messages = messages.before_message_id(message_id).order_by('-id')[:self.pagination_count]

        if message_ordering == OLD_MESSAGES:
            messages = reversed(messages)

        return Response(self.serializer_class(messages, many=True).data)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['conversation'] = self.kwargs.get('pk', None)
        return context

    def get_object(self):
        conversation_id = self.kwargs.get('pk', None)
        conversation = get_object_or_404(Conversation, pk=conversation_id)
        return Message.objects.for_conversation(conversation) \
            .with_prefetch() \
            .select_related('conversation').order_by('-created_at')[0]


class UnreadMessages(APIView):

    def get(self, request, *args, **kwargs):
        return Response({'unread': unread_count(self.request.user)})
