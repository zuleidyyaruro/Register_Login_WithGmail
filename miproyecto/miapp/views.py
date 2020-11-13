import json
from django.conf import settings
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User, Group, Permission
from django.core.exceptions import ValidationError
from django.core.mail import EmailMessage
from django.template.loader import get_template
from django.db import transaction
from django.db.models import Q
from django.http import HttpResponse
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.shortcuts import render, redirect, reverse, get_object_or_404
from miapp.forms import RegistrationForm

from django.views import View
from .tokens import user_tokenizer

from django.views.generic import TemplateView

# Create your views here.

class profile_View(TemplateView):
    template_name = "profile.html"
    

class RegisterView(View):
    def get(self, request):
        return render(request, 'register.html', { 'form': RegistrationForm() })

    def post(self, request):
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_valid = False
            user.save()
            token = user_tokenizer.make_token(user)
            user_id = urlsafe_base64_encode(force_bytes(user.id))
            url = 'http://localhost:8000' + reverse('confirm_email', kwargs={'user_id': user_id, 'token': token})
            message = get_template('register_email.html').render({
              'confirm_url': url
            })
            mail = EmailMessage('Django Survey Email Confirmation', message, to=[user.email], from_email=settings.EMAIL_HOST_USER)
            mail.content_subtype = 'html'
            mail.send()

            return render(request, 'login.html', {
              'form': AuthenticationForm(),
              'message': f'A confirmation email has been sent to {user.email}. Please confirm to finish registering'
            })

        return render(request, 'register.html', { 'form': form })

# ... omitting everything below for brevity

class LoginView(View):
    def get(self, request):
        return render(request, 'login.html', { 'form':  AuthenticationForm })

    def post(self, request):
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            try:
                form.clean()
            except ValidationError:
                return render(
                    request,
                    'login.html',
                    { 'form': form, 'invalid_creds': True }
                )

            login(request, form.get_user())

            return redirect(reverse('profile'))

        return render(request, 'login.html', { 'form': form })

class ConfirmRegistrationView(View):
    def get(self, request, user_id, token):
        user_id = force_text(urlsafe_base64_decode(user_id))
        
        user = User.objects.get(pk=user_id)

        context = {
          'form': AuthenticationForm(),
          'message': 'Registration confirmation error . Please click the reset password to generate a new confirmation email.'
        }
        if user and user_tokenizer.check_token(user, token):
            user.is_valid = True
            user.save()
            context['message'] = 'Registration complete. Please login'

        return render(request, 'login.html', context)
