from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.decorators import method_decorator
from django.views import View
from django.utils import timezone

from events.models import EventRegistration
from .models import Payment, PaymentQRCode
from .forms import UPIPaymentForm, CardPaymentForm, OfflinePaymentForm, QRCodeUploadForm


@method_decorator(login_required, name='dispatch')
class PaymentView(View):

    def get(self, request, registration_id):
        registration = get_object_or_404(
            EventRegistration, id=registration_id, user=request.user
        )

        event = registration.event

        upi_qr = PaymentQRCode.objects.filter(
            payment_type='upi', is_active=True
        ).first()

        card_qr = PaymentQRCode.objects.filter(
            payment_type='card', is_active=True
        ).first()

        context = {
            'registration': registration,
            'event': event,
            'upi_form': UPIPaymentForm(),
            'card_form': CardPaymentForm(),
            'offline_form': OfflinePaymentForm(),
            'upi_qr': upi_qr,
            'card_qr': card_qr,
        }
        return render(request, 'payments/payment.html', context)

    def post(self, request, registration_id):
        registration = get_object_or_404(
            EventRegistration, id=registration_id, user=request.user
        )

        event = registration.event
        payment_method = request.POST.get('payment_method')

        # ✅ SAFE: Only one payment per registration
        payment, created = Payment.objects.get_or_create(
            registration=registration,
            defaults={
                'user': request.user,
                'payment_method': payment_method,
                'amount': event.fee,
            }
        )

        if payment_method == 'upi':
            form = UPIPaymentForm(request.POST, request.FILES)
            if form.is_valid():
                payment.payment_method = 'upi'
                payment.upi_reference = form.cleaned_data['upi_reference']
                payment.proof = request.FILES.get('payment_proof')
                payment.status = 'completed'
                payment.paid_at = timezone.now()
                payment.save()

                registration.status = 'confirmed'
                registration.save()

                messages.success(request, 'UPI Payment confirmed!')
                return redirect('payments:ticket', registration_id=registration.id)

            messages.error(request, 'Invalid UPI details.')

        elif payment_method == 'card':
            form = CardPaymentForm(request.POST)
            if form.is_valid():
                payment.payment_method = 'card'
                payment.card_last4 = form.cleaned_data['card_number']
                payment.status = 'completed'
                payment.paid_at = timezone.now()
                payment.save()

                registration.status = 'confirmed'
                registration.save()

                messages.success(request, 'Card payment successful!')
                return redirect('payments:ticket', registration_id=registration.id)

            messages.error(request, 'Invalid card details.')

        elif payment_method == 'offline':
            form = OfflinePaymentForm(request.POST)
            if form.is_valid():
                payment.payment_method = 'offline'
                payment.notes = form.cleaned_data.get('notes', '')
                payment.status = 'processing'
                payment.save()

                registration.status = 'pending'
                registration.save()

                messages.success(
                    request,
                    'Offline payment recorded. Pay at college office.'
                )
                return redirect(
                    'payments:pending_ticket',
                    registration_id=registration.id
                )

        # Reload page with errors
        upi_qr = PaymentQRCode.objects.filter(
            payment_type='upi', is_active=True
        ).first()

        card_qr = PaymentQRCode.objects.filter(
            payment_type='card', is_active=True
        ).first()

        context = {
            'registration': registration,
            'event': event,
            'upi_form': UPIPaymentForm(),
            'card_form': CardPaymentForm(),
            'offline_form': OfflinePaymentForm(),
            'upi_qr': upi_qr,
            'card_qr': card_qr,
        }
        return render(request, 'payments/payment.html', context)


@method_decorator(login_required, name='dispatch')
class TicketView(View):
    def get(self, request, registration_id):
        registration = get_object_or_404(
            EventRegistration,
            id=registration_id,
            user=request.user,
            status='confirmed'
        )

        payment = registration.payment

        return render(request, 'payments/ticket.html', {
            'registration': registration,
            'payment': payment,
            'event': registration.event,
        })


@method_decorator(login_required, name='dispatch')
class PendingTicketView(View):
    def get(self, request, registration_id):
        registration = get_object_or_404(
            EventRegistration, id=registration_id, user=request.user
        )
        return render(request, 'payments/pending_ticket.html', {
            'registration': registration,
            'event': registration.event,
        })


@method_decorator(login_required, name='dispatch')
class QRCodeManageView(View):

    def get(self, request):
        if not request.user.is_staff and not request.user.is_superuser:
            messages.error(request, 'Access denied!')
            return redirect('events:home')

        qr_codes = PaymentQRCode.objects.all().order_by('-created_at')
        form = QRCodeUploadForm()
        return render(
            request,
            'payments/qr_manage.html',
            {'qr_codes': qr_codes, 'form': form}
        )

    def post(self, request):
        if not request.user.is_staff and not request.user.is_superuser:
            messages.error(request, 'Access denied!')
            return redirect('events:home')

        form = QRCodeUploadForm(request.POST, request.FILES)
        if form.is_valid():
            qr = form.save(commit=False)
            qr.uploaded_by = request.user
            qr.save()
            messages.success(request, 'QR Code uploaded successfully!')
            return redirect('payments:qr_manage')

        qr_codes = PaymentQRCode.objects.all().order_by('-created_at')
        return render(
            request,
            'payments/qr_manage.html',
            {'qr_codes': qr_codes, 'form': form}
        )