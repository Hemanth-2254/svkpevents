from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.decorators import method_decorator
from django.views import View
from django.db.models import Q
from .models import Event, EventRegistration
from .forms import EventForm, EventRegistrationForm
from payments.models import Payment
from openpyxl import Workbook
from django.http import HttpResponse


class HomeView(View):
    def get(self, request):
        upcoming_events = Event.objects.filter(status='upcoming').order_by('start_date')[:6]
        sports_events = Event.objects.filter(event_type='sports', status='upcoming')[:3]
        cultural_events = Event.objects.filter(event_type='cultural', status='upcoming')[:3]
        other_events = Event.objects.filter(event_type='other', status='upcoming')[:3]
        all_events = Event.objects.filter(status__in=['upcoming', 'ongoing']).order_by('start_date')
        context = {
            'upcoming_events': upcoming_events,
            'sports_events': sports_events,
            'cultural_events': cultural_events,
            'other_events': other_events,
            'all_events': all_events,
        }
        return render(request, 'events/home.html', context)


class EventListView(View):
    def get(self, request):
        events = Event.objects.all()
        event_type = request.GET.get('type', '')
        status = request.GET.get('status', '')
        search = request.GET.get('search', '')

        if event_type:
            events = events.filter(event_type=event_type)
        if status:
            events = events.filter(status=status)
        if search:
            events = events.filter(Q(title__icontains=search) | Q(description__icontains=search))

        context = {
            'events': events,
            'event_type': event_type,
            'status': status,
            'search': search,
        }
        return render(request, 'events/event_list.html', context)


class EventDetailView(View):
    def get(self, request, pk):
        event = get_object_or_404(Event, pk=pk)
        user_registration = None
        if request.user.is_authenticated:
            user_registration = EventRegistration.objects.filter(
                event=event, user=request.user
            ).first()
        context = {
            'event': event,
            'user_registration': user_registration,
        }
        return render(request, 'events/event_detail.html', context)


@method_decorator(login_required, name='dispatch')
class EventRegisterView(View):
    def get(self, request, pk):
        event = get_object_or_404(Event, pk=pk)
        if not event.is_registration_open:
            messages.error(request, 'Registration is closed for this event!')
            return redirect('events:event_detail', pk=pk)

        existing = EventRegistration.objects.filter(event=event, user=request.user).first()
        if existing:
            messages.info(request, 'You are already registered for this event!')
            return redirect('events:my_registrations')

        form = EventRegistrationForm(initial={
            'participant_name': request.user.get_full_name(),
            'participant_email': request.user.email,
            'participant_phone': request.user.phone,
        })
        return render(request, 'events/event_register.html', {'event': event, 'form': form})

    def post(self, request, pk):
        event = get_object_or_404(Event, pk=pk)
        if not event.is_registration_open:
            messages.error(request, 'Registration is closed!')
            return redirect('events:event_detail', pk=pk)

        form = EventRegistrationForm(request.POST)
        if form.is_valid():
            registration = form.save(commit=False)
            registration.event = event
            registration.user = request.user
            registration.status = 'pending'
            registration.save()

            # Reduce available seats
            event.available_seats = max(0, event.available_seats - 1)
            event.save()

            messages.success(request, 'Registration successful! Please complete payment.')
            return redirect('payments:payment', registration_id=registration.id)

        return render(request, 'events/event_register.html', {'event': event, 'form': form})


@method_decorator(login_required, name='dispatch')
class MyRegistrationsView(View):
    def get(self, request):
        registrations = EventRegistration.objects.filter(
            user=request.user
        ).select_related('event').order_by('-registered_at')
        return render(request, 'events/my_registrations.html', {'registrations': registrations})


