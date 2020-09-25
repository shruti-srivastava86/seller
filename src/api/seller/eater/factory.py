from seller.eater.models import Eater
from seller.user.factory import BaseUserFactory


class EaterUserFactory(BaseUserFactory):
    """
        Factory for creating an Eater user.
    """

    class Meta:
        model = Eater
