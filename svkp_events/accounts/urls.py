from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('register/', views.RegisterChoiceView.as_view(), name='register_choice'),
    path('register/student/', views.StudentRegisterView.as_view(), name='register_student'),
    path('register/staff/', views.StaffRegisterView.as_view(), name='register_staff'),
    path('register/other/', views.OtherRegisterView.as_view(), name='register_other'),
    path('register/verify-otp/', views.VerifyOTPRegisterView.as_view(), name='verify_otp_register'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('login/verify-otp/', views.VerifyOTPLoginView.as_view(), name='verify_otp_login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
]
