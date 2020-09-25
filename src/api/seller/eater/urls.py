from django.conf.urls import url

from seller.authentication.api import (
    EaterLoginView,
    LogoutView,
    ChangePasswordView,
    ForgotPasswordView,
    DeleteView)
from seller.authentication.views import ForgotPasswordTemplateView
from seller.dish.api import (
    DishListView,
    DietaryListView,
    CuisinesListView,
    AllergenListView
)
from seller.eater.api import (
    EaterSignUpView,
    EaterRetrieveDelete,
    EaterProfileView,
    EaterTransactionListCreateView,
    EaterGeneralSettingsView,
    ReportVendorView,
    SupportEaterView,
    EaterNotificationsView,
    FacebookSignup, FacebookLogin, UnreadMessages, EaterReviewCheckApi)
from seller.notification.api import DeviceRegister, DeviceUnregister, EaterPreferences
from seller.purchase.api import PurchaseListView
from seller.review.api import EaterRatingCreateView
from seller.vendor.api import (
    VendorListView,
    VendorRetrieveUpdateView,
    FavouriteVendor,
    UnFavouriteVendor,
    VendorDishesList,
    VendorRetrieveView)
from seller.vendor.web_api import WebMarketListView

eater_mobile_auth_urls = [
    url(r'^$', EaterRetrieveDelete.as_view(), name='retrieve_delete'),
    url(r'^login/$', EaterLoginView.as_view(), name='login'),
    url(r'^sign_up/$', EaterSignUpView.as_view(), name='sign_up'),
    url(r'^logout/$', LogoutView.as_view(), name='logout'),
    url(r'^delete/$', DeleteView.as_view(), name='delete'),
    url(r'^change_password/$', ChangePasswordView.as_view(), name='change_password'),
    url(r'^forgot_password/$', ForgotPasswordView.as_view(), name='forgot_password_email'),
    url(r'^forgot_password/(?P<token>.+)/$', ForgotPasswordTemplateView.as_view(), name='forgot_password'),
    url(r'^facebook/signup/$', FacebookSignup.as_view(), name="facebook_signup"),
    url(r'^facebook/login/$', FacebookLogin.as_view(), name="facebook_login"),
]

eater_mobile_profile_urls = [
    url(r'^profile/$', EaterProfileView.as_view(), name="profile"),
    url(r'^transaction/$', EaterTransactionListCreateView.as_view(), name='transaction'),
    url(r'^general_settings/$', EaterGeneralSettingsView.as_view(), name='general_settings'),

]

eater_mobile_vendor_urls = [
    url(r'^vendor/$', VendorListView.as_view(), name='vendors'),
    url(r'^vendor/(?P<pk>[0-9]+)/$', VendorRetrieveUpdateView.as_view(), name='vendor'),
    url(r'^vendor/(?P<pk>[0-9]+)/favourite/$', FavouriteVendor.as_view(), name='vendor_favourite'),
    url(r'^vendor/(?P<pk>[0-9]+)/unfavourite/$', UnFavouriteVendor.as_view(), name='vendors_unfavourite'),
    url(r'^vendor/(?P<pk>[0-9]+)/dishes/$', VendorDishesList.as_view(), name='vendors_dishes'),
]

eater_mobile_dish_urls = [
    url(r'^dish/$', DishListView.as_view(), name="dishes"),
    url(r'^dish/dietary/$', DietaryListView.as_view(), name="dietary"),
    url(r'^dish/cuisines/$', CuisinesListView.as_view(), name="cuisines"),
    url(r'^dish/allergens/$', AllergenListView.as_view(), name="allergens"),
]

eater_mobile_purchase_urls = [
    url(r'^scan/$', VendorRetrieveView.as_view(), name='scan'),
    url(r'^purchase/$', PurchaseListView.as_view(), name='purchase'),
]

eater_mobile_review_urls = [
    url(r'^review/$', EaterRatingCreateView.as_view(), name='review'),
    url(r'^check_review/$', EaterReviewCheckApi.as_view(), name='review_check'),
]

eater_mobile_notification_urls = [
    url(r'^notifications/$',
        EaterNotificationsView.as_view({
            'get': 'list',
        }),
        name="notifications"),
    url(r'^notifications/(?P<pk>[0-9]+)/read/$',
        EaterNotificationsView.as_view({
            'post': 'read',
        }),
        name="notifications-read"),
    url(r'^device_register/$', DeviceRegister.as_view(), name="register_device"),
    url(r'^device_unregister/$', DeviceUnregister.as_view(), name="unregister_device"),
    url(r'^notification_preference/$', EaterPreferences.as_view(), name="notification_preference"),
    url(r'^notifications/unread/$', UnreadMessages.as_view(), name="unread"),

]

eater_mobile_report_urls = [
    url(r'^report_vendor/$', ReportVendorView.as_view(), name='report_vendor'),
    url(r'^support_eater/$', SupportEaterView.as_view(), name='support_eater'),

]

eater_mobile_market_urls = [
    url(r'^markets/$', WebMarketListView.as_view(), name="markets"),

]

eater_mobile_urls = eater_mobile_auth_urls + \
                    eater_mobile_profile_urls + \
                    eater_mobile_vendor_urls + \
                    eater_mobile_dish_urls + \
                    eater_mobile_purchase_urls + \
                    eater_mobile_review_urls + \
                    eater_mobile_notification_urls + \
                    eater_mobile_report_urls + \
                    eater_mobile_market_urls
