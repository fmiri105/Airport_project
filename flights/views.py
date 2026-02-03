"""
Flight booking system views.

This module contains:
- DRF ViewSets for API endpoints (Flight, Passenger, User registration/management)
- Template-based views for HTML rendering (home, flight list/detail, join, my flights)
- Manager-only views for CRUD operations and passenger list
- Permission handling with custom permissions and group checks
- JWT authentication support via simplejwt
- User feedback with Django messages
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth.models import User, Group
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages

from .models import Flight, Passenger, Airport, City
from .serializers import FlightSerializer, PassengerSerializer, UserSerializer
from .permissions import IsFlightManager, IsPassenger
from .forms import FlightForm


# ───────────────────────────────────────────────
# Helper Functions
# ───────────────────────────────────────────────

def _is_manager_or_admin(user):
    """
    Check if the user is a staff member (admin) or belongs to the 'Flight Managers' group.

    Args:
        user: The user instance to check.

    Returns:
        bool: True if user has management permissions, False otherwise.
    """
    return user.is_authenticated and (user.is_staff or user.groups.filter(name='Flight Managers').exists())


# ───────────────────────────────────────────────
# JWT Token Views
# ───────────────────────────────────────────────

class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Custom endpoint for obtaining JWT access and refresh tokens.
    Can be extended with CustomTokenObtainPairSerializer for additional claims.
    """
    # serializer_class = CustomTokenObtainPairSerializer  # Uncomment if custom serializer exists
    pass


# ───────────────────────────────────────────────
# Flight API ViewSet (DRF)
# ───────────────────────────────────────────────

class FlightViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing flights.

    Permissions:
    - create/update/delete: Flight Managers or admins only
    - join/my_flights: authenticated users only
    - list/retrieve: public (AllowAny)
    - passengers: Flight Managers or admins only

    Endpoints:
    - GET    /api/flights/                → List all flights
    - GET    /api/flights/<id>/           → Retrieve flight detail
    - POST   /api/flights/                → Create new flight (manager only)
    - PUT    /api/flights/<id>/           → Update flight (manager only)
    - DELETE /api/flights/<id>/           → Delete flight (manager only)
    - POST   /api/flights/<id>/join/      → Join the flight as passenger
    - GET    /api/flights/my_flights/     → List current user's joined flights
    - GET    /api/flights/<id>/passengers/ → List passengers of the flight (manager only)
    """
    queryset = Flight.objects.all()
    serializer_class = FlightSerializer

    def get_permissions(self):
        """
        Custom permission logic based on the current action.
        """
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsFlightManager()]
        if self.action in ['join', 'my_flights']:
            return [IsAuthenticated()]
        if self.action == 'passengers':
            return [IsFlightManager()]
        return [AllowAny()]

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def join(self, request, pk=None):
        """
        Register the authenticated user (as passenger) to the specified flight.

        POST /api/flights/<id>/join/
        Requires authentication.
        Returns success message or error if already joined.
        """
        flight = self.get_object()

        try:
            passenger = request.user.passenger_profile
        except Passenger.DoesNotExist:
            return Response(
                {"error": "Passenger profile not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        if flight.passengers.filter(id=passenger.id).exists():
            return Response(
                {"error": "Already joined this flight"},
                status=status.HTTP_400_BAD_REQUEST
            )

        flight.passengers.add(passenger)
        return Response(
            {"message": "Successfully joined flight"},
            status=status.HTTP_200_OK
        )

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def my_flights(self, request):
        """
        Retrieve the list of flights the current authenticated user has joined.

        GET /api/flights/my_flights/
        Returns serialized list of flights.
        """
        try:
            passenger = request.user.passenger_profile
            flights = Flight.objects.filter(passengers=passenger)
            serializer = self.get_serializer(flights, many=True)
            return Response(serializer.data)
        except Passenger.DoesNotExist:
            return Response(
                {"error": "Passenger profile not found"},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=True, methods=['get'], permission_classes=[IsFlightManager])
    def passengers(self, request, pk=None):
        """
        Retrieve the list of passengers registered in the specified flight.

        GET /api/flights/<id>/passengers/
        Only accessible by Flight Managers or admins.
        Returns serialized list of passengers.
        """
        flight = self.get_object()
        passengers_data = flight.passengers.all()
        serializer = PassengerSerializer(passengers_data, many=True)
        return Response(serializer.data)


# ───────────────────────────────────────────────
# HTML Template-based Views
# ───────────────────────────────────────────────

def flight_list_view(request):
    """
    Render HTML page listing all flights.
    Managers/admins see add/edit/delete options.
    """
    flights = Flight.objects.select_related("origin__city", "destination__city").all()
    is_manager = _is_manager_or_admin(request.user)
    
    return render(request, 'flights/flight_list.html', {
        'flights': flights,
        'is_manager': is_manager
    })


def flight_detail_view(request, pk):
    """
    Render HTML page with flight details.
    Managers/admins see passenger list.
    """
    flight = get_object_or_404(Flight, pk=pk)
    is_manager = _is_manager_or_admin(request.user)
    
    return render(request, 'flights/flight_detail.html', {
        'flight': flight,
        'is_manager': is_manager
    })


@login_required
def flight_join_view(request, pk):
    """
    Allow logged-in user to join a flight via HTML form (POST).
    Shows feedback messages and redirects to my_flights.
    """
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

    return render(request, 'flights/flight_detail.html', {'flight': flight})


@login_required
def my_flights_view(request):
    """
    Render HTML page showing all flights the current user has joined.
    """
    try:
        passenger = request.user.passenger_profile
        flights = Flight.objects.filter(passengers=passenger).select_related(
            "origin__city", "destination__city"
        )
    except Passenger.DoesNotExist:
        messages.error(request, 'Passenger profile not found. Please register.')
        return redirect('register')

    return render(request, 'flights/my_flights.html', {'flights': flights})


def home_view(request):
    """
    Render the home/landing page.
    """
    return render(request, 'flights/home.html')


# ───────────────────────────────────────────────
# Manager-only HTML Views (Flight Managers & Admins)
# ───────────────────────────────────────────────

@user_passes_test(_is_manager_or_admin)
def flight_create_view(request):
    """
    HTML view for creating a new flight.
    Only accessible by Flight Managers or admins.
    """
    if request.method == 'POST':
        form = FlightForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Flight created successfully!')
            return redirect('flight_list')
    else:
        form = FlightForm()
    
    return render(request, 'flights/flight_form.html', {
        'form': form,
        'title': 'Add New Flight'
    })


@user_passes_test(_is_manager_or_admin)
def flight_edit_view(request, pk):
    """
    HTML view for editing an existing flight.
    Only accessible by Flight Managers or admins.
    """
    flight = get_object_or_404(Flight, pk=pk)
    
    if request.method == 'POST':
        form = FlightForm(request.POST, instance=flight)
        if form.is_valid():
            form.save()
            messages.success(request, 'Flight updated successfully!')
            return redirect('flight_detail', pk=flight.pk)
    else:
        form = FlightForm(instance=flight)
    
    return render(request, 'flights/flight_form.html', {
        'form': form,
        'title': f'Edit {flight.name}'
    })


@user_passes_test(_is_manager_or_admin)
def flight_delete_view(request, pk):
    """
    HTML view for deleting a flight.
    Only accessible by Flight Managers or admins.
    """
    flight = get_object_or_404(Flight, pk=pk)
    
    if request.method == 'POST':
        flight.delete()
        messages.success(request, 'Flight deleted successfully!')
        return redirect('flight_list')
    
    return render(request, 'flights/flight_confirm_delete.html', {
        'flight': flight
    })


@user_passes_test(_is_manager_or_admin)
def flight_passengers_view(request, pk):
    """
    HTML view displaying the list of passengers registered in a flight.
    Only accessible by Flight Managers or admins.
    """
    flight = get_object_or_404(Flight, pk=pk)
    passengers = flight.passengers.all()
    
    return render(request, 'flights/flight_passengers.html', {
        'flight': flight,
        'passengers': passengers
    })


# ───────────────────────────────────────────────
# Additional ViewSets
# ───────────────────────────────────────────────

class PassengerViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing passengers.

    - List / Retrieve / Update / Delete: authenticated users only
    """
    queryset = Passenger.objects.all()
    serializer_class = PassengerSerializer
    permission_classes = [IsAuthenticated]


class UserRegisterView(viewsets.ViewSet):
    """
    API endpoint for user registration and profile management.
    """
    permission_classes = [AllowAny]

    @action(detail=False, methods=['post'])
    def register(self, request):
        """
        Register a new user and automatically create a Passenger profile.

        POST /api/users/register/
        Returns user data on success or validation errors.
        """
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
        """
        Retrieve the current authenticated user's profile information.

        GET /api/users/me/
        Returns serialized user data.
        """
        serializer = UserSerializer(request.user)
        return Response(serializer.data)