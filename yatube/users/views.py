from django.views.generic import CreateView
from django.urls import reverse_lazy
from .forms import CreationForm
from django.contrib.auth.views import (PasswordChangeView,
                                       PasswordResetConfirmView,
                                       PasswordResetView)


class SignUp(CreateView):
    form_class = CreationForm
    success_url = reverse_lazy('posts:index')
    template_name = 'users/signup.html'


class CustomPasswordChangeView(PasswordChangeView):
    success_url = reverse_lazy('users:password_change_done')


class CustomPasswordResetView(PasswordResetView):
    success_url = reverse_lazy('users:password_reset_done')


class CustomPasswordConfirmView(PasswordResetConfirmView):
    success_url = reverse_lazy('users:password_reset_complete')
