import csv

from django.http import HttpResponse
from rest_framework.response import Response
import uuid
import os


class ErrorResponse:

    @staticmethod
    def build_serializer_error(serializer, status):
        return Response({"status": "error", "errors": serializer.errors},
                        status=status)

    @staticmethod
    def build_text_error(text, status):
        return Response({"status": "error", "errors": text}, status=status)


def random_profile_image_name(instance, old_filename):
    extension = os.path.splitext(old_filename)[1]
    filename = str(uuid.uuid4()) + extension
    return 'profile_images/' + filename


def random_media_name(instance, old_filename):
    extension = os.path.splitext(old_filename)[1]
    filename = str(uuid.uuid4()) + extension
    return 'media/' + filename


def random_thumbnail_name(instance, old_filename):
    extension = os.path.splitext(old_filename)[1]
    filename = str(uuid.uuid4()) + extension
    return 'thumbnails/' + filename


class ExportCsvMixin:
    def export_as_csv(self, request, queryset):
        meta = self.model._meta
        field_names = [field.name for field in meta.fields]

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename={}.csv'.format(meta)
        writer = csv.writer(response)

        writer.writerow(field_names)
        for obj in queryset:
            writer.writerow([getattr(obj, field) for field in field_names])

        return response
