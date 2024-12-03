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


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_appointments(request):
    date = request.GET.get('date')
    # Log all possible appointments for this date
    all_date_appointments = Appointment.objects.filter(date=date)
    for appt in all_date_appointments:
        print(
            f"ID: {appt.id}, User ID: {appt.user.id}, Username: {appt.user.username}, Date: {appt.date}, Time: {appt.time}")
    appointments = Appointment.objects.filter(date=date, user=request.user)
    serializer = AppointmentSerializer(appointments, many=True)
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