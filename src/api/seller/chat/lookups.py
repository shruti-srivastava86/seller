from ajax_select import register, LookupChannel

from seller.chat.models import Conversation


@register('conversations_lookup')
class ConversationsLookup(LookupChannel):

    model = Conversation

    def get_query(self, q, request):
        return self.model.objects.active().with_id(q)

    def format_item_display(self, item):
        return u"<div class='conversation'>%s</div>" % item
