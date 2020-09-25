from rest_framework.exceptions import ValidationError
from rest_framework.generics import (
    GenericAPIView,
    CreateAPIView,
    ListAPIView,
    RetrieveAPIView,
    RetrieveUpdateAPIView
)
from rest_framework import serializers

from api.generics.utils import Utils
from .mixins import (
    DualSerializerCreateModelMixin,
    DualSerializerUpdateModelMixin,
    DualSerializerDeleteModelMixin
)

from django.conf import settings


if settings.USE_SENTRY:
    from raven.contrib.django.raven_compat.models import client
else:
    from unittest.mock import MagicMock
    client = MagicMock()


class DualSerializerGenericAPIView(GenericAPIView):
    """
        Provides a mechanism to provide a request and response serializer,
        rather than the default single serializer for both request and response.
    """
    # Default serializer class for allowing running tests against this view
    serializer_class = serializers.Serializer

    def get_request_serializer(self, *args, **kwargs):
        """
        Return the serializer instance that should be used for validating and
        deserializing input.
        """
        serializer_class = self.get_request_serializer_class()
        kwargs['context'] = self.get_serializer_context()
        return serializer_class(*args, **kwargs)

    def get_request_serializer_class(self):
        """
        Return the class to use for the serializer.
        Defaults to using `self.request_serializer_class`.
        You may want to override this if you need to provide different
        serializations depending on the incoming request.
        (Eg. admins get full serialization, others get basic serialization)
        """
        assert self.request_serializer_class is not None, (
                "'%s' should either include a `request_serializer_class`"
                " attribute, "
                "or override the `get_request_serializer_class()` method."
                % self.__class__.__name__
        )

        return self.request_serializer_class

    def get_response_serializer(self, *args, **kwargs):
        """
        Return the serializer instance that should be used for serializing data
        to output.
        """
        serializer_class = self.get_response_serializer_class()
        kwargs['context'] = self.get_serializer_context()
        return serializer_class(*args, **kwargs)

    def get_response_serializer_class(self):
        """
        Return the class to use for the serializer.
        Defaults to using `self.response_serializer_class`.
        You may want to override this if you need to provide different
        serializations depending on the incoming request.
        (Eg. admins get full serialization, others get basic serialization)
        """
        assert self.response_serializer_class is not None, (
                "'%s' should either include a `response_serializer_class`"
                " attribute, "
                "or override the `get_response_serializer_class()` method."
                % self.__class__.__name__
        )

        return self.response_serializer_class


class CustomCreateAPIView(CreateAPIView):
    def post(self, request, *args, **kwargs):
        try:
            return super().post(request, *args, **kwargs)
        except ValidationError as e:
            client.captureException()
            return Utils.validation_error(e)
        except Exception as e:
            client.captureException()
            return Utils.exception_error(e)


class CustomListAPIView(ListAPIView):
    """
        Custom list view for listing a model instances.
    """

    def get(self, request, *args, **kwargs):
        try:
            return self.list(request, *args, **kwargs)
        except Exception as e:
            client.captureException()
            return Utils.exception_error(e)


class CustomRetrieveAPIView(RetrieveAPIView):
    """
        Custom retrieve view for retrieving a model instance.
    """

    def get(self, request, *args, **kwargs):
        try:
            return self.retrieve(request, *args, **kwargs)
        except Exception as e:
            client.captureException()
            return Utils.exception_error(e)


class CustomRetrieveUpdateAPIView(RetrieveUpdateAPIView):
    """
        Custom retrieve update view for retrieving and updating a model instance.
    """

    def get(self, request, *args, **kwargs):
        try:
            return self.retrieve(request, *args, **kwargs)
        except Exception as e:
            client.captureException()
            return Utils.exception_error(e)

    def put(self, request, *args, **kwargs):
        try:
            return self.update(request, *args, **kwargs)
        except Exception as e:
            client.captureException()
            return Utils.exception_error(e)

    def patch(self, request, *args, **kwargs):
        try:
            return self.partial_update(request, *args, **kwargs)
        except Exception as e:
            client.captureException()
            return Utils.exception_error(e)


