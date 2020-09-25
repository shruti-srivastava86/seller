from django.conf import settings

from seller.authentication.models import Token


def regenerate_token(user):
    """
        Recreates an authentication token for the passed in user

        :param user: The user to recreate the token for
        :type user: :class:`User <seller.user.models.User>`

        :return: The token for the user
        :rtype: Token
    """
    return Token.objects.create(user=user)


def get_token(user):
    """
        Gets an authentication token for the passed in user

        :param user: The user to get the token for
        :type user: :class:`User <seller.user.models.User>`

        :return: The token for the user
        :rtype: Token
    """
    try:
        return Token.objects.filter(user=user)[0]
    except IndexError:
        return Token.objects.create(user=user)


def create_guest_token(user):
    token, created = Token.objects.get_or_create(user=user,
                                                 key=settings.GUEST_AUTH_TOKEN)
    return token
