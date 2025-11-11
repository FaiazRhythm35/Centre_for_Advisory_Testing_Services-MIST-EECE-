from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from .models import Profile

class SignupForm(UserCreationForm):
    full_name = forms.CharField(max_length=150, required=False)
    account_type = forms.ChoiceField(choices=[('organization','Organization'),('self','Self')], initial='organization')
    org_name = forms.CharField(max_length=200, required=False)
    role_in_org = forms.CharField(max_length=120, required=False)
    phone = forms.CharField(max_length=50, required=False)
    address = forms.CharField(widget=forms.Textarea, required=False)

    class Meta:
        model = User
        fields = ('username', 'password1', 'password2')

    def clean(self):
        cleaned = super().clean()
        if cleaned.get('account_type') == 'organization':
            if not cleaned.get('org_name'):
                self.add_error('org_name', 'Organization name is required')
            if not cleaned.get('role_in_org'):
                self.add_error('role_in_org', 'Role in organization is required')
        return cleaned

    def save(self, commit=True):
        user = super().save(commit=False)
        email_val = self.cleaned_data.get('username')
        if email_val and '@' in email_val:
            user.email = email_val
        if commit:
            user.save()
            # Generate a simple 6-digit client ID padded with zeros
            try:
                next_num = (Profile.objects.count() + 1)
                client_id = f"{next_num:06d}"
            except Exception:
                client_id = "000001"
            Profile.objects.create(
                user=user,
                full_name=self.cleaned_data.get('full_name') or '',
                account_type=self.cleaned_data.get('account_type') or '',
                org_name=self.cleaned_data.get('org_name') or '',
                role_in_org=self.cleaned_data.get('role_in_org') or '',
                phone=self.cleaned_data.get('phone') or '',
                address=self.cleaned_data.get('address') or '',
                client_id=client_id,
            )
        return user


class ProfileUpdateForm(forms.ModelForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = Profile
        fields = [
            'full_name', 'account_type', 'org_name', 'role_in_org',
            'phone', 'address', 'city', 'country', 'profile_image'
        ]

    def clean_full_name(self):
        name = self.cleaned_data.get('full_name', '').strip()
        if name and not all(c.isalpha() or c.isspace() for c in name):
            raise forms.ValidationError('Full name must contain only letters and spaces.')
        return name

    def clean_profile_image(self):
        image = self.cleaned_data.get('profile_image')
        if image:
            if image.size > 1 * 1024 * 1024:
                raise forms.ValidationError('Image must be under 1MB.')
            if hasattr(image, 'content_type') and image.content_type not in ['image/jpeg', 'image/png']:
                raise forms.ValidationError('Only JPG and PNG images are allowed.')
        return image

class PasswordUpdateForm(forms.Form):
    old_password = forms.CharField(widget=forms.PasswordInput)
    new_password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)

    def __init__(self, *args, user: User = None, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned = super().clean()
        old = cleaned.get('old_password')
        new = cleaned.get('new_password')
        confirm = cleaned.get('confirm_password')
        if new and confirm and new != confirm:
            raise forms.ValidationError('New passwords do not match.')
        if self.user and old and not self.user.check_password(old):
            raise forms.ValidationError('Old password is incorrect.')
        # Policy: 8+ chars, upper, lower, digit; allow special
        if new:
            import re
            if not re.search(r'[A-Z]', new) or not re.search(r'[a-z]', new) or not re.search(r'\d', new) or len(new) < 8:
                raise forms.ValidationError('Password must be 8+ chars with upper, lower, and a digit.')
        return cleaned

# Strict form: only send reset if exactly one active account matches the email
from django.contrib.auth.forms import PasswordResetForm

class StrictPasswordResetForm(PasswordResetForm):
    def get_users(self, email):
        email_val = email or ''
        # Case-insensitive exact match on email
        qs = User._default_manager.filter(email__iexact=email_val, is_active=True)
        if qs.count() != 1:
            return []
        user = qs.first()
        if not user.has_usable_password():
            return []
        return [user]

# Enhanced form: accept email or username and still require a single active match
from django.utils.translation import gettext_lazy as _

class UsernameOrEmailPasswordResetForm(PasswordResetForm):
    email = forms.CharField(label=_('Email or Username'), widget=forms.TextInput(attrs={
        'placeholder': 'Email or username',
        'autocomplete': 'email',
    }))

    def get_users(self, value):
        val = (value or '').strip()
        if not val:
            return []
        if '@' in val:
            qs = User._default_manager.filter(email__iexact=val, is_active=True)
        else:
            qs = User._default_manager.filter(username__iexact=val, is_active=True)
        if qs.count() != 1:
            return []
        user = qs.first()
        # Must have an email to send to and a usable password
        if not user.email or not user.has_usable_password():
            return []
        return [user]

class UsernameOrEmailAuthenticationForm(AuthenticationForm):
    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        if username and password:
            val = (username or '').strip()
            resolved_username = val
            try:
                # Try resolve by email, phone, or username (case-insensitive)
                if '@' in val:
                    qs = User._default_manager.filter(email__iexact=val, is_active=True)
                elif val and any(ch.isdigit() for ch in val):
                    qs = User._default_manager.filter(profile__phone__iexact=val, is_active=True)
                else:
                    qs = User._default_manager.filter(username__iexact=val, is_active=True)
                if qs.count() == 1:
                    resolved_username = qs.first().username
            except Exception:
                pass
            self.user_cache = authenticate(self.request, username=resolved_username, password=password)
            if self.user_cache is None:
                raise self.get_invalid_login_error()
            else:
                self.confirm_login_allowed(self.user_cache)
        return self.cleaned_data