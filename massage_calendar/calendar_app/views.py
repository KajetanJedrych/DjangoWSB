from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils import timezone
from datetime import datetime, timedelta
from .models import Service, Employee, Availability, Appointment
from .serializers import (ServiceSerializer, EmployeeSerializer,
                          AvailabilitySerializer, AppointmentSerializer)


@api_view(['GET'])
def get_services(request):
    services = Service.objects.filter(active=True)
    serializer = ServiceSerializer(services, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def get_employees(request):
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

    # No need to check existing appointments for the first booking
    available_slots = []

    for availability in availabilities:
        current_time = availability.start_time
        end_time = availability.end_time
        print(f"Checking availability: {current_time} to {end_time}")

        while current_time <= end_time:
            # Check if this slot allows enough time for the service
            slot_end_time = (
                    datetime.combine(date, current_time) +
                    timedelta(minutes=service.duration)
            ).time()

            print(f"Checking slot: {current_time} to {slot_end_time}")

            if slot_end_time <= end_time:
                available_slots.append(current_time.strftime('%H:%M'))

            # Move to next slot (30-minute increments)
            current_time = (
                    datetime.combine(date, current_time) +
                    timedelta(minutes=30)
            ).time()

    print(f"Available slots: {available_slots}")
    return Response(available_slots)


from django.db.models import Q


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_appointments(request):
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