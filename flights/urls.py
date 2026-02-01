
from django.urls import path
from .views import HomeView, FlightListView, RegisterFlightView, my_flights, RegisterView

urlpatterns = [
    path("", HomeView.as_view(), name="home"),
    path('flights/', FlightListView.as_view(), name='flight_list'),
    path('register_flight/<int:flight_id>/', RegisterFlightView.as_view(), name='register_flight'),
    path('my_flights/', my_flights, name='my_flights'),
    path('register/', RegisterView.as_view(), name='register'),  # <-- این خط رو اضافه کن
]