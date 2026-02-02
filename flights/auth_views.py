from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.views.decorators.http import require_http_methods
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User
from django.views.decorators.http import require_POST
from django.contrib import messages
from .models import Passenger
from django.contrib.auth.forms import UserCreationForm


@require_http_methods(["GET", "POST"])
def cookie_login_view(request):
    """Render login form (GET) and on POST authenticate, create session and set JWT cookie."""
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            # create JWT
            refresh = RefreshToken.for_user(user)
            access = str(refresh.access_token)
            resp = redirect('flight_list') if 'next' not in request.POST else redirect(request.POST.get('next'))
            # Set httponly cookie for access token
            resp.set_cookie(
                'access_token',
                access,
                httponly=True,
                samesite='Lax',
            )
            return resp
    else:
        form = AuthenticationForm()

    return render(request, 'flights/login.html', {'form': form})


def cookie_logout_view(request):
    """Logout the user (session) and delete JWT cookie."""
    logout(request)
    resp = redirect('flight_list')
    resp.delete_cookie('access_token')
    return resp


@require_http_methods(["GET", "POST"])
def register_view(request):
    """Render registration form and create User + Passenger, then login and set JWT cookie."""
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # optionally set email/first/last if provided in POST
            email = request.POST.get('email', '')
            first_name = request.POST.get('first_name', '')
            last_name = request.POST.get('last_name', '')
            if email or first_name or last_name:
                user.email = email
                user.first_name = first_name
                user.last_name = last_name
                user.save()

            # create passenger profile
            Passenger.objects.create(
                user=user,
                name=user.get_full_name() or user.username,
                passport=f"P-{user.id:06d}",
                phone=''
            )

            # login and set cookie
            login(request, user)
            refresh = RefreshToken.for_user(user)
            access = str(refresh.access_token)
            resp = redirect('flight_list')
            resp.set_cookie('access_token', access, httponly=True, samesite='Lax')
            return resp
    else:
        form = UserCreationForm()

    return render(request, 'flights/register.html', {'form': form})
