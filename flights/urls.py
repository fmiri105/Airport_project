# flights/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    FlightViewSet, PassengerViewSet, UserRegisterView,
    CustomTokenObtainPairView,
    flight_list_view, flight_detail_view, flight_join_view, my_flights_view, home_view
)
from .auth_views import register_view

router = DefaultRouter()
router.register(r'flights', FlightViewSet)
router.register(r'passengers', PassengerViewSet)
router.register(r'users', UserRegisterView, basename='user')

urlpatterns = [
    # Template (HTML) routes
    path('', flight_list_view, name='flight_list'),
    path('home/', home_view, name='home'),
    path('register/', register_view, name='register'),
    path('flights/<int:pk>/', flight_detail_view, name='flight_detail'),
    path('flights/<int:pk>/register/', flight_join_view, name='register_flight'),
    path('my_flights/', my_flights_view, name='my_flights'),

    # API routes under /api/
    path('api/', include(router.urls)),
    path('api/token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]