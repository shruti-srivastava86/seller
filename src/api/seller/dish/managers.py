from django.db import models


class DishQueryset(models.QuerySet):

    def is_active(self):
        return self.filter(active=True,
                           deleted=False)

    def is_inactive(self):
        return self.filter(active=False,
                           deleted=False)

    def is_deleted(self):
        return self.filter(deleted=True)

    def for_vendor(self, pk):
        return self.filter(business__vendor__id=pk)

    def is_special(self):
        count = self.filter(special=True).count()
        if count > 0:
            return True
        else:
            return False

    def prefetch_dietary(self):
        return self.prefetch_related('dietary_information')
