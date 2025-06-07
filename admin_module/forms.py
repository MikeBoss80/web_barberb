# admin_module/forms.py
from django import forms
from .models import Product, Establishment

class ProductoForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = '__all__'
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Gel Fijador'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Descripción opcional...'
            }),
        }
        labels = {
            'stock_minimo': 'Stock Mínimo (alerta)',
        }



class CreateEstablishmentForm(forms.ModelForm):
    name_est = forms.CharField(max_length=50, required=True)
    address_est = forms.CharField(max_length=80, required=True)
    city_est = forms.CharField(max_length=20, required=True)
    country_est = forms.CharField(max_length=20, required=True)
    phone_est = forms.IntegerField(required=True)
    email_est = forms.CharField(max_length=100, required=True)
    description = forms.CharField(max_length=100, required=True)
    lat_est = forms.DecimalField( max_digits=10, decimal_places=7, required=True)
    lng_est = forms.DecimalField(max_digits=10, decimal_places=7, required=True)
    
    
    class Meta:
        model = Establishment
        fields = ("name_est", "address_est", "city_est", "country_est", "phone_est", "email_est","description","lat_est","lng_est")


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Estableces el queryset aquí para evitar errores de migraciones
        # Este paso se puede saltar ya que la union del establecimiento debe ser solo para barberos
        # y realizada solamente por el administrador
        # from .models import Establishment
        # self.fields['establishment'].queryset = Establishment.objects.all()

    def save(self, commit=True):
        if commit:
            Establishment.objects.create(
                name_est = self.cleaned_data.get("name_est"),
                address_est = self.cleaned_data.get("address_est"),
                city_est = self.cleaned_data.get("city_est"),
                country_est = self.cleaned_data.get("country_est"),
                phone_est = self.cleaned_data.get("phone_est"),
                email_est = self.cleaned_data.get("email_est"),
                description = self.cleaned_data.get("description"),
                lat_est = self.cleaned_data.get("lat_est"),
                lng_est = self.cleaned_data.get("lng_est"),
            )
        return user

