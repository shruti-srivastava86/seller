from django.contrib.auth.models import UserManager

from seller.user import enums


class EaterUserManager(UserManager):

    def create_user(self, **kwargs):
        user = self.model(**kwargs)
        user.save(using=self._db)
        user.is_active = True
        user.user_type = enums.EATER
        user.set_password(kwargs.get('password'))
        if 'location' in kwargs:
            user.location = kwargs.get('location')
        user.save(using=self._db)
        return user

    def create_guest_user(self, **kwargs):
        user = self.model(**kwargs)
        user.save(using=self._db)
        user.is_active = True
        user.user_type = enums.EATER
        user.set_password(kwargs.get('password'))
        if 'location' in kwargs:
            user.location = kwargs.get('location')
        user.save(using=self._db)
        return user
