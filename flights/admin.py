from django.contrib import admin
from .models import City, Airport, Flight, Passenger

@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']

@admin.register(Airport)
class AirportAdmin(admin.ModelAdmin):
    list_display = ['name', 'city']
    list_filter = ['city']
    search_fields = ['name', 'city__name']

@admin.register(Flight)
class FlightAdmin(admin.ModelAdmin):
    list_display = ['origin_airport', 'destination_airport', 'distance']
    list_filter = ['origin_airport__city', 'destination_airport__city']
    search_fields = ['origin_airport__name', 'destination_airport__name']

@admin.register(Passenger)
class PassengerAdmin(admin.ModelAdmin):
    list_display = ['user', 'flight_count']
    search_fields = ['user__username']

    def flight_count(self, obj):
        return obj.flights.count()
    flight_count.short_description = 'تعداد پروازها'