class DualSerializerCreateAPIView(DualSerializerCreateModelMixin,
                                  DualSerializerGenericAPIView):
    """
    Concrete view for creating a model instance.
    """

    def post(self, request, *args, **kwargs):
        try:
            return self.create(request, *args, **kwargs)
        except ValidationError as e:
            client.captureException()
            return Utils.validation_error(e)
        except Exception as e:
            client.captureException()
            return Utils.exception_error(e)


class DualSerializerUpdateAPIView(DualSerializerUpdateModelMixin,
                                  DualSerializerGenericAPIView):
    """
    Concrete view for updating a model instance.
    """

    def put(self, request, *args, **kwargs):
        try:
            return self.update(request, *args, **kwargs)
        except ValidationError as e:
            client.captureException()
            return Utils.validation_error(e)
        except Exception as e:
            client.captureException()
            return Utils.exception_error(e)

    def patch(self, request, *args, **kwargs):
        try:
            return self.partial_update(request, *args, **kwargs)
        except ValidationError as e:
            client.captureException()
            return Utils.validation_error(e)
        except Exception as e:
            client.captureException()
            return Utils.exception_error(e)


class DualSerializerCreateUpdateAPIView(DualSerializerCreateModelMixin,
                                        DualSerializerUpdateModelMixin,
                                        DualSerializerGenericAPIView):
    """
    Concrete view for creating and updating a model instance.
    """

    def post(self, request, *args, **kwargs):
        try:
            return self.create(request, *args, **kwargs)
        except ValidationError as e:
            client.captureException()
            return Utils.validation_error(e)
        except Exception as e:
            client.captureException()
            return Utils.exception_error(e)

    def put(self, request, *args, **kwargs):
        try:
            return self.update(request, *args, **kwargs)
        except ValidationError as e:
            client.captureException()
            return Utils.validation_error(e)
        except Exception as e:
            client.captureException()
            return Utils.exception_error(e)

    def patch(self, request, *args, **kwargs):
        try:
            return self.partial_update(request, *args, **kwargs)
        except ValidationError as e:
            client.captureException()
            return Utils.validation_error(e)
        except Exception as e:
            client.captureException()
            return Utils.exception_error(e)


class DualSerializerCreateDeleteAPIView(DualSerializerCreateModelMixin,
                                        DualSerializerDeleteModelMixin,
                                        DualSerializerGenericAPIView):
    """
    Concrete view for creating and deleting a model instance.
    """

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


class DualSerializerCreateUpdateDeleteAPIView(DualSerializerCreateModelMixin,
                                              DualSerializerUpdateModelMixin,
                                              DualSerializerDeleteModelMixin,
                                              DualSerializerGenericAPIView):
    """
    Concrete view for creating, updating, and deleting a model instance.
    """

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


class DualSerializerUpdateDeleteAPIView(DualSerializerUpdateModelMixin,
                                        DualSerializerDeleteModelMixin,
                                        DualSerializerGenericAPIView):
    """
    Concrete view for creating, updating, and deleting a model instance.
    """

    def patch(self, request, *args, **kwargs):
        try:
            return self.partial_update(request, *args, **kwargs)
        except ValidationError as e:
            client.captureException()
            return Utils.validation_error(e)
        except Exception as e:
            client.captureException()
            return Utils.exception_error(e)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


class CustomSerializer(serializers.Serializer):
    """
        Custom model serializer
        - This checks if all the required fields are specified -
    """

    def __init__(self, *args, **kwargs):
        super(CustomSerializer, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].error_messages[
                'required'] = '{} field is required'.format(field)


class CustomModelSerializer(serializers.ModelSerializer):
    """
        Custom model serializer
        - This checks if all the required fields are specified -
    """

    def __init__(self, *args, **kwargs):
        super(CustomModelSerializer, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].error_messages[
                'required'] = '{} field is required'.format(field)


class SuccessResponseSerializer(serializers.Serializer):
    success = serializers.BooleanField(required=False)
    error = serializers.CharField(required=False)
