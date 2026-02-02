from django import forms
from .models import Flight, Airport


class FlightForm(forms.ModelForm):
    class Meta:
        model = Flight
        fields = ['name', 'origin', 'destination', 'distance_km']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'origin': forms.Select(attrs={'class': 'form-select'}),
            'destination': forms.Select(attrs={'class': 'form-select'}),
            'distance_km': forms.NumberInput(attrs={'class': 'form-control'}),
        }
