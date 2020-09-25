import json

from django.conf import settings
from django.db.models import Q
from scarface.models import (
    Application,
    Platform,
    Device,
    PushMessage
)

from seller.user import enums
from seller.notification.models import Notifications

"""
    Manage Applications/Platforms
"""


def create_notifications(**kwargs):
    Notifications.objects.create(
        **kwargs
    )


def get_or_setup_apns_application(user_type):
    if user_type == enums.EATER:
        application, created = Application.objects.get_or_create(
            name=settings.SCARFACE_APNS_APPLICATION_NAME_EATER
        )
    else:
        application, created = Application.objects.get_or_create(
            name=settings.SCARFACE_APNS_APPLICATION_NAME_VENDOR
        )
    return application


def get_or_setup_gcm_application():
    application, created = Application.objects.get_or_create(
        name=settings.SCARFACE_GCM_APPLICATION_NAME
    )
    return application


def get_or_setup_apns_platform(user_type):
    application = get_or_setup_apns_application(user_type)
    if user_type == enums.EATER:
        apns_platform, created = Platform.objects.get_or_create(
            platform=settings.SCARFACE_APNS_PLATFORM,
            application=application,
            arn=settings.SCARFACE_APNS_ARN_EATER
        )
    else:
        apns_platform, created = Platform.objects.get_or_create(
            platform=settings.SCARFACE_APNS_PLATFORM,
            application=application,
            arn=settings.SCARFACE_APNS_ARN_VENDOR
        )
    apns_platform.is_registered_or_register()
    return apns_platform, application


def get_or_setup_gcm_platform(user_type):
    application = get_or_setup_gcm_application()
    gcm_platform, created = Platform.objects.get_or_create(
        platform=settings.SCARFACE_GCM_PLATFORM,
        application=application,
        arn=settings.SCARFACE_GCM_ARN
    )
    gcm_platform.is_registered_or_register()
    return gcm_platform, application


"""
    Managing devices
"""


def register_device(user, token, uuid, device_type):
    platform = ''
    unregister_device(user, token, uuid)

    if device_type == "apns":
        platform, application = get_or_setup_apns_platform(
            user.user_type
        )
    elif device_type == "gcm":
        platform, application = get_or_setup_gcm_platform(
            user.user_type
        )

    if platform:
        device, created = Device.objects.get_or_create(
            device_id=uuid,
            push_token=token,
            platform=platform
        )
        device.is_registered_or_register()
        user.devices.add(device)


def unregister_device(user, token, uuid):
    devices = Device.objects.filter(
        Q(push_token=token) | Q(device_id=uuid)
    )
    for device in devices:
        user.devices.remove(device)
    devices.delete()


def unregister_all_devices_for_user(user):
    devices = user.devices.all()
    for device in devices:
        device.delete()


"""
    Sending Push Messages
"""


def send_message_to_devices(user_type, devices, text, data, badge_count, category=None):
    try:
        get_or_setup_apns_platform(user_type)
        # get_or_setup_gcm_platform(user_type)
    except Exception:
        pass

    extra_payload = {
        'aps': {

        }
    }
    if category:
        extra_payload['aps']['category'] = category

    if 'large_image' in data:
        # iOS implemented this like this for some reason...
        if data['large_image']:
            extra_payload['large_image'] = data['large_image']
            extra_payload['aps']['mutable-content'] = 1

    if 'title' in data:
        extra_payload['aps']['alert'] = {
            'title': data['title'],
            'body': text,
        }
    push_message = {
        "title": data['title'],
        "body": text
    }

    for device in devices:
        message = PushMessage(
            context=json.dumps(data),
            context_id='none',
            has_new_content=True,
            message=push_message,
            sound="default",
            badge_count=badge_count
        )
        # Set AFTER initiating object actually makes it work
        # I don't know why, but this works ¯\_(ツ)_/¯
        message.extra_payload = extra_payload

        device.update()
        device.send(message)
