
# from django.urls import path
# from .views import FlightListView, RegisterFlightView, MyFlightsView, RegisterView, FlightPassengersView

# urlpatterns = [
#     path('flights/', FlightListView.as_view(), name='flight_list'),
#     path('register_flight/<int:flight_id>/', RegisterFlightView.as_view(), name='register_flight'),
#     path('my_flights/', MyFlightsView.as_view(), name='my_flights'),
#     path('flight/<int:flight_id>/passengers/', FlightPassengersView.as_view(), name='flight_passengers'),  # <-- جدید
#     path('register/', RegisterView.as_view(), name='register'),
# ]

# JWT
from django.urls import path
from .views import (
    FlightListView,
    RegisterFlightView,
    MyFlightsView,
    FlightPassengersView,
    RegisterView,
    LoginView,  
)

urlpatterns = [
    path('flights/', FlightListView.as_view(), name='flight_list'),
    path('register_flight/<int:flight_id>/', RegisterFlightView.as_view(), name='register_flight'),
    path('my_flights/', MyFlightsView.as_view(), name='my_flights'),
    path('flight/<int:flight_id>/passengers/', FlightPassengersView.as_view(), name='flight_passengers'),
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'), 
]