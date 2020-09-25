from django.conf.urls import url

from seller.authentication.api import (
    VendorLoginView,
    LogoutView,
    ChangePasswordView,
    ForgotPasswordView,
    DeleteView,
)
from seller.authentication.views import ForgotPasswordTemplateView
from seller.chat.api import (
    ConversationList,
    MessageList,
    UnreadMessages, ConversationListDetails)
from seller.dish.api import (
    VendorListCreateDishView,
    VendorDishRetrieveUpdateDeleteView
)
from seller.notification.api import (
    DeviceRegister,
    DeviceUnregister,
    VendorPreferences,
    TestNotification
)
from seller.review.api import VendorRatingListView
from seller.vendor.api import (
    VendorSignUpView,
    VendorCheckIn,
    VendorCheckOut,
    VendorProfileView,
    VendorTransactionListCreateView,
    VendorNotificationsView)
from seller.vendor.web_api import WebMarketListView

vendor_mobile_auth_urls = [
    url(r'^login/$', VendorLoginView.as_view(), name='login'),
    url(r'^sign_up/$', VendorSignUpView.as_view(), name='sign_up'),
    url(r'^logout/$', LogoutView.as_view(), name='logout'),
    url(r'^delete/$', DeleteView.as_view(), name='delete'),
    url(r'^change_password/$', ChangePasswordView.as_view(), name='change_password'),
    url(r'^forgot_password/$', ForgotPasswordView.as_view(), name='forgot_password_email'),
    url(r'^forgot_password/(?P<token>.+)/$', ForgotPasswordTemplateView.as_view(), name='forgot_password'),
]

vendor_mobile_profile_urls = [
    url(r'^profile/$', VendorProfileView.as_view(), name='profile'),
    url(r'^checkin/$', VendorCheckIn.as_view(), name='checkin'),
    url(r'^checkout/$', VendorCheckOut.as_view(), name='checkout'),
    url(r'^transaction/$', VendorTransactionListCreateView.as_view(), name='transaction'),
]

vendor_mobile_dish_urls = [
    url(r'^dish/$', VendorListCreateDishView.as_view(), name='dishes'),
    url(r'^dish/(?P<pk>[0-9]+)/$', VendorDishRetrieveUpdateDeleteView.as_view(), name='dish'),
]

vendor_mobile_chat_urls = [
    url(r'^chat/$', ConversationList.as_view(), name='chats'),
    url(r'^chat/details/$', ConversationListDetails.as_view(), name='chat_details'),
    url(r'^chat/(?P<pk>[0-9]+)/messages/$', MessageList.as_view(), name='messages'),
    url(r'^chat/unread/$', UnreadMessages.as_view(), name="unread"),

]

vendor_mobile_review_urls = [
    url(r'^rating/$', VendorRatingListView.as_view(), name='ratings'),
]

vendor_mobile_market_urls = [
    url(r'^markets/$', WebMarketListView.as_view(), name="markets"),

]

vendor_mobile_notification_urls = [
    url(r'^notifications/$', VendorNotificationsView.as_view(), name="notifications"),
    url(r'^device_register/$', DeviceRegister.as_view(), name="register_device"),
    url(r'^device_unregister/$', DeviceUnregister.as_view(), name="unregister_device"),
    url(r'^notification_preference/$', VendorPreferences.as_view(), name="notification_preference"),
    url(r'^test_notification/$', TestNotification.as_view(), name="test_notification"),
]

vendor_mobile_reward_urls = [
    url(r'^rating/$', VendorRatingListView.as_view(), name='ratings'),
]

vendor_mobile_urls = vendor_mobile_auth_urls + \
                     vendor_mobile_profile_urls + \
                     vendor_mobile_dish_urls + \
                     vendor_mobile_chat_urls + \
                     vendor_mobile_review_urls + \
                     vendor_mobile_notification_urls + \
                     vendor_mobile_market_urls
