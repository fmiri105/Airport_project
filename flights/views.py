# flights/views.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.contrib.auth.models import User, Group

from .models import Flight, Passenger, Airport, City
from .serializers import (
    FlightSerializer, PassengerSerializer, UserSerializer,
    CustomTokenObtainPairSerializer
)
from .permissions import IsFlightManager, IsPassenger
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages


# Login و Token دریافت
class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


# ViewSet برای مدیریت پروازها
class FlightViewSet(viewsets.ModelViewSet):
    queryset = Flight.objects.all()
    serializer_class = FlightSerializer
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            # فقط Flight Managers می‌تونند اضافه/ویرایش کنند
            permission_classes = [IsFlightManager]
        elif self.action == 'join':
            # تمام کاربران احراز‌شده می‌تونند join کنند
            permission_classes = [IsAuthenticated]
        else:
            # list و retrieve برای همه
            permission_classes = [AllowAny]
        
        return [permission() for permission in permission_classes]
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def join(self, request, pk=None):
        """کاربر پروازی رو رزرو می‌کند"""
        flight = self.get_object()
        
        try:
            passenger = request.user.passenger_profile
        except Passenger.DoesNotExist:
            return Response(
                {'error': 'Passenger profile not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        if flight.passengers.filter(id=passenger.id).exists():
            return Response(
                {'error': 'Already joined this flight'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        flight.passengers.add(passenger)
        return Response(
            {'message': 'Successfully joined flight'},
            status=status.HTTP_200_OK
        )
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def my_flights(self, request):
        """پروازهای رزرو‌شده کاربر"""
        try:
            passenger = request.user.passenger_profile
            flights = Flight.objects.filter(passengers=passenger)
            serializer = self.get_serializer(flights, many=True)
            return Response(serializer.data)
        except Passenger.DoesNotExist:
            return Response(
                {'error': 'Passenger profile not found'},
                status=status.HTTP_404_NOT_FOUND
            )


# ------------------ Template-based views (HTML) ------------------
def flight_list_view(request):
    """Render the flight list page using templates (HTML)."""
    flights = Flight.objects.all()
    return render(request, 'flights/flight_list.html', {'flights': flights})


def flight_detail_view(request, pk):
    """Show flight detail and a join button (template)."""
    flight = get_object_or_404(Flight, pk=pk)
    return render(request, 'flights/flight_detail.html', {'flight': flight})


@login_required
def flight_join_view(request, pk):
    """Allow logged-in user to join a flight via HTML form (POST)."""
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
            messages.success(request, 'Successfully joined the flight.')
        return redirect('my_flights')

    return render(request, 'flights/flight_detail.html', {'flight': flight})


@login_required
def my_flights_view(request):
    """Render the current user's flights using templates."""
    try:
        passenger = request.user.passenger_profile
    except Passenger.DoesNotExist:
        messages.error(request, 'Passenger profile not found. Please register.')
        return redirect('register')

    flights = Flight.objects.filter(passengers=passenger)
    return render(request, 'flights/my_flights.html', {'flights': flights})


def home_view(request):
    """Render the home page template."""
    return render(request, 'flights/home.html')


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
            # Passenger رو اتوماتیک ساخت
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
        """مشاهدهٔ اطلاعات کاربر جاری"""
        serializer = UserSerializer(request.user)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def add_to_flight_managers(self, request):
        """اضافه کردن یک کاربر به گروه Flight Managers (فقط برای ادمین)"""
        if not request.user.is_staff:
            return Response(
                {'error': 'Only admins can add users to Flight Managers group'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        username = request.data.get('username')
        if not username:
            return Response(
                {'error': 'Username is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            user = User.objects.get(username=username)
            group = Group.objects.get(name='Flight Managers')
            user.groups.add(group)
            return Response(
                {'message': f'User {username} added to Flight Managers'},
                status=status.HTTP_200_OK
            )
        except User.DoesNotExist:
            return Response(
                {'error': f'User {username} not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Group.DoesNotExist:
            return Response(
                {'error': 'Flight Managers group not found. Run: python manage.py create_flight_groups'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def remove_from_flight_managers(self, request):
        """حذف کردن یک کاربر از گروه Flight Managers (فقط برای ادمین)"""
        if not request.user.is_staff:
            return Response(
                {'error': 'Only admins can remove users from Flight Managers group'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        username = request.data.get('username')
        if not username:
            return Response(
                {'error': 'Username is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            user = User.objects.get(username=username)
            group = Group.objects.get(name='Flight Managers')
            user.groups.remove(group)
            return Response(
                {'message': f'User {username} removed from Flight Managers'},
                status=status.HTTP_200_OK
            )
        except User.DoesNotExist:
            return Response(
                {'error': f'User {username} not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Group.DoesNotExist:
            return Response(
                {'error': 'Flight Managers group not found'},
                status=status.HTTP_404_NOT_FOUND
            )
