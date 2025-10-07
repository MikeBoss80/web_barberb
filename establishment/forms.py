# admin_module/forms.py
from django import forms
from establishment.models import Establishment

class CreateEstablishmentForm(forms.ModelForm):
    class Meta:
        model = Establishment
        fields = [
            "name_est", "address_est", "city_est", "country_est",
            "phone_est", "email_est", "description",
            "lat_est", "lng_est"
             ]
        labels = {
            "name_est": "Nombre del Establecimiento",
            "address_est": "Dirección",
            "city_est": "Ciudad",
            "country_est": "País",
            "phone_est": "Teléfono",
            "email_est": "Correo electrónico",
            "description": "Descripción",
        }
        widgets = {
            "name_est": forms.TextInput(attrs={"class": "form-control", "placeholder": "Ej: Barbería Central"}),
            # Este input será visible y usado por Google Places (id=autocomplete)
            "address_est": forms.TextInput(attrs={"class": "form-control inputDireccion", "id": "inputDireccionAdd", "placeholder": "Busca la dirección en Google Maps"}),
            "city_est": forms.TextInput(attrs={"class": "form-control inputCity", "id": "inputCityAdd", "placeholder": "Ej: Bogotá"}),
            "country_est": forms.TextInput(attrs={"class": "form-control inputCountry", "id": "inputCountryAdd", "placeholder": "Ej: Colombia"}),
            "phone_est": forms.TextInput(attrs={"class": "form-control", "placeholder": "+57 300 123 4567"}),
            "email_est": forms.EmailInput(attrs={"class": "form-control", "placeholder": "ejemplo@email.com"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "lat_est": forms.HiddenInput(attrs={
                "class": "form-control inputLat",
                "id": "inputLatAdd",
                "maxlength": "20"
            }),
            "lng_est": forms.HiddenInput(attrs={
                "class": "form-control inputLng",
                "id": "inputLngAdd",
                "maxlength": "20"
            }),
        }