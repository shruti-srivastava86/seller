from django.db import IntegrityError

from rest_framework.mixins import CreateModelMixin, UpdateModelMixin, DestroyModelMixin
from rest_framework.response import Response
from rest_framework import status


class DualSerializerCreateModelMixin(CreateModelMixin):
    """
    Create a model instance.
    """

    def create(self, request, *args, **kwargs):
        request_serializer = self.get_request_serializer(data=request.data)
        request_serializer.is_valid(raise_exception=True)
        try:
            obj = self.perform_create(request_serializer)
            response_serializer = self.get_response_serializer(obj)
            headers = self.get_success_headers(response_serializer.data)
            return Response(response_serializer.data,
                            status=status.HTTP_201_CREATED,
                            headers=headers)
        except IntegrityError:
            # Catch IntegrityError if the creation is a duplicate
            return Response(status=status.HTTP_409_CONFLICT)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def perform_create(self, serializer):
        return serializer.save()


class DualSerializerUpdateModelMixin(UpdateModelMixin):
    """
    Update a model instance.
    """

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        request_serializer = self.get_request_serializer(instance,
                                                         data=request.data,
                                                         partial=partial)
        request_serializer.is_valid(raise_exception=True)
        obj = self.perform_update(request_serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        response_serializer = self.get_response_serializer(obj)
        return Response(response_serializer.data)

    def perform_update(self, serializer):
        return serializer.save()


class DualSerializerDeleteModelMixin(DestroyModelMixin):
    """
    Delete a model instance
    """

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def perform_destroy(self, instance):
        instance.delete()
