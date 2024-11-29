# In your_app/management/commands/generate_availabilities.py
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import datetime, timedelta, date
from massage_calendar.calendar_app.models import Employee, Availability


class Command(BaseCommand):
    help = 'Generate availabilities for all employees'

    def add_arguments(self, parser):
        parser.add_argument('days', type=int, help='Number of days to generate availabilities')

    def handle(self, *args, **options):
        days = options['days']

        # Get all active employees
        employees = Employee.objects.filter(active=True)

        start_date = date.today()
        end_date = start_date + timedelta(days=days)

        # Generate availabilities
        for employee in employees:
            current_date = start_date
            while current_date <= end_date:
                # Skip Sundays (weekday() returns 6 for Sunday)
                if current_date.weekday() != 6:
                    # Check if availability already exists
                    existing_availability = Availability.objects.filter(
                        employee=employee,
                        date=current_date
                    ).exists()

                    if not existing_availability:
                        Availability.objects.create(
                            employee=employee,
                            date=current_date,
                            start_time=time(9, 0),  # 9:00 AM
                            end_time=time(17, 0)  # 5:00 PM
                        )

                # Move to next day
                current_date += timedelta(days=1)

        self.stdout.write(self.style.SUCCESS(f'Successfully generated availabilities for {days} days'))