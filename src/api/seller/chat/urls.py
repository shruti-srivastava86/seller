from django.conf.urls import url

from seller.chat.api import ConversationList

chat_mobile_urls = [
    url(r'^$', ConversationList.as_view(), name='retrieve_delete'),


]
