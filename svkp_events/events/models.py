from django.db import models
from django.conf import settings


class Event(models.Model):
    EVENT_TYPES = (
        ('sports', 'Sports'),
        ('cultural', 'Cultural Activities'),
        ('academic', 'Academic'),
        ('technical', 'Technical'),
        ('other', 'Other Events'),
    )
    STATUS_CHOICES = (
        ('upcoming', 'Upcoming'),
        ('ongoing', 'Ongoing'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    )

    title = models.CharField(max_length=200)
    event_type = models.CharField(max_length=20, choices=EVENT_TYPES)
    description = models.TextField()
    venue = models.CharField(max_length=200)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    registration_deadline = models.DateTimeField()
    total_seats = models.PositiveIntegerField()
    available_seats = models.PositiveIntegerField()
    fee = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    image = models.ImageField(upload_to='event_images/', blank=True, null=True)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='upcoming')
    is_college_only = models.BooleanField(default=True, help_text='College events only')
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, related_name='created_events'
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='updated_events'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'events'
        ordering = ['-start_date']

    def __str__(self):
        return f"{self.title} ({self.get_event_type_display()})"

    @property
    def is_registration_open(self):
        from django.utils import timezone
        return (self.status == 'upcoming' and
                self.available_seats > 0 and
                timezone.now() < self.registration_deadline)

    @property
    def registered_count(self):
        return self.registrations.filter(status='confirmed').count()


class EventRegistration(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending Payment'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
    )

    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='registrations')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='registrations')
    ticket_number = models.CharField(max_length=20, unique=True)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='pending')
    registered_at = models.DateTimeField(auto_now_add=True)
    participant_name = models.CharField(max_length=200)
    participant_email = models.EmailField()
    participant_phone = models.CharField(max_length=15)

    class Meta:
        db_table = 'event_registrations'
        unique_together = ['event', 'user']

    def __str__(self):
        return f"{self.ticket_number} - {self.participant_name} - {self.event.title}"

    def save(self, *args, **kwargs):
        if not self.ticket_number:
            import random, string
            self.ticket_number = 'SVKP' + ''.join(random.choices(string.digits, k=8))
        super().save(*args, **kwargs)
