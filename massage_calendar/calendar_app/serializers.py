from rest_framework import serializers
from .models import Service, Employee, Availability, Appointment


class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = ['id', 'name', 'description', 'duration', 'active']


class EmployeeSerializer(serializers.ModelSerializer):
    services = ServiceSerializer(many=True, read_only=True)

    class Meta:
        model = Employee
        fields = ['id', 'name', 'specialization', 'services', 'active']


class AvailabilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Availability
        fields = ['id', 'employee', 'date', 'start_time', 'end_time']


class AppointmentSerializer(serializers.ModelSerializer):
    service_name = serializers.CharField(source='service.name', read_only=True)
    employee_name = serializers.CharField(source='employee.name', read_only=True)
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)

    class Meta:
        model = Appointment
        fields = ['id', 'user', 'service', 'service_name', 'employee',
                  'employee_name', 'date', 'time', 'status', 'notes',
                  'user_name']
        read_only_fields = ['status', 'created_at', 'updated_at']