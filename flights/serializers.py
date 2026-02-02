# flights/serializers.py (فایل جدید)
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth.models import User
from .models import Flight, Passenger, Airport, City


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['username'] = user.username
        token['is_flight_manager'] = user.groups.filter(name='Flight Managers').exists()
        return token


class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = ['id', 'name']


class AirportSerializer(serializers.ModelSerializer):
    city = CitySerializer()
    
    class Meta:
        model = Airport
        fields = ['id', 'name', 'code', 'city']


class FlightSerializer(serializers.ModelSerializer):
    origin = AirportSerializer(read_only=True)
    destination = AirportSerializer(read_only=True)
    origin_id = serializers.IntegerField(write_only=True)
    destination_id = serializers.IntegerField(write_only=True)
    passenger_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Flight
        fields = [
            'id', 'name', 'origin', 'destination',
            'origin_id', 'destination_id',
            'distance_km', 'passenger_count'
        ]
    
    def get_passenger_count(self, obj):
        return obj.passengers.count()


class PassengerSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    
    class Meta:
        model = Passenger
        fields = ['id', 'user', 'name', 'passport', 'phone']


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    groups = serializers.StringRelatedField(many=True, read_only=True)
    is_flight_manager = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'first_name', 'last_name', 'groups', 'is_flight_manager']
    
    def get_is_flight_manager(self, obj):
        return obj.groups.filter(name='Flight Managers').exists()
    
    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', '')
        )
        return user