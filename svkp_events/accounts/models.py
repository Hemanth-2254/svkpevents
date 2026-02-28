from django.contrib.auth.models import AbstractUser
from django.db import models
import random
import datetime
from django.utils import timezone


class CustomUser(AbstractUser):
    USER_TYPES = (
        ('student', 'Student'),
        ('staff', 'Staff'),
        ('other', 'Other'),
    )
    user_type = models.CharField(max_length=10, choices=USER_TYPES, default='other')
    phone = models.CharField(max_length=15, unique=True)
    roll_number = models.CharField(max_length=20, blank=True, null=True)  # for students
    department = models.CharField(max_length=100, blank=True, null=True)
    employee_id = models.CharField(max_length=20, blank=True, null=True)  # for staff
    is_email_verified = models.BooleanField(default=False)
    is_phone_verified = models.BooleanField(default=False)
    profile_pic = models.ImageField(upload_to='profiles/', blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'custom_users'

    def __str__(self):
        return f"{self.get_full_name()} ({self.user_type})"


class OTPVerification(models.Model):
    OTP_PURPOSES = (
        ('registration', 'Registration'),
        ('login', 'Login'),
        ('password_reset', 'Password Reset'),
    )
    phone = models.CharField(max_length=15)
    otp_code = models.CharField(max_length=6)
    purpose = models.CharField(max_length=20, choices=OTP_PURPOSES)
    is_used = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    class Meta:
        db_table = 'otp_verifications'

    def save(self, *args, **kwargs):
        if not self.pk:
            self.expires_at = timezone.now() + datetime.timedelta(minutes=10)
        super().save(*args, **kwargs)

    def is_valid(self):
        return not self.is_used and timezone.now() < self.expires_at

    @classmethod
    def generate_otp(cls, phone, purpose):
        # Invalidate previous OTPs
        cls.objects.filter(phone=phone, purpose=purpose, is_used=False).update(is_used=True)
        otp_code = str(random.randint(100000, 999999))
        otp = cls.objects.create(phone=phone, otp_code=otp_code, purpose=purpose)
        # Print OTP to CMD/console as required
        print("\n" + "="*60)
        print(f"  SVKP COLLEGE - OTP VERIFICATION")
        print(f"  Phone: {phone}")
        print(f"  Purpose: {purpose.upper()}")
        print(f"  OTP Code: {otp_code}")
        print(f"  Valid for: 10 minutes")
        print("="*60 + "\n")
        return otp_code

    def __str__(self):
        return f"OTP for {self.phone} - {self.purpose}"
