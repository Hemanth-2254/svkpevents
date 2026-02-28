from django.contrib import admin
from .models import Payment, PaymentQRCode


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['transaction_id', 'registration', 'payment_method', 'amount', 'status', 'paid_at']
    list_filter = ['payment_method', 'status']
    search_fields = ['transaction_id', 'upi_reference']
    readonly_fields = ['transaction_id', 'created_at', 'updated_at']


@admin.register(PaymentQRCode)
class PaymentQRCodeAdmin(admin.ModelAdmin):
    list_display = ['title', 'payment_type', 'upi_id', 'is_active', 'uploaded_by', 'created_at']
    list_filter = ['payment_type', 'is_active']
