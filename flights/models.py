
from django.db import models
from django.contrib.auth.models import User

class City(models.Model):
    name = models.CharField(max_length=100)
    def __str__(self): return self.name

class Airport(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10, unique=True)
    city = models.ForeignKey(City, on_delete=models.CASCADE)
    def __str__(self): return f"{self.name} ({self.code})"

class Passenger(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='passenger_profile')  # ← رابطه اصلی
    name = models.CharField(max_length=100)
    passport = models.CharField(max_length=20, unique=True)
    phone = models.CharField(max_length=15, blank=True)
    
    def __str__(self):
        return f"{self.name} ({self.user.username})"

class Flight(models.Model):
    name = models.CharField(max_length=50)
    origin = models.ForeignKey(Airport, on_delete=models.CASCADE, related_name="departing_flights")
    destination = models.ForeignKey(Airport, on_delete=models.CASCADE, related_name="arriving_flights")
    distance_km = models.PositiveIntegerField()
    passengers = models.ManyToManyField(Passenger, blank=True, related_name="flights")
    
    class Meta:
        permissions = [
            ("can_manage_flights", "Can add/edit/delete flights"),
        ]

    def __str__(self):
        return f"{self.name}: {self.origin} → {self.destination}"