from django.db import models
from django.contrib.auth.models import User

class City(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class Airport(models.Model):
    name = models.CharField(max_length=100)
    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name='airports')

    def __str__(self):
        return f"{self.name} ({self.city.name})"

class Flight(models.Model):
    origin_airport = models.ForeignKey(Airport, on_delete=models.CASCADE, related_name='departures')
    destination_airport = models.ForeignKey(Airport, on_delete=models.CASCADE, related_name='arrivals')
    distance = models.IntegerField(help_text="Distance in km")

    def __str__(self):
        return f"Flight from {self.origin_airport} to {self.destination_airport} ({self.distance} km)"

class Passenger(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    flights = models.ManyToManyField(Flight, related_name='passengers', blank=True)

    def __str__(self):
        return self.user.username