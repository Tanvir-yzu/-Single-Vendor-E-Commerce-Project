from django.views.generic import CreateView, UpdateView
from django.contrib.auth.views import LoginView, LogoutView,  PasswordResetView, PasswordResetConfirmView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import logout
from django.shortcuts import redirect
from .forms import UserRegisterForm, ProfileForm
from .models import Profile
from django.conf import settings
from django.utils.html import strip_tags
from django.core.mail import send_mail
from django.template.loader import render_to_string


class RegisterView(CreateView):
    form_class = UserRegisterForm
    template_name = 'accounts/register.html'
    success_url = reverse_lazy('accounts:login')

    def form_valid(self, form):
        response = super().form_valid(form)
        # Create Profile if it doesn't exist
        Profile.objects.get_or_create(user=self.object)
        # Save additional fields to Profile
        self.object.profile.name = form.cleaned_data['name']
        self.object.profile.mobile_number = form.cleaned_data['mobile_number']
        self.object.profile.nid_image = form.cleaned_data['nid_image']
        self.object.profile.save()

        # Send welcome email using template
        context = {'user': self.object}
        html_message = render_to_string('accounts/registration_email.html', context)
        plain_message = strip_tags(html_message)
        
        send_mail(
            subject='Welcome to FM TRADE',
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[self.object.email],
            html_message=html_message,
            fail_silently=False,
        )

        return response

class CustomLoginView(LoginView):
    template_name = 'accounts/login.html'
    success_url = reverse_lazy('home_page')

class CustomLogoutView(LogoutView):
    template_name = 'accounts/logout.html'
    success_url = reverse_lazy('accounts:login')

    def dispatch(self, request, *args, **kwargs):
        logout(request)
        return redirect(self.success_url)

class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = Profile
    form_class = ProfileForm
    template_name = 'accounts/profile_edit.html'
    success_url = reverse_lazy('accounts:profile_edit')  # Include the namespace

    def get_object(self):
        profile, created = Profile.objects.get_or_create(user=self.request.user)
        return profile


class CustomPasswordResetView(PasswordResetView):
    template_name = 'accounts/reset_password.html'
    email_template_name = 'accounts/password_reset_email.html'
    subject_template_name = 'accounts/password_reset_subject.txt'
    success_url = reverse_lazy('accounts:password_reset_done')
    from_email = "2020tanvir1971@gmail.com"  # Use the email from settings
    
    
class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'accounts/password_reset_confirm.html'
    success_url = reverse_lazy('accounts:password_reset_complete')