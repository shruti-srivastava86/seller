from rest_framework.exceptions import APIException


class UserNotInConversationException(APIException):
    status_code = 400
    default_detail = 'You are not a participant in this conversation, so this action is forbidden.'
    default_code = 'detail'
