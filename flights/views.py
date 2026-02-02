from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.contrib.auth.models import User, Group
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .models import Flight, Passenger, Airport, City
from .serializers import (
    FlightSerializer, PassengerSerializer, UserSerializer,
    CustomTokenObtainPairSerializer
)
from .permissions import IsFlightManager, IsPassenger
from .forms import FlightForm

# Helper function برای چک کردن manager/admin
def _is_manager_or_admin(user):
    """چک کردن Flight Manager یا Admin بودن"""
    return user.is_authenticated and (
        user.is_staff or 
        user.groups.filter(name='Flight Managers').exists()
    )

# Login و Token دریافت
class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

# ViewSet برای API پروازها
class FlightViewSet(viewsets.ModelViewSet):
    queryset = Flight.objects.all()
    serializer_class = FlightSerializer
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsFlightManager]
        elif self.action == 'join':
            permission_classes = [IsAuthenticated]
        elif self.action == 'passengers':
            permission_classes = [IsFlightManager]
        else:
            permission_classes = [AllowAny]
        return [permission() for permission in permission_classes]
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def join(self, request, pk=None):
        flight = self.get_object()
        try:
            passenger = request.user.passenger_profile
        except Passenger.DoesNotExist:
            return Response({'error': 'Passenger profile not found'}, 
                          status=status.HTTP_404_NOT_FOUND)
        
        if flight.passengers.filter(id=passenger.id).exists():
            return Response({'error': 'Already joined this flight'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        flight.passengers.add(passenger)
        return Response({'message': 'Successfully joined flight'}, 
                       status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def my_flights(self, request):
        try:
            passenger = request.user.passenger_profile
            flights = Flight.objects.filter(passengers=passenger)
            serializer = self.get_serializer(flights, many=True)
            return Response(serializer.data)
        except Passenger.DoesNotExist:
            return Response({'error': 'Passenger profile not found'}, 
                          status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=True, methods=['get'], permission_classes=[IsFlightManager])
    def passengers(self, request, pk=None):
        flight = self.get_object()
        passengers_data = flight.passengers.all()
        serializer = PassengerSerializer(passengers_data, many=True)
        return Response(serializer.data)

# ------------------ Template Views ------------------
def flight_list_view(request):
    flights = Flight.objects.all()
    is_manager = _is_manager_or_admin(request.user)
    return render(request, 'flights/flight_list.html', {
        'flights': flights, 
        'is_manager': is_manager
    })

def flight_detail_view(request, pk):
    flight = get_object_or_404(Flight, pk=pk)
    is_manager = _is_manager_or_admin(request.user)
    return render(request, 'flights/flight_detail.html', {
        'flight': flight, 
        'is_manager': is_manager
    })

@login_required
def flight_join_view(request, pk):
    flight = get_object_or_404(Flight, pk=pk)
    try:
        passenger = request.user.passenger_profile
    except Passenger.DoesNotExist:
        messages.error(request, 'Passenger profile not found. Please register first.')
        return redirect('register')

    if request.method == 'POST':
        if flight.passengers.filter(id=passenger.id).exists():
            messages.info(request, 'You already joined this flight.')
        else:
            flight.passengers.add(passenger)
            messages.success(request, 'Successfully joined the flight!')
        return redirect('my_flights')

    is_manager = _is_manager_or_admin(request.user)
    return render(request, 'flights/flight_detail.html', {
        'flight': flight, 
        'is_manager': is_manager
    })

@login_required
def my_flights_view(request):
    try:
        passenger = request.user.passenger_profile
    except Passenger.DoesNotExist:
        messages.error(request, 'Passenger profile not found. Please register.')
        return redirect('register')

    flights = Flight.objects.filter(passengers=passenger)
    is_manager = _is_manager_or_admin(request.user)
    return render(request, 'flights/my_flights.html', {
        'flights': flights, 
        'is_manager': is_manager
    })

def home_view(request):
    return render(request, 'flights/home.html')

# ------------------ Manager Views (فقط Flight Manager و Admin) ------------------
@user_passes_test(_is_manager_or_admin)
def flight_create_view(request):
    """افزودن پرواز جدید"""
    if request.method == 'POST':
        form = FlightForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'پرواز با موفقیت اضافه شد!')
            return redirect('flight_list')
    else:
        form = FlightForm()
    return render(request, 'flights/flight_form.html', {
        'form': form, 
        'title': 'افزودن پرواز جدید'
    })

@user_passes_test(_is_manager_or_admin)
def flight_edit_view(request, pk):
    """ویرایش پرواز"""
    flight = get_object_or_404(Flight, pk=pk)
    if request.method == 'POST':
        form = FlightForm(request.POST, instance=flight)
        if form.is_valid():
            form.save()
            messages.success(request, 'پرواز با موفقیت ویرایش شد!')
            return redirect('flight_detail', pk=flight.pk)
    else:
        form = FlightForm(instance=flight)
    return render(request, 'flights/flight_form.html', {
        'form': form, 
        'title': f'ویرایش {flight.name}'
    })

@user_passes_test(_is_manager_or_admin)
def flight_delete_view(request, pk):
    """حذف پرواز"""
    flight = get_object_or_404(Flight, pk=pk)
    if request.method == 'POST':
        flight.delete()
        messages.success(request, 'پرواز با موفقیت حذف شد!')
        return redirect('flight_list')
    return render(request, 'flights/flight_confirm_delete.html', {
        'flight': flight
    })

@user_passes_test(_is_manager_or_admin)
def flight_passengers_view(request, pk):
    """نمایش مسافران پرواز"""
    flight = get_object_or_404(Flight, pk=pk)
    passengers = flight.passengers.all()
    return render(request, 'flights/flight_passengers.html', {
        'flight': flight, 
        'passengers': passengers
    })

# ------------------ API ViewSets ------------------
class PassengerViewSet(viewsets.ModelViewSet):
    queryset = Passenger.objects.all()
    serializer_class = PassengerSerializer
    permission_classes = [IsAuthenticated]

class UserRegisterView(viewsets.ViewSet):
    permission_classes = [AllowAny]
    
    @action(detail=False, methods=['post'])
    def register(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            Passenger.objects.create(
                user=user,
                name=user.get_full_name() or user.username,
                passport=f"P-{user.id:06d}",
                phone=''
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def me(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)
