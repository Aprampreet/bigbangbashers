from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone # Import timezone for another helpful property
from django.core.exceptions import ValidationError

class Event(models.Model):
    admin = models.ForeignKey(User, on_delete=models.CASCADE, related_name="admin_events")
    name = models.CharField(max_length=200)
    date = models.DateField()
    registration_end = models.DateField()
    time = models.TimeField()
    venue = models.CharField(max_length=300, default="Will be Disclosed")
    ticket_price = models.DecimalField(max_digits=8, decimal_places=2)
    banner_image = models.ImageField(upload_to='event_banners/')
    key_points = models.TextField(help_text="Enter event highlights / bullet points")
    whatsapp_group = models.CharField(max_length=500,null=True , blank= True)

    def clean(self):
        if self.registration_end and self.date and self.registration_end > self.date:
            raise ValidationError({
                'registration_end': "Registration end date cannot be after the event date."
            })

    def __str__(self):
        return self.name
    
    @property
    def total_revenue(self):

        num_registrations = self.registrations.count()
        return self.ticket_price * num_registrations

    @property
    def is_registration_open(self):
        return timezone.now().date() <= self.registration_end and timezone.now().date() <= self.date

    @property
    def is_finished(self):
        return timezone.now().date() > self.date


class EventRegistration(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='registrations')
    Student_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    collage_name = models.CharField(max_length=500,default='Guru Nanak Dev University')
    is_hostler = models.BooleanField()
    department = models.CharField(max_length=100)
    year = models.CharField(max_length=10)
    course = models.CharField(max_length=100)
    registration_date = models.DateTimeField(auto_now_add=True)
    payment_screenshot = models.ImageField(upload_to='payment_screenshots/')
    
    def __str__(self):
        return f"{self.Student_name} - {self.event.name}"