import time

from django import forms
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.views.generic import FormView
from django.conf import settings
from django.core.files.storage import default_storage

from explorer.models import Query, QueryResult
from ajax_select.fields import AutoCompleteSelectField

from seller.user.models import User
from seller.notification.tasks import send_query_notification

if settings.USE_SENTRY:
    from raven.contrib.django.raven_compat.models import client
else:
    from unittest.mock import MagicMock
    client = MagicMock()


class SendNotificationForm(forms.Form):
    title = forms.CharField()
    subtitle = forms.CharField(
        help_text='This is the text under the title which is sent to the devices\' push notification')
    notification_text = forms.CharField(
        help_text='This is the full text which will be displayed inside of the app',
        widget=forms.Textarea(attrs={'rows': 2}))

    vendor = AutoCompleteSelectField('vendors', required=False)

    icon_image = forms.ImageField(
        label='Icon Image (ratio 2:3)', required=False)
    large_image = forms.ImageField(
        label='Large Image (ratio 19:10)', required=False)


class QuerySendNotification(FormView):
    """Given a Django Query Explorer Query, and a notification title and text, send a notification
    to any users which match it
    """
    template_name = 'explorer/send_notification.html'
    form_class = SendNotificationForm
    success_url = 'explorer_index'

    def get_first_users(self, sql):
        sql = sql.strip()
        if sql.endswith(';'):
            sql = sql[:-1]  # Strip off ;
        user_ids = [x[0] for x in QueryResult('SELECT * FROM ( {} ) q LIMIT 20;'.format(sql)).data]
        return User.objects.filter(id__in=user_ids)[:20]

    def get_query(self, form=None):
        return get_object_or_404(Query, pk=self.kwargs['query_id'])

    def get_context_data(self, **kwargs):
        cntxt = super().get_context_data(**kwargs)
        query = self.get_query()
        cntxt['query'] = query

        if query is not None:
            users = self.get_first_users(query.sql)

            cntxt['users'] = users
        return cntxt

    def form_valid(self, form):
        # Send the notifications here!
        query = self.get_query(form).sql

        vendor_id = None
        if form.cleaned_data.get('vendor'):
            vendor_id = form.cleaned_data['vendor'].id

        icon = None
        icon_url = None
        if form.cleaned_data.get('icon_image'):
            icon = default_storage.save(
                'chat/icon-{}.png'.format(time.time()), form.cleaned_data['icon_image'])
            icon_url = self.request.build_absolute_uri(
                default_storage.url(icon))

        image = None
        image_url = None
        if form.cleaned_data.get('large_image'):
            image = default_storage.save(
                'chat/image-{}.png'.format(time.time()), form.cleaned_data['large_image'])
            image_url = self.request.build_absolute_uri(
                default_storage.url(image))

        # Send in the background
        send_query_notification.delay(
            self.request.user.id, query, {
                'notification_text': form.cleaned_data['notification_text'],
                'title': form.cleaned_data['title'],
                'subtitle': form.cleaned_data['subtitle'],
                'vendor_id': vendor_id,
                'icon_url': icon_url,
                'icon': icon,
                'image_url': image_url,
                'image': image
            })

        messages.success(self.request, 'Notifications were sent')
        return redirect(self.success_url)


class QueryChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.title


class SimpleNotificationForm(SendNotificationForm):
    query = QueryChoiceField(
        empty_label=None,
        widget=forms.RadioSelect,
        queryset=Query.objects.all())


class SimpleQuerySendNotification(QuerySendNotification):
    """A subclass of QuerySendNotification which stays in the admin
    for users who do not have permission to enter the explorer
    """
    template_name = 'admin/send_notification.html'
    form_class = SimpleNotificationForm
    success_url = 'admin:index'

    def get_query(self, form=None):
        try:
            return form.cleaned_data['query']
        except AttributeError:
            pass
