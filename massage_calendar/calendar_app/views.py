from rest_framework import generics
from .models import Service, Employee, Availability, Appointment
from .serializers import ServiceSerializer, EmployeeSerializer, AvailabilitySerializer, AppointmentSerializer
from rest_framework.permissions import IsAuthenticated


class ServiceListView(generics.ListAPIView):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer

class EmployeeListView(generics.ListAPIView):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer

class AvailabilityListView(generics.ListAPIView):
    serializer_class = AvailabilitySerializer

    def get_queryset(self):
        date = self.request.query_params.get('date')
        return Availability.objects.filter(date=date)

class AppointmentCreateView(generics.CreateAPIView):
    queryset = Appointment.objects.all()
    serializer_class = AppointmentSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
