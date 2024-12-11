from django.db.models import Q, F
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from datetime import datetime, timedelta
from .models import Service, Employee, Availability, Appointment
from .serializers import (ServiceSerializer, EmployeeSerializer,
                          AvailabilitySerializer, AppointmentSerializer)


@api_view(['GET'])
def get_services(request):
    """
    Retrieve all active services.
    """
    services = Service.objects.filter(active=True)
    serializer = ServiceSerializer(services, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def get_employees(request):
    """
     Retrieve all active employees or those offering a specific service.
     """
    service_id = request.GET.get('service_id')
    if service_id:
        employees = Employee.objects.filter(
            active=True,
            services__id=service_id
        ).distinct()
    else:
        employees = Employee.objects.filter(active=True)
    serializer = EmployeeSerializer(employees, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def get_available_slots(request):
    """
    Retrieve available time slots for a given date, employee, and service.
    """
    date_str = request.GET.get('date')
    employee_id = request.GET.get('employee_id')
    service_id = request.GET.get('service_id')

    print(f"Received parameters: date={date_str}, employee_id={employee_id}, service_id={service_id}")

    if not all([date_str, employee_id, service_id]):
        return Response(
            {'error': 'Missing required parameters'},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        date = datetime.strptime(date_str, '%Y-%m-%d').date()
        employee = Employee.objects.get(id=employee_id)
        service = Service.objects.get(id=service_id)

        print(f"Parsed date: {date}")
        print(f"Employee: {employee}")
        print(f"Service: {service}")
    except (ValueError, Employee.DoesNotExist, Service.DoesNotExist) as e:
        print(f"Error parsing parameters: {e}")
        return Response(
            {'error': 'Invalid parameters'},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Get employee's availability for the date
    availabilities = Availability.objects.filter(
        employee=employee,
        date=date
    )
    print(f"Availabilities found: {availabilities.count()}")

    if not availabilities.exists():
        return Response([], status=status.HTTP_404_NOT_FOUND)

    # Get existing appointments for the day
    existing_appointments = Appointment.objects.filter(
        employee=employee,
        date=date,
        status='scheduled'
    )

    available_slots = []

    for availability in availabilities:
        current_time = availability.start_time
        end_time = availability.end_time
        print(f"Checking availability: {current_time} to {end_time}")

        while current_time <= end_time:
            # Check if this slot allows enough time for the service
            slot_datetime = datetime.combine(date, current_time)
            slot_end_datetime = slot_datetime + timedelta(minutes=service.duration)

            # Verify the slot is within the availability period
            if slot_end_datetime.time() > end_time:
                break

            # Check for conflicts with existing appointments
            has_conflicts = any(
                (
                    # Check if new slot overlaps with existing appointment
                        current_time < appt.time < slot_end_datetime.time() or
                        # Check if existing appointment overlaps with new slot
                        appt.time < slot_end_datetime.time() and
                        (datetime.combine(date, appt.time) + timedelta(
                            minutes=appt.service.duration)).time() > current_time
                )
                for appt in existing_appointments
            )

            # If no conflicts, add the slot
            if not has_conflicts:
                available_slots.append(current_time.strftime('%H:%M'))

            # Move to next slot (30-minute increments)
            current_time = (
                    datetime.combine(date, current_time) +
                    timedelta(minutes=30)
            ).time()

    print(f"Available slots: {available_slots}")
    return Response(available_slots)



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_appointments(request):
    """
    Retrieve appointments for the current user or all appointments if the user is a manager.
    """
    # Robust manager check
    is_manager = request.user.groups.filter(name__iexact='Managers').exists()
    print("All Groups:", list(request.user.groups.values_list('name', flat=True)))

    # Base queryset
    if is_manager:
        # Explicitly fetch ALL appointments for managers
        queryset = Appointment.objects.all()
    else:
        # Regular users see only their own appointments
        queryset = Appointment.objects.filter(user=request.user)

    # Get query parameters
    date = request.GET.get('date')
    end_date = request.GET.get('end_date')

    # Date filtering
    if date:
        if end_date:
            queryset = queryset.filter(
                date__gte=date,
                date__lte=end_date
            )
        else:
            queryset = queryset.filter(date=date)

    # Extensive logging
    print(f"Current User: {request.user.username}")
    print(f"Is Manager: {is_manager}")
    print(f"Total Appointments Found: {queryset.count()}")

    # Detailed appointment logging
    for appt in queryset:
        print(
            f"Appointment - "
            f"ID: {appt.id}, "
            f"User: {appt.user.username}, "
            f"Date: {appt.date}, "
            f"Time: {appt.time}, "
            f"Status: {appt.status}"
        )

    # Use select_related to optimize query and fetch related data
    queryset = queryset.select_related('user', 'service', 'employee')

    serializer = AppointmentSerializer(queryset, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_appointment(request):
    """
    Create a new appointment for the authenticated user.
    """
    data = request.data.copy()
    data['user'] = request.user.id

    serializer = AppointmentSerializer(data=data)
    if serializer.is_valid():
        try:
            appointment = serializer.save()
            appointment.full_clean()  # Run model validation
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except ValidationError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)