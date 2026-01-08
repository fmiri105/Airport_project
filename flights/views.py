from django.shortcuts import render, redirect
from django.views.generic import ListView, View, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from django.contrib import messages


#  JWT
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.shortcuts import redirect
from django.views.generic import TemplateView


from .models import Flight, Passenger

class FlightListView(ListView):
    model = Flight
    template_name = 'flights/flight_list.html'
    context_object_name = 'flights'

class MyFlightsView(LoginRequiredMixin, ListView):
    template_name = 'flights/my_flights.html'
    context_object_name = 'flights'

    def get_queryset(self):
        passenger, _ = Passenger.objects.get_or_create(user=self.request.user)
        return passenger.flights.all()
    
    
class RegisterFlightView(LoginRequiredMixin, View):
    def get(self, request, flight_id):
        flight = Flight.objects.get(id=flight_id)
        passenger, created = Passenger.objects.get_or_create(user=request.user)
        
        if flight in passenger.flights.all():
            messages.warning(request, f"شما قبلاً پرواز «{flight}» را ثبت کرده‌اید!")
        else:
            passenger.flights.add(flight)
            messages.success(request, f"پرواز «{flight}» با موفقیت برای شما ثبت شد!")

        return redirect('my_flights')  
    
from django.contrib.auth.mixins import UserPassesTestMixin

class FlightPassengersView(UserPassesTestMixin, ListView):
    template_name = 'flights/flight_passengers.html'
    context_object_name = 'passengers'

    def test_func(self):
        # ادمین (is_staff) یا عضو گروه Flight Managers
        return self.request.user.is_staff or self.request.user.groups.filter(name='Flight Managers').exists()

    def handle_no_permission(self):
        messages.error(self.request, "شما مجوز مشاهده لیست مسافران را ندارید.")
        return redirect('flight_list')

    def get_queryset(self):
        flight_id = self.kwargs['flight_id']
        self.flight = Flight.objects.get(id=flight_id)
        return Passenger.objects.filter(flights=self.flight)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['flight'] = self.flight
        return context
    

class RegisterView(CreateView):
    template_name = 'flights/register.html'
    form_class = UserCreationForm
    success_url = reverse_lazy('flight_list')  


#  JWT
# وییو برای گرفتن توکن (لاگین)
class CustomTokenObtainPairView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        # می‌تونی توکن رو در کوکی هم ست کنی (اختیاری)
        return response

# وییو برای چک کردن کاربر جاری (برای تمپلیت‌ها)
class UserInfoView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        groups = list(user.groups.values_list('name', flat=True))
        return Response({
            'username': user.username,
            'is_staff': user.is_staff,
            'groups': groups
        })

class LoginView(TemplateView):
    template_name = 'flights/login.html'