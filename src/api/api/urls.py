from django.conf.urls import include, url
from django.contrib import admin
from django.conf import settings
from django.views.static import serve
from ajax_select import urls as ajax_select_urls

from rest_framework.urlpatterns import format_suffix_patterns

from api.views import home, SwaggerSchemaView, password_reset
from seller.authentication.views import ForgotPasswordTemplateView
from seller.chat.urls import chat_mobile_urls
from seller.eater.urls import eater_mobile_urls
from seller.vendor.mobile_urls import vendor_mobile_urls
from seller.vendor.web_urls import vendor_web_urls
from seller.dish.urls import dish_mobile_urls
from seller.dish.web_urls import dish_web_urls
from api.views import DashboardView, AdminChatView, EmailTemplateView
from seller.notification.views import (
    QuerySendNotification, SimpleQuerySendNotification)


def generate_api_url_include(name):
    regex = r'^{}/'.format(name)
    namespace = 'seller.{}'.format(name)
    if name == "docs":
        return url(regex, SwaggerSchemaView.as_view(), name=namespace)
    to_include = include('seller.{}.urls'.format(name))
    return url(regex, to_include, name=namespace)


def generate_mobile_url_include(name):
    regex = r'^{}/'.format(name)
    namespace = 'seller.mobile.{}'.format(name)
    if name == "eater":
        to_include = include(eater_mobile_urls, namespace=namespace)
    elif name == "vendor":
        to_include = include(vendor_mobile_urls, namespace=namespace)
    elif name == "dish":
        to_include = include(dish_mobile_urls, namespace=namespace)
    else:
        to_include = include(chat_mobile_urls, namespace=namespace)
    return url(regex, to_include, name=namespace)


def generate_web_url_include(name):
    regex = r'^{}/'.format(name)
    namespace = 'seller.web.{}'.format(name)
    if name == "vendor":
        to_include = include(vendor_web_urls, namespace=namespace)
    elif name == "dish":
        to_include = include(dish_web_urls, namespace=namespace)
    return url(regex, to_include, name=namespace)


namespaces_to_include = [
    "docs",
]

api_namespaces_to_include = [
    "eater",
    "vendor",
    "dish",
    "chat",

]

web_api_namespaces_to_include = [
    "vendor",
    "dish",

]

api_namespace_urls = [
    generate_api_url_include(name) for name in namespaces_to_include
]

mobile_api_namespace_urls = [
    generate_mobile_url_include(name) for name in api_namespaces_to_include
]

web_api_namespace_urls = [
    generate_web_url_include(name) for name in web_api_namespaces_to_include
]

urlpatterns = [
    url(r'^api/v1/', include(api_namespace_urls)),
    url(r'^api/v1/mobile/', include(mobile_api_namespace_urls)),
    url(r'^api/v1/web/', include(web_api_namespace_urls)),
]

urlpatterns = format_suffix_patterns(urlpatterns)


def get_admin_urls(urls):
    def get_urls():
        my_urls = [
            url(r'^dashboard/$', DashboardView.as_view(), name="dashboard"),
            url(r'^user/explorer/$', SimpleQuerySendNotification.as_view(), name="explorer"),
            url(r'^chat/$', AdminChatView.as_view(), name="chat"),
            url(r'^test_email/$', EmailTemplateView.as_view(), name="email_test"),
        ]
        return my_urls + urls

    return get_urls


admin_urls = get_admin_urls(admin.site.get_urls())
admin.site.get_urls = admin_urls

urlpatterns += [
    url(r'^_admin/', include(admin.site.urls)),

    url(r'^explorer/notify/(?P<query_id>[0-9]+)/$', QuerySendNotification.as_view(), name="explorer-send"),

    url(r'^explorer/', include('explorer.urls')),
    url('auth/$^', include('django.contrib.auth.urls')),
    url(r'^admin/forgot_password/$', password_reset, name='forgot_password_reset'),
    url(r'^admin/forgot_password/(?P<token>.+)/$', ForgotPasswordTemplateView.as_view(), name='forgot_password'),

    url(r'^ajax_select/', include(ajax_select_urls)),
    url(r'^$', home, name='home'),
    url(r'^uploads/(.*)$', serve, {
        'document_root': settings.MEDIA_ROOT, 'show_indexes': True
    }),

]

try:
    urlpatterns += [
        url(r'^silk/', include('silk.urls', namespace='silk')),
    ]
except Exception as e:
    pass


if settings.DEBUG_TOOLBAR:
    import debug_toolbar

    urlpatterns = [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
