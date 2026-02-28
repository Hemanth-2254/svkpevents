from django import forms
from .models import Event, EventRegistration


class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['title', 'event_type', 'description', 'venue', 'start_date',
                  'end_date', 'registration_deadline', 'total_seats', 'available_seats',
                  'fee', 'image', 'status', 'is_college_only']
        widgets = {
            'start_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'end_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'registration_deadline': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'description': forms.Textarea(attrs={'rows': 4}),
        }


class EventRegistrationForm(forms.ModelForm):
    class Meta:
        model = EventRegistration
        fields = ['participant_name', 'participant_email', 'participant_phone']
        widgets = {
            'participant_name': forms.TextInput(attrs={'placeholder': 'Full Name'}),
            'participant_email': forms.EmailInput(attrs={'placeholder': 'Email Address'}),
            'participant_phone': forms.TextInput(attrs={'placeholder': 'Phone Number'}),
        }
