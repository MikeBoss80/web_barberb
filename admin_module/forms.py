# admin_module/forms.py
from django import forms
from .models import Product, Establishment

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

