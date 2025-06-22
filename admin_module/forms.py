# admin_module/forms.py
from django import forms
from .models import Product, Establishment
from services_module.models import ServiceDate,EstablishmentService
from django.contrib.auth.models import User

class CreateProductForm(forms.ModelForm):
    name_product = forms.CharField(max_length=40, required=True, label="Nombre", widget=forms.TextInput(attrs={'placeholder': 'Nombre del producto'}))
    description_product = forms.CharField(max_length=80, required=True)
    amount = forms.IntegerField(required=True, initial=0)
    minimun_stock = forms.IntegerField(required=True, initial=0)
    price_product = forms.IntegerField(required=True, initial=0)

    class Meta:
        model = Product
        # exclude=["id_admin_id"]
        fields = ("name_product", "description_product", "amount", "minimun_stock", "price_product")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        product=super().save(commit=False)
        if commit:
            product.save()
        return product

class CreateEstablishmentForm(forms.ModelForm):
    name_est = forms.CharField(max_length=50, required=True, label="Nombre", widget=forms.TextInput(attrs={'placeholder': 'Nombre del establecimiento'}))
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
        exclude=["id_admin_id"]
        fields = ("name_est", "address_est", "city_est", "country_est", "phone_est", "email_est","description","lat_est","lng_est")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        establishment=super().save(commit=False)
        if commit:
            establishment.save()
        return establishment

class ServiceDateForm(forms.ModelForm):
    class Meta:
        model = ServiceDate
        fields = ['customer', 'barber', 'service', 'date', 'status']
        widgets = {
            'date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }
    
    def __init__(self, *args, **kwargs):
        #debemos extraer el request enviado desde la vista 
        request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)


        self.fields['barber'].queryset = User.objects.filter(groups__name='Barbero')
        self.fields['barber'].label_from_instance = lambda obj: f"{obj.first_name} {obj.last_name}"

        self.fields['customer'].queryset = User.objects.filter(groups__name='Cliente')
        self.fields['customer'].label_from_instance = lambda obj: f"{obj.first_name} {obj.last_name}"

        #Filtramo los servicios segun el establecimiento vinculado al usuario ya sea barbero o administrador
        


        # Mostrar nombre y precio del servicio
        self.fields['service'].queryset = EstablishmentService.objects.select_related('service')
        self.fields['service'].label_from_instance = lambda obj: f"{obj.service.name_service} - ${obj.service.price_service}"

        # Opcional: valor por defecto del estado
        self.fields['status'].initial = 'Agendada'
