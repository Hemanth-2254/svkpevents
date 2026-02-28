from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, OTPVerification


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ['username', 'get_full_name', 'user_type', 'phone', 'department', 'is_phone_verified']
    list_filter = ['user_type', 'is_phone_verified', 'is_active']
    search_fields = ['username', 'first_name', 'last_name', 'phone', 'email']
    fieldsets = UserAdmin.fieldsets + (
        ('College Info', {'fields': ('user_type', 'phone', 'roll_number', 'employee_id', 'department', 'address', 'profile_pic', 'is_phone_verified')}),
    )


@admin.register(OTPVerification)
class OTPVerificationAdmin(admin.ModelAdmin):
    list_display = ['phone', 'otp_code', 'purpose', 'is_used', 'created_at', 'expires_at']
    list_filter = ['purpose', 'is_used']
    readonly_fields = ['created_at', 'expires_at']
