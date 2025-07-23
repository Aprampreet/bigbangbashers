from django.shortcuts import render, redirect, get_object_or_404,HttpResponse
from .models import Event, EventRegistration
from django.contrib.auth.decorators import login_required, user_passes_test
from django.forms import ModelForm
from django import forms
from django.contrib import messages
from django.urls import reverse
from django.utils import timezone
from .tasks import send_email_async
import csv
from urllib.parse import quote,urlencode



class EventForm(ModelForm):
    date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    registration_end = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    time = forms.TimeField(widget=forms.TimeInput(attrs={'type': 'time'}))

    class Meta:
        model = Event
        fields = [
            'name', 'date', 'registration_end', 'time', 'venue',
            'ticket_price', 'whatsapp_group', 'banner_image', 'key_points'
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'placeholder': 'Event Name'
            }),
            'venue': forms.TextInput(attrs={
                'placeholder': 'Venue (e.g., Main Auditorium)'
            }),
            'ticket_price': forms.NumberInput(attrs={
                'placeholder': 'e.g., 500.00'
            }),
            'key_points': forms.Textarea(attrs={
                'placeholder': 'Enter event highlights / bullet points, each on a new line',
                'rows': 5
            }),
            'date': forms.DateInput(attrs={'type': 'date'}),
            'registration_end': forms.DateInput(attrs={'type': 'date'}),
            'time': forms.TimeInput(attrs={'type': 'time'}),
        }



class EventRegistrationForm(ModelForm):
    class Meta:
        model = EventRegistration
        exclude = ['user', 'event', 'registration_date'] 
        widgets = {
            'Student_name': forms.TextInput(attrs={'placeholder': 'Your Full Name'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Your Email'}),
            'phone': forms.TextInput(attrs={'placeholder': 'Your Phone Number'}),
            'department': forms.TextInput(attrs={'placeholder': 'Your Department'}),
            'year': forms.TextInput(attrs={'placeholder': 'Your Academic Year'}),
            'course': forms.TextInput(attrs={'placeholder': 'Your Course'}),
        }

def event_list_view(request):
    events = Event.objects.all().order_by('-date')
    context = {
        'events': events,
        'today': timezone.now().date(), # Pass today's date to the template
    }
    return render(request, 'core/event_list.html', context)

@login_required
def event_detail_view(request, pk):
    event = get_object_or_404(Event, pk=pk)
    today = timezone.now().date()
    registration_end_datetime_iso = event.registration_end.isoformat() if event.registration_end else None
    return render(request, 'core/event_detail.html', {'event': event, 'today': today, 'registration_end_datetime_iso': registration_end_datetime_iso, 'is_registration_open': event.is_registration_open})

@login_required
@user_passes_test(lambda u: u.is_staff)
def event_create_view(request):
    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES)
        if form.is_valid():
            event = form.save(commit=False)
            event.admin = request.user
            event.save()
            messages.success(request, 'Event created successfully!')
            return redirect('event_detail', pk=event.pk)
    else:
        form = EventForm()
    return render(request, 'core/event_form.html', {'form': form, 'form_title': 'Create New Event'})

@login_required
def event_register_view(request, pk):
    event = get_object_or_404(Event, pk=pk)
    
    if not event.is_registration_open:
        messages.error(request, "Registration for this event has closed.")
        return redirect('event_detail', pk=event.pk)
    upi_link = f"upi://pay?{urlencode({
        'pa': '7855800005@ptaxis',
        'pn': request.user.username,
        'am': f'{event.ticket_price:.2f}',
        'cu': 'INR'
    })}"

    # For Google Charts QR (note: single slash after upi:)
    qr_payload = upi_link.replace("upi://", "upi:/")
    qr_code_url = f"https://chart.googleapis.com/chart?chs=180x180&cht=qr&chl={quote(qr_payload)}"

    if request.method == 'POST':
        form = EventRegistrationForm(request.POST, request.FILES)
        if form.is_valid():

            registration = form.save(commit=False)
            registration.user = request.user
            registration.event = event
            registration.save()
            user_email = registration.email
            admin_email = event.admin.email
            your_email = "bigbangbashers@gmail.com"

            event_details = (
            f"Event Name: {event.name}\n"
            f"Date: {event.date.strftime('%A, %B %d, %Y')}\n"
            f"Time: {event.time.strftime('%I:%M %p')}\n"
            f"Venue: {event.venue}\n"
        )

            # Email to user (confirmation)
            send_email_async.delay(
            subject=f"🎉 Registration Confirmed – {event.name}",
            message=(
                f"Hi {registration.Student_name},\n\n"
                f"🎊 You’ve successfully registered for *{event.name}*! We’re thrilled to have you with us.\n\n"
                f"📅 **Event Details:**\n"
                f"• Event: {event.name}\n"
                f"• Date: {event.date.strftime('%A, %d %B %Y')}\n"
                f"• Time: {event.time.strftime('%I:%M %p')}\n"
                f"• Venue: {event.venue}\n\n"
                f"📢 *Stay connected with all event updates, reminders, and announcements!*\n"
                f"Join our official WhatsApp group:\n👉 {registration.event.whatsapp_group}\n\n"
                f"📝 Save the date and keep an eye on your inbox — we’ll be sending reminders as the event approaches.\n\n"
                f"If you have any questions, feel free to reach out.\n\n"
                f"Best regards,\n"
                f"Team EventHub – Big Bang Bashers"
            ),
            recipient_list=[user_email],
        )


            # Email to your central inbox
            send_email_async.delay(
                subject=f"🔔 New Registration Notification – {event.name}",
                message=(
                    f"A participant has registered for the event \"{event.name}\".\n\n"
                    f"👤 **Registrant Details:**\n"
                    f"- Name: {registration.Student_name}\n"
                    f"- Email: {user_email}\n"
                    f"- Phone: {registration.phone}\n"
                    f"- Department: {registration.department}\n"
                    f"- Year: {registration.year}\n"
                    f"- Course: {registration.course}\n\n"
                    f"**Event Info:**\n{event_details}\n"
                ),
                recipient_list=["bigbangbashers@gmail.com"],
            )




            messages.success(request, 'Successfully registered for the event! A confirmation email has been sent.')
            return redirect('my_registrations') 
    else:
        form = EventRegistrationForm()
    return render(request, 'core/event_register.html', {'form': form, 'event': event,'upi_link': upi_link,'qr_code_url': qr_code_url,})

