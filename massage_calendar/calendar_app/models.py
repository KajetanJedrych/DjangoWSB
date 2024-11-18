from django.db import models
from django.conf import settings

# Usługi
class Service(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    duration = models.PositiveIntegerField(help_text="Duration in minutes")

    def __str__(self):
        return self.name

# Pracownicy
class Employee(models.Model):
    name = models.CharField(max_length=100)
    specialization = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.name

# Dostępność pracowników
class Availability(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()

    def __str__(self):
        return f"{self.employee.name} - {self.date}"

# Wizyty
class Appointment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  # Użytkownik powiązany z wizytą
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    date = models.DateField()
    time = models.TimeField()

    def __str__(self):
        return f"{self.user.username} - {self.service.name} on {self.date} at {self.time}"
