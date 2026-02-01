from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, CreateView, TemplateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy

from .models import Flight, Passenger


class HomeView(TemplateView):
    template_name = "flights/home.html"


class FlightListView(ListView):
    model = Flight
    template_name = 'flights/flight_list.html'
    context_object_name = 'flights'
    
    def get_queryset(self):
        return Flight.objects.select_related(
            "origin__city", "destination__city"
        ).prefetch_related("passengers")


class RegisterView(CreateView):
    template_name = 'flights/register.html'
    form_class = UserCreationForm
    success_url = reverse_lazy('flight_list')

    def form_valid(self, form):
        # کاربر رو ذخیره کن
        user = form.save()
        
        # اتوماتیک لاگین کن (خیلی مهم!)
        login(self.request, user)
        
        # اگر می‌خوای مسافر (Passenger) هم اتوماتیک ساخته بشه
        Passenger.objects.create(
            user=user,
            name=user.get_full_name() or user.username,
            passport=f"P-{user.id:06d}",
            phone=''
        )
        
        return super().form_valid(form)


@login_required
def join_flight(request, flight_id):
    flight = get_object_or_404(Flight, pk=flight_id)
    
    # مسافر کاربر لاگین‌شده رو بگیریم (چون OneToOne داریم)
    passenger = request.user.passenger_profile  # ← از related_name استفاده می‌کنیم
    
    # اگر قبلاً ثبت‌نام کرده
    if flight.passengers.filter(id=passenger.id).exists():
        return render(request, 'flights/already_joined.html', {'flight': flight})
    
    # اضافه کردن مسافر به پرواز
    flight.passengers.add(passenger)
    
    return redirect('my_flights')


@login_required
def my_flights(request):
    passenger = request.user.passenger_profile
    flights = Flight.objects.filter(passengers=passenger).select_related(
        "origin__city", "destination__city"
    )
    
    return render(request, 'flights/my_flights.html', {'flights': flights})

# ثبت پرواز توسط کاربر لاگین‌شده
class RegisterFlightView(LoginRequiredMixin, View):
    def get(self, request, flight_id):
        flight = Flight.objects.get(id=flight_id)
        passenger, created = Passenger.objects.get_or_create(user=request.user)
        passenger.flights.add(flight)
        return redirect('flight_list')
