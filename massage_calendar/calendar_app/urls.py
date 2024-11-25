from django.urls import path
from . import views

urlpatterns = [
    path('services/', views.get_services, name='services'),
    path('employees/', views.get_employees, name='employees'),
    path('available-slots/', views.get_available_slots, name='available-slots'),
    path('appointments/', views.get_appointments, name='appointments'),
    path('appointments/create/', views.create_appointment, name='create-appointment'),
]