@login_required
def my_registrations_view(request):
    registrations = EventRegistration.objects.filter(user=request.user).order_by('-registration_date')
    return render(request, 'core/my_registrations.html', {'registrations': registrations})


@login_required
@user_passes_test(lambda u: u.is_staff)
def export_event_registrations_csv(request, pk):
    event = get_object_or_404(Event, pk=pk)

    if request.user != event.admin:
        messages.error(request, "You are not authorized to export registrations for this event.")
        return redirect('admin_my_events')

    registrations = EventRegistration.objects.filter(event=event).order_by('-registration_date')

    # Prepare CSV response
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{event.name}_registrations.csv"'

    writer = csv.writer(response)
    writer.writerow(['Name',
        'Email',
        'Phone',
        'College Name',
        'Hosteller (Yes/No)',
        'Department',
        'Year',
        'Course',
        'Registration Date',])

    for reg in registrations:
        writer.writerow([
            reg.Student_name,
            reg.email,
            reg.phone,
            reg.collage_name,
            'Yes' if reg.is_hostler else 'No',
            reg.department,
            reg.year,
            reg.course,
            reg.registration_date.strftime("%Y-%m-%d %H:%M"),
        ])

    return response

@login_required
@user_passes_test(lambda u: u.is_staff)
def admin_event_registrations_view(request, pk):
    event = get_object_or_404(Event, pk=pk)
    if request.user != event.admin:
        messages.error(request, "You are not authorized to view registrations for this event.")
        return redirect('admin_my_events') # Redirect to their own events list

    registrations = EventRegistration.objects.filter(event=event).order_by('-registration_date')
    return render(request, 'core/admin_event_registrations.html', {'event': event, 'registrations': registrations})

def home_view(request):
    latest_event = Event.objects.order_by('-date').first()
    return render(request, 'core/home.html', {'latest_event': latest_event})

@login_required
@user_passes_test(lambda u: u.is_staff)
def admin_my_events_view(request):
    my_events = Event.objects.filter(admin=request.user).order_by('-date')
    today = timezone.localdate()
    return render(request, 'core/admin_my_events.html', {'my_events': my_events,'today': today,})


@login_required
@user_passes_test(lambda u: u.is_staff)
def delete_event(request, pk):
    event = get_object_or_404(Event, pk=pk)
    
    if request.method == "POST":
        event.delete()
        messages.success(request, "Event deleted successfully.")
        return redirect("event_list")  

    return redirect("event_detail", pk=pk)

@login_required
@user_passes_test(lambda u: u.is_staff)
def edit_event(request,pk):
    event = get_object_or_404(Event,pk=pk)
    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES, instance=event)
        if form.is_valid():
            form.save()
            messages.success(request, "Event updated successfully.")
            return redirect('event_detail', pk=event.pk) 
    else:
        form = EventForm(instance=event)
    return render(request, "core/edit_event.html", {"form": form, "event": event})


def custom_404_view(request, exception):
    return render(request, '404.html', status=404)