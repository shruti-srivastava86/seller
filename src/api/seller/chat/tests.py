from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from seller.vendor.factory import VendorUserFactory, BusinessFactory
from seller.chat.factory import ConversationFactory, MessageFactory
from seller.chat import enums


class ChatApiTest(APITestCase):
    def setUp(self):
        self.vendor = VendorUserFactory()
        BusinessFactory(vendor=self.vendor)
        self.conversation = ConversationFactory()
        self.conversation.initiator = self.vendor
        self.conversation.chat_type = enums.SUPPORT
        self.conversation.save()
        self.message = MessageFactory()
        self.message.conversation = self.conversation
        self.message.save()
        self.client.force_authenticate(user=self.vendor)

    def test_vendor_chat_conversation(self):
        """
            Test for retreival of conversation mobile
        :return:
        """
        self.url = reverse("seller.mobile.vendor:chats")
        response = self.client.get(self.url, {"chat_type": enums.SUPPORT})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        if 'results' in response.data:
            data = response.data['results'][0]
            self.assertTrue('id' in data)
            self.assertTrue('initiator' in data)
            self.assertTrue('last_message_text' in data)
            self.assertTrue('title' in data)
            self.assertTrue('chat_type' in data)

    def test_vendor_chat_messages(self):
        """
            Test for creating and fetching messages in conversation mobile
        :return:
        """

        self.url = reverse("seller.mobile.vendor:messages", kwargs={'pk': self.conversation.id})
        self.message = "message"
        response = self.client.post(self.url, {"message": self.message})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data[0]
        self.assertEqual(data.get('message'), self.message)
        self.assertTrue('id' in data)
        self.assertTrue('image' in data)
        self.assertTrue('conversation' in data)
        self.assertTrue('read_by' in data)

    def test_vendor_web_chat_conversation(self):
        """
            Test for retreival of conversation web
        :return:
        """
        self.url = reverse("seller.web.vendor:chats")
        response = self.client.get(self.url, {"chat_type": enums.SUPPORT})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        if 'results' in response.data:
            data = response.data['results'][0]
            self.assertTrue('id' in data)
            self.assertTrue('initiator' in data)
            self.assertTrue('last_message_text' in data)
            self.assertTrue('title' in data)
            self.assertTrue('chat_type' in data)

    def test_vendor_web_chat_messages(self):
        """
            Test for creating and fetching messages in conversation web
        :return:
        """

        self.url = reverse("seller.web.vendor:messages", kwargs={'pk': self.conversation.id})
        self.message = "message"
        response = self.client.post(self.url, {"message": self.message})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data[0]
        self.assertEqual(data.get('message'), self.message)
        self.assertTrue('id' in data)
        self.assertTrue('image' in data)
        self.assertTrue('conversation' in data)
        self.assertTrue('read_by' in data)

    def test_vendor_chat_unread(self):
        """
            Test for vendor unread messages mobile
        :return:
        """
        self.url = reverse("seller.mobile.vendor:unread")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue("unread" in response.data)

    def test_vendor_chat_details(self):
        """
            Test for vendor chat details mobile
        :return:
        """
        self.url = reverse("seller.mobile.vendor:chat_details")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        if 'results' in response.data:
            data = response.data['results'][0]
            self.assertTrue("unread_count" in data)
            self.assertTrue("chat_type" in data)
            self.assertTrue("chat_name" in data)

    def test_vendor_web_chat_unread(self):
        """
            Test for vendor unread messages web
        :return:
        """
        self.url = reverse("seller.web.vendor:unread")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue("unread" in response.data)

    def test_vendor_web_chat_details(self):
        """
            Test for vendor chat details web
        :return:
        """
        self.url = reverse("seller.web.vendor:chat_details")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue("unread" in response.data)
