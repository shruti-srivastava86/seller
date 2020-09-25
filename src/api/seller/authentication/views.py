from django.shortcuts import render
from django.views.generic import FormView
from rest_framework.permissions import AllowAny
from rest_framework.renderers import TemplateHTMLRenderer

from seller.authentication.forms import ForgotPasswordForm
from seller.user.models import ForgotPassword
from seller.user.validators import Validations


class ForgotPasswordTemplateView(FormView):
    """
        A user can reset their password by opening the one-time reset link sent to their profile
    """
    renderer_classes = [TemplateHTMLRenderer]
    permission_classes = [AllowAny]
    form_class = ForgotPasswordForm
    template_name = 'seller/forgot_password.html'

    def get(self, request, *args, **kwargs):
        forgot_password = ForgotPassword.objects.filter(
            token=self.kwargs.get('token')
        )
        if not forgot_password.exists():
            return render(request, 'seller/forgot_password_expired.html')
        return super(ForgotPasswordTemplateView, self).get(request,
                                                           *args,
                                                           **kwargs)

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        token = self.kwargs.get('token')
        password = self.request.POST.get('password')
        forgot_password = ForgotPassword.objects.filter(token=token).first()
        user = forgot_password.user

        try:
            Validations.validate_password(password)
        except Exception as e:
            form.add_error(
                "password",
                "Password must contain at least 8 characters"
            )
            return self.form_invalid(form)

        user.set_password(password)
        user.save()
        forgot_password.delete()

        return render(request, 'seller/forgot_password_success.html')
