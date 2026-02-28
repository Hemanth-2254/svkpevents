from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.views import View
from .models import CustomUser, OTPVerification
from .forms import (StudentRegistrationForm, StaffRegistrationForm,
                    OtherRegistrationForm, OTPForm, LoginForm, PhoneForm)


class RegisterChoiceView(View):
    def get(self, request):
        return render(request, 'accounts/register_choice.html')


class StudentRegisterView(View):
    def get(self, request):
        form = StudentRegistrationForm()
        return render(request, 'accounts/register.html', {'form': form, 'user_type': 'Student', 'step': 1})

    def post(self, request):
        form = StudentRegistrationForm(request.POST)
        if form.is_valid():
            phone = form.cleaned_data['phone']
            # Check phone uniqueness
            if CustomUser.objects.filter(phone=phone).exists():
                messages.error(request, 'Phone number already registered!')
                return render(request, 'accounts/register.html', {'form': form, 'user_type': 'Student', 'step': 1})
            # Store form data in session
            request.session['reg_data'] = request.POST.dict()
            request.session['reg_type'] = 'student'
            # Generate OTP
            OTPVerification.generate_otp(phone, 'registration')
            messages.success(request, f'OTP sent to {phone}. Check the server console!')
            return redirect('accounts:verify_otp_register')
        return render(request, 'accounts/register.html', {'form': form, 'user_type': 'Student', 'step': 1})


class StaffRegisterView(View):
    def get(self, request):
        form = StaffRegistrationForm()
        return render(request, 'accounts/register.html', {'form': form, 'user_type': 'Staff', 'step': 1})

    def post(self, request):
        form = StaffRegistrationForm(request.POST)
        if form.is_valid():
            phone = form.cleaned_data['phone']
            if CustomUser.objects.filter(phone=phone).exists():
                messages.error(request, 'Phone number already registered!')
                return render(request, 'accounts/register.html', {'form': form, 'user_type': 'Staff', 'step': 1})
            request.session['reg_data'] = request.POST.dict()
            request.session['reg_type'] = 'staff'
            OTPVerification.generate_otp(phone, 'registration')
            messages.success(request, f'OTP sent to {phone}. Check the server console!')
            return redirect('accounts:verify_otp_register')
        return render(request, 'accounts/register.html', {'form': form, 'user_type': 'Staff', 'step': 1})


class OtherRegisterView(View):
    def get(self, request):
        form = OtherRegistrationForm()
        return render(request, 'accounts/register.html', {'form': form, 'user_type': 'Other', 'step': 1})

    def post(self, request):
        form = OtherRegistrationForm(request.POST)
        if form.is_valid():
            phone = form.cleaned_data['phone']
            if CustomUser.objects.filter(phone=phone).exists():
                messages.error(request, 'Phone number already registered!')
                return render(request, 'accounts/register.html', {'form': form, 'user_type': 'Other', 'step': 1})
            request.session['reg_data'] = request.POST.dict()
            request.session['reg_type'] = 'other'
            OTPVerification.generate_otp(phone, 'registration')
            messages.success(request, f'OTP sent to {phone}. Check the server console!')
            return redirect('accounts:verify_otp_register')
        return render(request, 'accounts/register.html', {'form': form, 'user_type': 'Other', 'step': 1})


class VerifyOTPRegisterView(View):
    def get(self, request):
        if 'reg_data' not in request.session:
            return redirect('accounts:register_choice')
        form = OTPForm()
        return render(request, 'accounts/verify_otp.html', {'form': form, 'purpose': 'Registration'})

    def post(self, request):
        form = OTPForm(request.POST)
        if form.is_valid():
            otp_entered = form.cleaned_data['otp_code']
            reg_data = request.session.get('reg_data', {})
            reg_type = request.session.get('reg_type', 'other')
            phone = reg_data.get('phone')

            otp_obj = OTPVerification.objects.filter(
                phone=phone, purpose='registration', is_used=False
            ).order_by('-created_at').first()

            if otp_obj and otp_obj.is_valid() and otp_obj.otp_code == otp_entered:
                otp_obj.is_used = True
                otp_obj.save()

                # Create the user
                if reg_type == 'student':
                    form_class = StudentRegistrationForm
                elif reg_type == 'staff':
                    form_class = StaffRegistrationForm
                else:
                    form_class = OtherRegistrationForm

                user_form = form_class(reg_data)
                if user_form.is_valid():
                    user = user_form.save(commit=False)
                    user.is_phone_verified = True
                    user.save()
                    del request.session['reg_data']
                    del request.session['reg_type']
                    login(request, user)
                    messages.success(request, f'Registration successful! Welcome {user.get_full_name()}!')
                    return redirect('events:home')
                else:
                    messages.error(request, 'Registration error. Please try again.')
                    return redirect('accounts:register_choice')
            else:
                messages.error(request, 'Invalid or expired OTP. Please try again.')

        return render(request, 'accounts/verify_otp.html', {'form': form, 'purpose': 'Registration'})


class LoginView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('events:home')
        form = LoginForm()
        return render(request, 'accounts/login.html', {'form': form})

    def post(self, request):
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            phone = form.cleaned_data['phone']

            user = authenticate(request, username=username, password=password)
            if user:
                if user.phone != phone:
                    messages.error(request, 'Phone number does not match your account!')
                    return render(request, 'accounts/login.html', {'form': form})
                # Generate login OTP
                OTPVerification.generate_otp(phone, 'login')
                request.session['login_user_id'] = user.id
                messages.success(request, f'OTP sent to {phone}. Check the server console!')
                return redirect('accounts:verify_otp_login')
            else:
                messages.error(request, 'Invalid username or password!')

        return render(request, 'accounts/login.html', {'form': form})


class VerifyOTPLoginView(View):
    def get(self, request):
        if 'login_user_id' not in request.session:
            return redirect('accounts:login')
        form = OTPForm()
        return render(request, 'accounts/verify_otp.html', {'form': form, 'purpose': 'Login'})

    def post(self, request):
        form = OTPForm(request.POST)
        if form.is_valid():
            otp_entered = form.cleaned_data['otp_code']
            user_id = request.session.get('login_user_id')

            try:
                user = CustomUser.objects.get(id=user_id)
                otp_obj = OTPVerification.objects.filter(
                    phone=user.phone, purpose='login', is_used=False
                ).order_by('-created_at').first()

                if otp_obj and otp_obj.is_valid() and otp_obj.otp_code == otp_entered:
                    otp_obj.is_used = True
                    otp_obj.save()
                    del request.session['login_user_id']
                    login(request, user)
                    messages.success(request, f'Welcome back, {user.get_full_name()}!')
                    return redirect('events:home')
                else:
                    messages.error(request, 'Invalid or expired OTP!')
            except CustomUser.DoesNotExist:
                messages.error(request, 'User not found!')

        return render(request, 'accounts/verify_otp.html', {'form': form, 'purpose': 'Login'})


class LogoutView(View):
    def get(self, request):
        logout(request)
        messages.success(request, 'Logged out successfully!')
        return redirect('events:home')


class ProfileView(View):
    def get(self, request):
        if not request.user.is_authenticated:
            return redirect('accounts:login')
        return render(request, 'accounts/profile.html', {'user': request.user})
