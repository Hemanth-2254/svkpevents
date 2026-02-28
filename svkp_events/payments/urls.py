from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('pay/<int:registration_id>/', views.PaymentView.as_view(), name='payment'),
    path('ticket/<int:registration_id>/', views.TicketView.as_view(), name='ticket'),
    path('pending/<int:registration_id>/', views.PendingTicketView.as_view(), name='pending_ticket'),
    path('qr-codes/', views.QRCodeManageView.as_view(), name='qr_manage'),
]
