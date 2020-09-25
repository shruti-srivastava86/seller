from ajax_select.admin import AjaxSelectAdmin, AjaxSelectAdminTabularInline
from django.contrib import admin

from seller.chat.models import Conversation, Message
from api.generics.ajax_select.ajax_select import make_ajax_form
from seller.utils import ExportCsvMixin


def message_ajax_form():
    return make_ajax_form(
        Message,
        {
            'user': {
                'lookup': 'users_lookup',
                'help_text': 'Enter user email to search'
            },
            'read_by': {
                'lookup': 'users_lookup',
                'help_text': 'Enter user email to search'
            },
            'conversation': {
                'lookup': 'conversations_lookup',
                'help_text': 'Enter conversation id to search'
            }
        },
        show_help_text=False,
    )


def conversation_ajax_form():
    return make_ajax_form(
        Conversation,
        {
            'initiator': {
                'lookup': 'users_lookup',
                'help_text': 'Enter user email to search'
            },
            'users': {
                'lookup': 'users_lookup',
                'help_text': 'Enter user email to search'
            },
            'left_by': {
                'lookup': 'users_lookup',
                'help_text': 'Enter user email to search'
            }
        },
        show_help_text=False,
    )


class MessageAdmin(AjaxSelectAdmin):
    list_display = ['user', 'message', 'created_at']
    search_fields = ['user__email']
    form = message_ajax_form()


class MessageInline(AjaxSelectAdminTabularInline):
    model = Message
    extra = 0

    form = message_ajax_form()


class ConversationAdmin(AjaxSelectAdmin, ExportCsvMixin):
    list_display = ['title', 'initiator', 'recipient', 'message', 'message_time']
    inlines = [MessageInline]
    search_fields = ['initiator__email']
    list_filter = ['initiator__vendor', 'chat_type']
    actions = ['export_as_csv']
    form = conversation_ajax_form()

    def message(self, obj):
        try:
            message = obj.conversation_messages.all()[0]
            return message.message
        except Exception as e:
            return None

    def message_time(self, obj):
        try:
            message = obj.conversation_messages.all()[0]
            return message.created_at
        except Exception as e:

            return None

    def recipient(self, obj):
        return "\n".join([p.email for p in obj.users.all()])


admin.site.register(Conversation, ConversationAdmin)
admin.site.register(Message, MessageAdmin)
