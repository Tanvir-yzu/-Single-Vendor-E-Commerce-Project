from django import forms
from django.contrib.auth.forms import UserCreationForm,  PasswordResetForm, SetPasswordForm
from django.contrib.auth.models import User
from .models import Profile

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    name = forms.CharField(max_length=100)
    mobile_number = forms.CharField(max_length=15)
    nid_image = forms.ImageField(required=True)

    class Meta:
        model = User
        fields = ['username', 'name', 'email', 'mobile_number', 'password1', 'password2', 'nid_image']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Common text input style
        text_input_style = 'w-full px-4 py-2 mt-1 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition duration-150'
        # File input style
        file_input_style = 'block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100'

        # Apply styles to all fields
        self.fields['username'].widget.attrs.update({'class': text_input_style})
        self.fields['name'].widget.attrs.update({'class': text_input_style})
        self.fields['email'].widget.attrs.update({'class': text_input_style})
        self.fields['mobile_number'].widget.attrs.update({'class': text_input_style})
        self.fields['password1'].widget.attrs.update({'class': text_input_style})
        self.fields['password2'].widget.attrs.update({'class': text_input_style})
        self.fields['nid_image'].widget.attrs.update({'class': file_input_style})

        # Add placeholder text
        self.fields['username'].widget.attrs['placeholder'] = 'Enter your username'
        self.fields['name'].widget.attrs['placeholder'] = 'Full name'
        self.fields['email'].widget.attrs['placeholder'] = 'example@email.com'
        self.fields['mobile_number'].widget.attrs['placeholder'] = '+8801XXXXXXXXX'

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
        return user

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['name', 'mobile_number', 'profile_image', 'address', 'nid_image']
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Common text input style
        text_input_style = 'w-full px-4 py-2 mt-1 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500'
        # Textarea style
        textarea_style = 'w-full px-4 py-2 mt-1 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500'
        # File input style
        file_input_style = 'block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100'

        # Apply styles to all fields
        self.fields['name'].widget.attrs.update({'class': text_input_style})
        self.fields['mobile_number'].widget.attrs.update({'class': text_input_style})
        self.fields['address'].widget.attrs.update({'class': textarea_style})
        self.fields['profile_image'].widget.attrs.update({'class': file_input_style})
        self.fields['nid_image'].widget.attrs.update({'class': file_input_style})

        # Add placeholder text
        self.fields['mobile_number'].widget.attrs['placeholder'] = '+8801XXXXXXXXX'
        self.fields['address'].widget.attrs['placeholder'] = 'Enter your full address'
        


class CustomPasswordResetForm(PasswordResetForm):
    email = forms.EmailField(
        label="Email",
        max_length=254,
        widget=forms.EmailInput(attrs={
            'class': 'w-full px-4 py-2 mt-1 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors duration-200',
            'placeholder': 'Enter your email address'
        })
    )


class CustomSetPasswordForm(SetPasswordForm):
    new_password1 = forms.CharField(
        label="New password",
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-2 mt-1 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors duration-200',
            'placeholder': 'Enter new password',
            'autocomplete': 'new-password'
        })
    )
    new_password2 = forms.CharField(
        label="Confirm new password",
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-2 mt-1 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors duration-200',
            'placeholder': 'Confirm new password',
            'autocomplete': 'new-password'
        })
    )
        
       