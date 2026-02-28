from django.db import models
from django.conf import settings
import random
import string


class PaymentQRCode(models.Model):
    PAYMENT_TYPES = (
        ('upi', 'UPI'),
        ('card', 'Card'),
    )

    payment_type = models.CharField(max_length=10, choices=PAYMENT_TYPES)
    title = models.CharField(max_length=100)
    qr_image = models.ImageField(upload_to='qr_codes/')
    upi_id = models.CharField(max_length=100, blank=True, null=True)
    is_active = models.BooleanField(default=True)

    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'payment_qr_codes'

    def __str__(self):
        return self.title


class Payment(models.Model):
    PAYMENT_METHODS = (
        ('upi', 'UPI'),
        ('card', 'Card / Net Banking'),
        ('offline', 'Offline / Cash'),
    )

    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    )

    registration = models.OneToOneField(
        'events.EventRegistration',
        on_delete=models.CASCADE,
        related_name='payment'
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='payments'
    )

    payment_method = models.CharField(max_length=10, choices=PAYMENT_METHODS)
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    transaction_id = models.CharField(
        max_length=20,
        unique=True,
        editable=False
    )

    upi_reference = models.CharField(max_length=100, blank=True, null=True)
    card_last4 = models.CharField(max_length=4, blank=True, null=True)

    status = models.CharField(
        max_length=15,
        choices=STATUS_CHOICES,
        default='pending'
    )

    proof = models.ImageField(
        upload_to='payment_proofs/',
        blank=True,
        null=True
    )

    notes = models.TextField(blank=True, null=True)
    paid_at = models.DateTimeField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'payments'

    def __str__(self):
        return f"Payment {self.id} - {self.status}"

    def save(self, *args, **kwargs):
        if not self.transaction_id:
            self.transaction_id = self.generate_txn_id()
        super().save(*args, **kwargs)

    @staticmethod
    def generate_txn_id():
        return 'TXN' + ''.join(
            random.choices(string.ascii_uppercase + string.digits, k=10)
        )