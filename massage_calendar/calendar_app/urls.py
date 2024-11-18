from django.urls import path
from .views import ServiceListView, EmployeeListView, AvailabilityListView, AppointmentCreateView

urlpatterns = [
    path('services/', ServiceListView.as_view(), name='service-list'),
    path('employees/', EmployeeListView.as_view(), name='employee-list'),
    path('availability/', AvailabilityListView.as_view(), name='availability-list'),
    path('appointments/', AppointmentCreateView.as_view(), name='appointment-create'),
]