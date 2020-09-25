import arrow
import datetime

from django.http import HttpResponse
from django.db.models import Sum
from django.shortcuts import render
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.clickjacking import xframe_options_exempt
from django.views.generic import TemplateView
from django.conf import settings
from django.views.generic import View
from django.shortcuts import render_to_response
from django.template.context import make_context
from django.template.loader import get_template

from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.schemas import SchemaGenerator
from rest_framework.views import APIView
from seller.authentication.models import Token
from rest_framework_swagger import renderers

from seller.chat.models import Message
from seller.user import enums
from seller.user.models import User, ReportVendor, Transaction
from seller.user.utils import send_forgot_password_email
from seller.purchase.models import Purchase
from seller.vendor.models import Vendor, Business, OpeningHours, VendorProfileViews
from seller.vendor.enums import COMPLETED as VENDOR_COMPLETED
from seller.notification import enums as notification_enums
from seller.notification.models import EmailTemplate


VENDOR_SAMPLE = {'name': 'Bob Smith', 'business': {'name': 'Fish n Chips'}}


EMAIL_CONFIGURATIONS = {
    'forgot': {
        'template': 'forgot_password',
        'config': {
            'link': 'https://example.org/eojfij/',
            'user': {'name': 'John Smith'},
        },
        'text_config': notification_enums.FORGOT_PASSWORD,
    },
    'onboarding': {
        'template': 'onboarding',
        'config': {
            'link': 'https://example.org/eojfij/',
            'vendor': VENDOR_SAMPLE,
        },
        'text_config': notification_enums.ONBOARDING,
    },
    'approved': {
        'template': 'approved',
        'config': {
            'link': 'https://example.org/eojfij/',
            'vendor': VENDOR_SAMPLE,
        },
        'text_config': notification_enums.APPROVE_EMAIL,
    },
    'remind_complete': {
        'template': 'remind_complete',
        'config': {
            'link': 'https://example.org/eojfij/',
            'vendor': VENDOR_SAMPLE,
        },
        'text_config': notification_enums.REMIND_COMPLETE,
    },
    'rejected': {
        'template': 'rejected',
        'config': {
            'vendor': VENDOR_SAMPLE,
        },
        'text_config': notification_enums.REJECT_EMAIL,
    },
    'vendor_report': {
        'template': 'vendor_report',
        'config': {
            'vendor': {
                'name': 'Apple Stall',
                'location': {
                    'x': '1384.304',
                    'y': '49349.32',
                }
            },
            'eater': {'name': 'John Smith', 'email': 'eater@seller.com', },
            'date': '20-11-2019',
            'time': '12:09',
            'comment': 'Comment',
            'reason': 'Mouldy Food',
        },
        'text_config': notification_enums.REPORT_VENDOR,
    },
    'support': {
        'template': 'support',
        'config': {
            'comment': "The app blew up my house! Help!",
            'subject': 'Something',
        },
        'text_config': notification_enums.SUPPORT,
    },
}


class EmailTemplateView(View):
    """View used to display the basic email template
    """
    def get(self, request, *args):
        if 'email' not in request.GET:
            config = EMAIL_CONFIGURATIONS['forgot']
        else:
            config = EMAIL_CONFIGURATIONS[request.GET['email']]

        template_name = 'templated_email/{}.email'.format(config['template'])

        response = {}

        config['config']['app_config'] = settings
        config['config']['protocol'] = 'http'
        config['config']['domain'] = request.META['HTTP_HOST']

        try:
            template = EmailTemplate.objects.get(type=config['text_config'])
            config['config']['text'] = template.content
        except EmailTemplate.DoesNotExist:
            config['config']['text'] = '<!> WARNING <!> EMAIL TEMPLATE DOES NOT EXIST <!> WARNING <!>'

        context = make_context(config['config'], request=request)
        template = get_template(template_name)
        with context.bind_template(template.template):
            for node in template.template.nodelist:
                attr = getattr(node, 'name', None)
                if attr is not None:
                    response[attr] = node.render(context).strip()

        response['templates'] = EMAIL_CONFIGURATIONS.keys()

        return render_to_response(
            'seller/test_email.html', response)


class SwaggerSchemaView(APIView):
    permission_classes = [AllowAny]
    renderer_classes = [
        renderers.OpenAPIRenderer,
        renderers.SwaggerUIRenderer
    ]

    def get(self, request):
        generator = SchemaGenerator(title='Hawkker API')
        schema = generator.get_schema(request=request)

        return Response(schema)


def home(request):
    return HttpResponse("Hello, World.")


def password_reset(request):
    user = User.filter.with_email(request.GET.get('emailAddress')).first()
    data = {}
    if not user:
        data['error'] = "No user with this email exists"
        return render(request, 'registration/forgot_password.html', data)
    elif not user.is_staff:
        data['error'] = "No user with this email exists"
        return render(request, 'registration/forgot_password.html', data)

    send_forgot_password_email(user)
    data['success'] = "Check your email for setting up new password"

    return render(request, 'registration/forgot_password.html', data)


class DashboardView(TemplateView):
    template_name = 'admin/dashboard.html'

    def get_context_data(self, **kwargs):
        cntxt = super().get_context_data(**kwargs)
        cntxt['tab'] = 'dashboard'
        message_count = Message.objects.for_user(self.request.user).unread(self.request.user).count()

        cntxt['unread_chat'] = message_count

        cntxt['checked_in'] = Business.objects.filter(open=True).count()

        today_weekday = datetime.datetime.today().weekday()  # Same as Enum
        cntxt['should_checked_in'] = Business.objects.filter(opening_hours__in=OpeningHours.objects.filter(
            weekday=today_weekday,
            open=True)).count()

        cntxt['closed_today'] = Business.objects.filter(open=False).count()
        cntxt['pending_approval'] = Vendor.objects.filter(status=VENDOR_COMPLETED).count()

        cntxt['unread_complaints'] = ReportVendor.objects.filter(processed=False).count()
        profile_views = VendorProfileViews.objects.filter(
            created_at__date=timezone.now().date()

        ).first()
        if profile_views:
            cntxt['registered_browsing'] = profile_views.count
            cntxt['guest_browsing'] = profile_views.guest_count
        else:
            cntxt['registered_browsing'] = 0
            cntxt['guest_browsing'] = 0

        cntxt['purchases_today'] = Purchase.objects.filter(
            created_at__date=arrow.now().date()).count()
        cntxt['last_week_unreviewed'] = Purchase.objects.filter(
            created_at__gte=arrow.now().shift(weeks=-1).datetime,
            rating__isnull=True).count()
        cntxt['trans_last_week'] = Purchase.objects.filter(
            created_at__gte=arrow.now().shift(weeks=-1).datetime).count()
        cntxt['today_loyalty_redemption'] = Transaction.objects.filter(
            type=enums.DEBIT,
            created_at__date=datetime.date.today(),
            reason=enums.EATER_REWARD).aggregate(total=Sum('coins'))['total'] or 0
        return cntxt


@method_decorator(xframe_options_exempt, name='dispatch')
class AdminChatView(TemplateView):
    template_name = 'admin/chat.html'

    def get_context_data(self, **kwargs):
        cntxt = super().get_context_data(**kwargs)
        cntxt['tab'] = 'chat'
        cntxt['base_url'] = settings.WEB_BASE_URL
        cntxt['token'] = Token.objects.get_or_create(
            user=self.request.user)[0]
        cntxt['id'] = self.request.user.id
        return cntxt
