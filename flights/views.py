from django.shortcuts import render, redirect
from django.views.generic import ListView, View, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy

from .models import Flight, Passenger

# لیست پروازها
class FlightListView(ListView):
    model = Flight
    template_name = 'flights/flight_list.html'
    context_object_name = 'flights'

# ثبت پرواز توسط کاربر لاگین‌شده
class RegisterFlightView(LoginRequiredMixin, View):
    def get(self, request, flight_id):
        flight = Flight.objects.get(id=flight_id)
        passenger, created = Passenger.objects.get_or_create(user=request.user)
        passenger.flights.add(flight)
        return redirect('flight_list')

# پروازهای من
@login_required
def my_flights(request):
    try:
        passenger = Passenger.objects.get(user=request.user)
    except Passenger.DoesNotExist:
        passenger = Passenger.objects.create(user=request.user)
    return render(request, 'flights/my_flights.html', {'flights': passenger.flights.all()})

# <<<--- این بخش رو حتماً اضافه کن --->>>
class RegisterView(CreateView):
    template_name = 'flights/register.html'
    form_class = UserCreationForm
    success_url = reverse_lazy('flight_list')  # <-- همین کافیه، اما برای لاگین هم نیاز داریم