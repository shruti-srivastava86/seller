from ajax_select import register, LookupChannel

from seller.user.models import User


@register('users_lookup')
class UsersLookup(LookupChannel):
    model = User

    def get_query(self, q, request):
        return self.model.filter.active().is_vendor().contains_email(q)

    def format_item_display(self, item):
        return u"<div class='user'>%s</div>" % item.email

    def can_add(self, user, model):
        return False
