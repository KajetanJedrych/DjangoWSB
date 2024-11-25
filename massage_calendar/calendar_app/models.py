# models.py
from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils import timezone


class Service(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    duration = models.PositiveIntegerField(help_text="Duration in minutes")
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Employee(models.Model):
    name = models.CharField(max_length=100)
    specialization = models.CharField(max_length=100, blank=True, null=True)
    services = models.ManyToManyField(Service, related_name='employees')
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Availability(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()

    class Meta:
        ordering = ['date', 'start_time']
        verbose_name_plural = "Availabilities"

    def clean(self):
        if self.start_time >= self.end_time:
            raise ValidationError("End time must be after start time")
        if self.date < timezone.now().date():
            raise ValidationError("Cannot set availability for past dates")

    def __str__(self):
        return f"{self.employee.name} - {self.date}"


class Appointment(models.Model):
    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('no_show', 'No Show'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    date = models.DateField()
    time = models.TimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    notes = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['date', 'time']

    def clean(self):
        # Check if appointment is in the past
        appointment_datetime = timezone.datetime.combine(self.date, self.time)
        if appointment_datetime < timezone.now():
            raise ValidationError("Cannot create appointments in the past")

        # Check if employee is available
        availability = Availability.objects.filter(
            employee=self.employee,
            date=self.date,
            start_time__lte=self.time,
            end_time__gte=self.time
        )
        if not availability.exists():
            raise ValidationError("Employee is not available at this time")

        # Check for overlapping appointments
        overlapping = Appointment.objects.filter(
            employee=self.employee,
            date=self.date,
            time=self.time,
            status='scheduled'
        ).exclude(id=self.id)

        if overlapping.exists():
            raise ValidationError("This time slot is already booked")

    def __str__(self):
        return f"{self.user.username} - {self.service.name} on {self.date} at {self.time}"