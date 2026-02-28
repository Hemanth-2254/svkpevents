from django.contrib import admin
from .models import Event, EventRegistration


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ['title', 'event_type', 'status', 'start_date', 'total_seats', 'available_seats', 'fee']
    list_filter = ['event_type', 'status', 'is_college_only']
    search_fields = ['title', 'description', 'venue']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(EventRegistration)
class EventRegistrationAdmin(admin.ModelAdmin):
    list_display = ['ticket_number', 'participant_name', 'event', 'status', 'registered_at']
    list_filter = ['status', 'event__event_type']
    search_fields = ['ticket_number', 'participant_name', 'participant_email']
    readonly_fields = ['ticket_number', 'registered_at']
