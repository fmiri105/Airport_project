from django.contrib import admin
from .models import Flight, Passenger, Airport, City

@admin.register(Flight)
class FlightAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'origin',                    # مستقیماً origin نمایش داده می‌شه
        'origin_city',               # متد سفارشی برای شهر
        'destination',
        'destination_city',          # متد سفارشی
        'distance_km',
        'passenger_count',           # تعداد مسافران
    ]
    list_filter = [
        'origin__city',              # فیلتر بر اساس شهر مبدا
        'destination__city',         # فیلتر بر اساس شهر مقصد
    ]
    search_fields = ['name', 'origin__name', 'destination__name']
    readonly_fields = ['passenger_count']  # اختیاری

    def origin_city(self, obj):
        return obj.origin.city.name if obj.origin and obj.origin.city else '-'
    origin_city.short_description = 'شهر مبدا'

    def destination_city(self, obj):
        return obj.destination.city.name if obj.destination and obj.destination.city else '-'
    destination_city.short_description = 'شهر مقصد'

    def passenger_count(self, obj):
        return obj.passengers.count()
    passenger_count.short_description = 'تعداد مسافران'


# اگر می‌خوای بقیه مدل‌ها هم در ادمین باشن (اختیاری)
@admin.register(Passenger)
class PassengerAdmin(admin.ModelAdmin):
    list_display = ['name', 'passport', 'phone', 'user']
    search_fields = ['name', 'passport']

@admin.register(Airport)
class AirportAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'city']
    search_fields = ['name', 'code']

@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']