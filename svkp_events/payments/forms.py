from django import forms
from .models import Payment, PaymentQRCode


class UPIPaymentForm(forms.Form):
    upi_reference = forms.CharField(
        max_length=100,
        label='UPI Transaction Reference / UTR Number',
        widget=forms.TextInput(attrs={'placeholder': 'Enter UTR/Reference Number after payment'})
    )
    payment_proof = forms.ImageField(
        required=False,
        label='Payment Screenshot (Optional)'
    )


class CardPaymentForm(forms.Form):
    card_number = forms.CharField(max_length=19, widget=forms.TextInput(attrs={'placeholder': 'Card Number'}))
    card_holder = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'placeholder': 'Card Holder Name'}))
    expiry = forms.CharField(max_length=7, widget=forms.TextInput(attrs={'placeholder': 'MM/YYYY'}))
    cvv = forms.CharField(max_length=4, widget=forms.TextInput(attrs={'placeholder': 'CVV', 'type': 'password'}))

    def clean_card_number(self):
        number = self.cleaned_data['card_number'].replace(' ', '').replace('-', '')
        if not number.isdigit() or len(number) < 15:
            raise forms.ValidationError('Invalid card number')
        return number[-4:]  # Only store last 4 digits


class OfflinePaymentForm(forms.Form):
    notes = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3, 'placeholder': 'Any notes for offline payment (optional)'}),
        required=False,
        label='Notes'
    )


class QRCodeUploadForm(forms.ModelForm):
    class Meta:
        model = PaymentQRCode
        fields = ['payment_type', 'title', 'qr_image', 'upi_id', 'is_active']
