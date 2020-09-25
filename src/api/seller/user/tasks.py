import json

from celery.task import task

from seller.chat.enums import NOTIFICATIONS
from seller.chat.models import Conversation, Message
from seller.eater.utils import unread_count as eater_badge_count
from seller.notification import constants
from seller.notification.utils import create_notifications
from seller.notification.utils import send_message_to_devices
from seller.user.enums import VENDOR
from seller.user.models import User
from seller.vendor.utils import unread_count


def create_message(initiator, notification_text, conversation, context):
    message = Message()
    if isinstance(initiator, int):
        message.user_id = initiator
    else:
        message.user = initiator
    message.message = notification_text
    if context.get('image'):
        message.image = context.get('image')
    message.conversation = conversation
    message.save()
    return message


@task(name="cohorting_users")
def send_notifications_user(initiator, users, notification_text, title, subtitle, context=None, model_context=None):
    """
        For sending notification for eaters and vendors based on sql query
    :param initiator: Who created the notification
    :param users: Who to send the notification to
    :param notification_text: Text of the notification. Not sent to the push mechanism
    :param title: Title of the notification
    :param subtitle: Subtitle of the Notification.
    :param context: The context send to the user
    :param model_context: The context saved to the model
    :return:
    """
    if context is None:
        context = {}
    if model_context is None:
        model_context = {}

    data = {}
    context["notification_text"] = notification_text
    if len(users) > 0 and isinstance(users[0], int):
        users = User.objects.filter(id__in=users)

    for user in users:
        if user.user_type == VENDOR:
            data = model_context
            conversation = Conversation()
            if isinstance(initiator, int):
                conversation.initiator_id = initiator
            else:
                conversation.initiator = initiator
            conversation.title = title
            conversation.chat_type = NOTIFICATIONS
            conversation.save()
            conversation.users.add(user)
            create_message(initiator, notification_text, conversation, model_context)
            message_count = unread_count(user)
            vendor_context = {**{
                "type": constants.NOTIFICATIONS,
                "id": conversation.id,
                "title": title,

            }, **context}

            send_message_to_devices(
                user.user_type,
                user.devices.all(),
                subtitle,
                vendor_context,
                message_count,
                constants.PUSH_CATEGORY_MARKETING)
        else:
            data = model_context

            eater_context = {**{
                "type": NOTIFICATIONS,
                "title": title,
            }, **context}
            badge_count = eater_badge_count(user)
            send_message_to_devices(
                user.user_type,
                user.devices.all(),
                subtitle,
                eater_context,
                badge_count,
                constants.PUSH_CATEGORY_MARKETING)

        data['message'] = notification_text
        data['context'] = json.dumps(context)
        create_notifications(
            user=user,
            content_object=user,
            notification_type=NOTIFICATIONS,
            **data)
