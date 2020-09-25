import json

import requests
from django.contrib.auth import authenticate
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers
from rest_framework.exceptions import ParseError

from seller.eater.models import Eater
from seller.user import enums
from seller.user.models import (
    User,
    GeneralSettings,
    Transaction
)
from seller.vendor import enums as vendor_enums
from seller.vendor.models import Vendor, Business
from seller.vendor.utils import send_on_board_email


class Validations(object):
    @staticmethod
    def required_field(obj):
        if not obj:
            raise ParseError(_("Required field can't be empty"))
        return obj

    @staticmethod
    def validate_lat(obj):
        if not obj:
            raise ParseError(_("Latitude can't be empty"))
        return obj

    @staticmethod
    def validate_lng(obj):
        if not obj:
            raise ParseError(_("Longitude can't be empty"))
        return obj

    @staticmethod
    def validate_email(obj):
        if not obj:
            raise serializers.ValidationError("Email can't be empty")
        elif User.objects.filter(email=obj):
            raise serializers.ValidationError(
                "User with this email already exists"
            )
        return obj

    @staticmethod
    def validate_facebook_id(obj):
        if not obj:
            raise serializers.ValidationError("Facebook id cannot be empty")
        elif Eater.objects.filter(facebook_id=obj):
            raise serializers.ValidationError(
                "User with this facebook already exists"
            )
        return obj

    @staticmethod
    def validate_password(obj):
        if not obj or len(obj) < 8:
            raise serializers.ValidationError(
                "Password must contain at least 8 characters"
            )
        return obj

    @staticmethod
    def validate_business_name(obj):
        if not obj:
            raise serializers.ValidationError("Business can't be empty")
        elif Business.objects.filter(name=obj):
            raise serializers.ValidationError(
                "Business with this name already exists"
            )
        return obj

    @staticmethod
    def validate_update_business_name(obj, vendor):
        if not obj:
            raise serializers.ValidationError("Business can't be empty")
        elif Business.objects.filter(name=obj).exclude(vendor=vendor):
            raise serializers.ValidationError(
                "Business with this name already exists"
            )
        return obj

    @staticmethod
    def validate_login(data):
        email = data.get('email')
        password = data.get('password')
        user = authenticate(username=email, password=password)
        if not user:
            raise ParseError(
                _('The email and password do not match, please try again.')
            )
        data['user'] = user
        return data

    @staticmethod
    def validate_eater_login(data):
        email = data.get('email')
        password = data.get('password')
        user = authenticate(username=email, password=password)
        if not user or not user.user_type == enums.EATER:
            raise ParseError(
                _('The email and password do not match, please try again.')
            )
        data['user'] = user
        return data

    @staticmethod
    def validate_vendor_login(data):
        email = data.get('email')
        password = data.get('password')
        user = authenticate(username=email, password=password)
        if not user or not user.user_type == enums.VENDOR:
            raise ParseError(
                _('The email and password do not match, please try again.')
            )
        elif user.vendor.status == vendor_enums.INCOMPLETE:
            send_on_board_email(user)
            raise ParseError(
                _('Please complete your profile by visiting the link provided in your email.')
            )
        # elif user.vendor.status == vendor_enums.COMPLETED:
        #     raise ParseError(
        #         _('Your profile is not approved yet.')
        #     )
        data['user'] = user
        return data

    @staticmethod
    def validate_change_password(instance, data):
        old_password = data.get("old_password")
        password = data.get("password")
        is_correct_password = instance.check_password(old_password)
        if old_password is None or password is None:
            raise ParseError(
                _("You must provide your old and new password.")
            )
        elif not is_correct_password:
            raise ParseError(
                _("Your old password is incorrect.")
            )
        elif old_password == password:
            raise ParseError(
                _("Please enter a password different from your current one.")
            )
        elif len(password) < 8:
            raise ParseError(
                _("Password must contain at least 8 characters")
            )
        return data

    @staticmethod
    def validate_general_settings():
        general_settings = GeneralSettings.objects.get_settings()
        if not general_settings:
            raise ParseError(
                "General settings not provided by Hawkker"
            )
        return general_settings

    @staticmethod
    def validate_min_max_coins_limit(general_settings, coins):
        if not (general_settings.minimum_coins_redeemable <=
                coins <=
                general_settings.maximum_coins_redeemable):
            raise ParseError(
                "Invalid coins"
            )

    @staticmethod
    def validate_user_coins(user, coins):
        if not user.coins >= coins:
            raise ParseError(
                "Insufficient coins"
            )

    @staticmethod
    def validate_transaction(qr_id):
        transaction = Transaction.objects.with_valid_qr_id(
            qr_id
        ).first()
        if not transaction:
            raise ParseError(
                "Invalid QR code"
            )
        return transaction

    @staticmethod
    def validate_vendor(uuid):
        try:
            vendor = Vendor.objects.get(uuid=uuid)
        except Exception as e:
            vendor = None

        if not vendor:
            raise ParseError(
                "Invalid Vendor"
            )
        return vendor

    @staticmethod
    def verify_facebook_signup(facebook_token, facebook_id):
        try:
            url = "https://graph.facebook.com/v2.11/me?access_token={}".format(facebook_token)
            response = requests.get(url)
            return facebook_id == json.loads(response.content.decode('utf-8'))['id']
        except Exception as e:
            return False
