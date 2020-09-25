from templated_mail.mail import BaseEmailMessage

from seller.notification.models import EmailTemplate


class HawkkerEmailMessage(BaseEmailMessage):
    def __init__(self, email_type, **kwargs):
        super().__init__(**kwargs)
        self.email_type = email_type

    def get_context_data(self):
        context = super().get_context_data()

        try:
            template = EmailTemplate.objects.get(type=self.email_type)
            context['text'] = template.content
        except EmailTemplate.DoesNotExist:
            # Raise an error to inform of missing template
            raise RuntimeError(
                'Email Template for {} does not exist'.format(self.email_type))

        return context
