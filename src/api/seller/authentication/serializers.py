from rest_framework import serializers

from api.generics.generics import CustomSerializer
from seller.user.models import User
from seller.user.serializers import UserSerializer
from seller.user.validators import Validations


class SignUpSerializer(CustomSerializer):
    """
        Serializer for dealing with a Sign up post request.
    """
    email = serializers.CharField(
        required=True
    )
    name = serializers.CharField(
        required=True
    )
    password = serializers.CharField(
        required=True
    )

    def validate_email(self, obj):
        return Validations.validate_email(
            obj
        )

    def validate_password(self, obj):
        return Validations.validate_password(
            obj
        )

    def create(self, validated_data):
        return User.objects.create_user(
            **validated_data
        )


class LoginSerializer(CustomSerializer):
    """
        Serializer for dealing with a Login post request.
    """
    email = serializers.CharField(
        required=True
    )
    password = serializers.CharField(
        required=True
    )

    def validate(self, data):
        user = Validations.validate_login(
            data
        )
        return user


class EaterLoginSerializer(LoginSerializer):
    def validate(self, data):
        return Validations.validate_eater_login(
            data
        )


class VendorLoginSerializer(LoginSerializer):
    def validate(self, data):
        return Validations.validate_vendor_login(
            data
        )


class UserTokenSerializer(serializers.Serializer):
    """
        Serializer for a User and a Token.
    """
    user = UserSerializer()
    token = serializers.CharField()


class ChangePasswordSerializer(CustomSerializer):
    """
        Serializer for changing a User's password.
    """
    old_password = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True
    )
    password = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True
    )

    def validate(self, data):
        return Validations.validate_change_password(
            self.instance,
            data
        )

    def update(self, instance, validated_data):
        password = validated_data.get(
            "password"
        )
        instance.set_password(
            password
        )
        instance.save()
        return instance


class ForgotPasswordSerializer(CustomSerializer):
    """
        Serializer for forgot User's password.
    """
    email = serializers.CharField(
        required=True
    )