# Staff/Admin only views
@method_decorator(login_required, name='dispatch')
class EventCreateView(View):
    def get(self, request):
        if request.user.user_type not in ['staff'] and not request.user.is_superuser:
            messages.error(request, 'Only staff and admin can create events!')
            return redirect('events:home')
        form = EventForm()
        return render(request, 'events/event_form.html', {'form': form, 'action': 'Create'})

    def post(self, request):
        if request.user.user_type not in ['staff'] and not request.user.is_superuser:
            messages.error(request, 'Only staff and admin can create events!')
            return redirect('events:home')
        form = EventForm(request.POST, request.FILES)
        if form.is_valid():
            event = form.save(commit=False)
            event.created_by = request.user
            event.save()
            messages.success(request, f'Event "{event.title}" created successfully!')
            return redirect('events:event_detail', pk=event.pk)
        return render(request, 'events/event_form.html', {'form': form, 'action': 'Create'})


@method_decorator(login_required, name='dispatch')
class EventUpdateView(View):
    def get(self, request, pk):
        if request.user.user_type not in ['staff'] and not request.user.is_superuser:
            messages.error(request, 'Only staff and admin can update events!')
            return redirect('events:home')
        event = get_object_or_404(Event, pk=pk)
        form = EventForm(instance=event)
        return render(request, 'events/event_form.html', {'form': form, 'action': 'Update', 'event': event})

    def post(self, request, pk):
        if request.user.user_type not in ['staff'] and not request.user.is_superuser:
            messages.error(request, 'Only staff and admin can update events!')
            return redirect('events:home')
        event = get_object_or_404(Event, pk=pk)
        form = EventForm(request.POST, request.FILES, instance=event)
        if form.is_valid():
            event = form.save(commit=False)
            event.updated_by = request.user
            event.save()
            messages.success(request, f'Event "{event.title}" updated successfully!')
            return redirect('events:event_detail', pk=event.pk)
        return render(request, 'events/event_form.html', {'form': form, 'action': 'Update', 'event': event})


@method_decorator(login_required, name='dispatch')
class StaffDashboardView(View):
    def get(self, request):
        if request.user.user_type not in ['staff'] and not request.user.is_superuser:
            messages.error(request, 'Access denied!')
            return redirect('events:home')
        events = Event.objects.all().order_by('-created_at')
        total_registrations = EventRegistration.objects.count()
        confirmed_registrations = EventRegistration.objects.filter(status='confirmed').count()
        context = {
            'events': events,
            'total_registrations': total_registrations,
            'confirmed_registrations': confirmed_registrations,
        }
        return render(request, 'events/staff_dashboard.html', context)

@method_decorator(login_required, name='dispatch')
class EventRegistrationsStaffView(View):
    def get(self, request, pk):
        if request.user.user_type not in ['staff'] and not request.user.is_superuser:
            messages.error(request, 'Access denied!')
            return redirect('events:home')

        event = get_object_or_404(Event, pk=pk)
        registrations = EventRegistration.objects.filter(
            event=event
        ).select_related('user').order_by('-registered_at')

        return render(request, 'events/staff_event_registrations.html', {
            'event': event,
            'registrations': registrations
        })
@method_decorator(login_required, name='dispatch')
class ExportRegistrationsExcelView(View):
    def get(self, request, pk):
        if request.user.user_type not in ['staff'] and not request.user.is_superuser:
            messages.error(request, 'Access denied!')
            return redirect('events:home')

        event = get_object_or_404(Event, pk=pk)
        registrations = EventRegistration.objects.filter(event=event).select_related('user')

        wb = Workbook()
        ws = wb.active
        ws.title = "Registrations"

        ws.append([
            "S.No", "Name", "Email", "Phone",
            "Status", "Registered At"
        ])

        for idx, r in enumerate(registrations, start=1):
            ws.append([
                idx,
                r.participant_name,
                r.participant_email,
                r.participant_phone,
                r.status,
                r.registered_at.strftime("%d-%m-%Y %H:%M"),
            ])

        response = HttpResponse(
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        response["Content-Disposition"] = (
            f'attachment; filename="{event.title}_registrations.xlsx"'
        )

        wb.save(response)
        return response

