from django.conf.urls import url

from seller.authentication.api import (
    VendorLoginView,
    LogoutView,
    ChangePasswordView,
    DeleteView,
    ForgotPasswordView)
from seller.authentication.views import ForgotPasswordTemplateView
from seller.chat.api import ConversationList, MessageList, UnreadMessages
from seller.dish.api import (
    VendorListCreateDishView,
    VendorDishRetrieveUpdateDeleteView,
)
from seller.review.api import VendorRatingListView
from seller.vendor.api import (
    VendorSignUpView,
    VendorTransactionListCreateView)
from seller.vendor.web_api import (
    VendorOnboardingView,
    VendorIngredientsView,
    VendorProfileView,
    VendorIngredientsUpdateView,
    VendorAllergensUpdateView,
    VendorImagesUpdateView,
    VendorTradingUpdateView,
    VendorBusinessUpdateView,
    VendorLocationUpdateView,
    WebMarketListView,
    VendorProfileUpdateView,
    VendorSearchView,
    VendorDashboardView,
    VendorLatestTransactionsView,
    VendorCustomerTypeView,
    VedorMostPurchasedDishesView,
    VendorHighestRatedDishes,
    VendorAddressUpdateView,
    VendorTransactionDetailsView, ConversationListDetailsWeb, PurchaseDetails, AllDishesView)

vendor_web_auth_urls = [
    url(r'^login/$', VendorLoginView.as_view(), name='login'),
    url(r'^sign_up/$', VendorSignUpView.as_view(), name='sign_up'),
    url(r'^logout/$', LogoutView.as_view(), name='logout'),
    url(r'^delete/$', DeleteView.as_view(), name='delete'),
    url(r'^change_password/$', ChangePasswordView.as_view(), name='change_password'),
    url(r'^forgot_password/$', ForgotPasswordView.as_view(), name='forgot_password_email'),
    url(r'^forgot_password/(?P<token>.+)/$', ForgotPasswordTemplateView.as_view(), name='forgot_password'),

]

vendor_web_profile_urls = [
    url(r'^onboarding/$', VendorOnboardingView.as_view(), name='onboarding'),
    url(r'^profile/$', VendorProfileView.as_view(), name='profile'),
    url(r'^update_profile/$', VendorProfileUpdateView.as_view(), name='update_profile'),
    url(r'^update_business/$', VendorBusinessUpdateView.as_view(), name='update_business'),
    url(r'^update_trading/$', VendorTradingUpdateView.as_view(), name='update_trading'),
    url(r'^update_allergens/$', VendorAllergensUpdateView.as_view(), name='update_allergens'),
    url(r'^update_ingredients/$', VendorIngredientsUpdateView.as_view(), name='update_ingredients'),
    url(r'^update_photos/$', VendorImagesUpdateView.as_view(), name='update_photos'),
    url(r'^update_location/$', VendorLocationUpdateView.as_view(), name='update_location'),
    url(r'^update_address/$', VendorAddressUpdateView.as_view(), name='update_address'),
    url(r'^transaction/$', VendorTransactionListCreateView.as_view(), name='transaction'),

]

vendor_web_dish_urls = [
    url(r'^dish/$', VendorListCreateDishView.as_view(), name='dishes'),
    url(r'^dish/(?P<pk>[0-9]+)/$', VendorDishRetrieveUpdateDeleteView.as_view(), name='dish'),
    url(r'^ingredients/$', VendorIngredientsView.as_view(), name='ingredients'),
    url(r'^all_dishes/$', AllDishesView.as_view(), name='all_dishes')

]

vendor_web_market_urls = [
    url(r'^markets/$', WebMarketListView.as_view(), name="markets"),

]

vendor_web_review_urls = [
    url(r'^rating/$', VendorRatingListView.as_view(), name='ratings'),
]

vendor_web_chat_urls = [
    url(r'^chat/$', ConversationList.as_view(), name='chats'),
    url(r'^chat/details/$', ConversationListDetailsWeb.as_view(), name='chat_details'),
    url(r'^chat/(?P<pk>[0-9]+)/messages/$', MessageList.as_view(), name='messages'),
    url(r'^chat/unread/$', UnreadMessages.as_view(), name="unread"),

]

vendor_web_search_urls = [
    url(r'^search/$', VendorSearchView.as_view(), name='search'),
]

vendor_web_dashboard_urls = [
    url(r'^dashboard/$', VendorDashboardView.as_view(), name='dashboard'),
    url(r'latest_transactions/$', VendorLatestTransactionsView.as_view(), name='latest_transactions'),
    url(r'transactions_details/$', VendorTransactionDetailsView.as_view(), name='transactions_details'),
    url(r'customer_type/$', VendorCustomerTypeView.as_view(), name="customer_type"),
    url(r'most_purchased_dishes/$', VedorMostPurchasedDishesView.as_view(), name="most_purchased_dishes"),
    url(r'highest_rated_dishes/$', VendorHighestRatedDishes.as_view(), name="highest_rated_dishes"),
    url(r'purchases/$', PurchaseDetails.as_view(), name="purchases")
]

vendor_web_urls = vendor_web_auth_urls + \
                  vendor_web_profile_urls + \
                  vendor_web_dish_urls + \
                  vendor_web_market_urls + \
                  vendor_web_review_urls + \
                  vendor_web_chat_urls + \
                  vendor_web_search_urls + \
                  vendor_web_dashboard_urls
