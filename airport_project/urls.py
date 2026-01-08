from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.views.generic import TemplateView 
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from flights.views import CustomTokenObtainPairView, UserInfoView  

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', TemplateView.as_view(template_name='flights/home.html'), name='home'),
    path('', include('flights.urls')),
    
    # path('login/', auth_views.LoginView.as_view(template_name='flights/login.html'), name='login'),
    # path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    # JWT endpoints
    path('api/token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/user/', UserInfoView.as_view(), name='user_info'),  # <-- این خط رو اضافه کن!   

]



