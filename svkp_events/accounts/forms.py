from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser


class StudentRegistrationForm(UserCreationForm):
    first_name = forms.CharField(max_length=100, required=True)
    last_name = forms.CharField(max_length=100, required=True)
    email = forms.EmailField(required=True)
    phone = forms.CharField(max_length=15, required=True)
    roll_number = forms.CharField(max_length=20, required=True)
    department = forms.CharField(max_length=100, required=True)
    address = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}), required=False)

    class Meta:
        model = CustomUser
        fields = ['username', 'first_name', 'last_name', 'email', 'phone',
                  'roll_number', 'department', 'address', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.user_type = 'student'
        if commit:
            user.save()
        return user


class StaffRegistrationForm(UserCreationForm):
    first_name = forms.CharField(max_length=100, required=True)
    last_name = forms.CharField(max_length=100, required=True)
    email = forms.EmailField(required=True)
    phone = forms.CharField(max_length=15, required=True)
    employee_id = forms.CharField(max_length=20, required=True)
    department = forms.CharField(max_length=100, required=True)
    address = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}), required=False)

    class Meta:
        model = CustomUser
        fields = ['username', 'first_name', 'last_name', 'email', 'phone',
                  'employee_id', 'department', 'address', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.user_type = 'staff'
        if commit:
            user.save()
        return user


class OtherRegistrationForm(UserCreationForm):
    first_name = forms.CharField(max_length=100, required=True)
    last_name = forms.CharField(max_length=100, required=True)
    email = forms.EmailField(required=True)
    phone = forms.CharField(max_length=15, required=True)
    address = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}), required=False)

    class Meta:
        model = CustomUser
        fields = ['username', 'first_name', 'last_name', 'email', 'phone',
                  'address', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.user_type = 'other'
        if commit:
            user.save()
        return user


class OTPForm(forms.Form):
    otp_code = forms.CharField(
        max_length=6,
        min_length=6,
        label='Enter OTP',
        widget=forms.TextInput(attrs={'placeholder': 'Enter 6-digit OTP', 'autocomplete': 'off', 'class': 'otp-input'})
    )


class PhoneForm(forms.Form):
    phone = forms.CharField(
        max_length=15,
        label='Phone Number',
        widget=forms.TextInput(attrs={'placeholder': 'Enter your phone number'})
    )


class LoginForm(forms.Form):
    username = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': 'Username'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Password'})
    )
    phone = forms.CharField(
        max_length=15,
        widget=forms.TextInput(attrs={'placeholder': 'Phone for OTP verification'})
    )
