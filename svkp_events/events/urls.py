from django.urls import path
from . import views
from .views import (
    EventRegistrationsStaffView,
    ExportRegistrationsExcelView
)

app_name = 'events'

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('events/', views.EventListView.as_view(), name='event_list'),
    path('events/<int:pk>/', views.EventDetailView.as_view(), name='event_detail'),
    path('events/<int:pk>/register/', views.EventRegisterView.as_view(), name='event_register'),
    path('events/create/', views.EventCreateView.as_view(), name='event_create'),
    path('events/<int:pk>/update/', views.EventUpdateView.as_view(), name='event_update'),
    path('my-registrations/', views.MyRegistrationsView.as_view(), name='my_registrations'),
    path('staff/dashboard/', views.StaffDashboardView.as_view(), name='staff_dashboard'),
    path('staff/event/<int:pk>/registrations/',EventRegistrationsStaffView.as_view(),name='staff_event_registrations'),
    path('staff/event/<int:pk>/registrations/excel/',ExportRegistrationsExcelView.as_view(),name='export_registrations_excel'),
]

