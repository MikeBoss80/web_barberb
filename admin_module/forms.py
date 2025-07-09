# admin_module/forms.py
from django import forms
from workflows.models import FlowInstance
from .models import Product, Establishment, Service
from services_module.models import ServiceDate,EstablishmentService
from django.contrib.auth.models import User
from barber_module.models import BarberRequest

class CreateProductForm(forms.ModelForm):
    name_product = forms.CharField(max_length=40, required=True, label="Nombre", widget=forms.TextInput(attrs={'placeholder': 'Nombre del producto'}))
    description_product = forms.CharField(max_length=80, required=True)
    amount = forms.IntegerField(required=True, initial=0)
    minimun_stock = forms.IntegerField(required=True, initial=0)
    price_product = forms.IntegerField(required=True, initial=0)

    class Meta:
        model = Product
        # exclude=["id_admin_id"]
        fields = ("name_product", "description_product", "amount", "minimun_stock", "price_product", "category")

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
        fields = ['customer', 'barber', 'service', 'date']
        widgets = {
            'customer': forms.Select(attrs={'class': 'form-control select2'}),
            'barber': forms.Select(attrs={'class': 'form-control'}),
            'service': forms.Select(attrs={'class': 'form-control'}),
            'date': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
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

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.status = 'Agendada'  # 👈 Valor por defecto interno
        if commit:
            instance.save()
        return instance

class EditarBarberoEstadoForm(forms.ModelForm):
    class Meta:
        model = ServiceDate
        fields = ['barber', 'status']

    def __init__(self, *args, **kwargs):
        request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)

        if request:
            user = request.user
            try:
                est = user.profile.establishment
                self.fields['barber'].queryset = User.objects.filter(
                    groups__name='Barbero',
                    profile__establishment=est
                )
            except:
                self.fields['barber'].queryset = User.objects.none()

        #Trae nombre y apellido del barbero
        self.fields['barber'].label_from_instance = lambda obj: f"{obj.first_name} {obj.last_name}"

        self.fields['barber'].widget.attrs.update({'class': 'form-select'})
        self.fields['status'].widget = forms.Select(
            choices=[
                ('Agendada', 'Agendada'),
                ('Cancelada', 'Cancelada'),
                ('Completada', 'Completada'),
            ],
            attrs={'class': 'form-select'}
        )

class BarberRequestAdminResponseForm(forms.ModelForm):
    class Meta:
        model = BarberRequest
        fields = ['respuesta_admin']  # Solo permite escribir respuesta
        widgets = {
            'respuesta_admin': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }
        labels = {
            'respuesta_admin': 'Respuesta del Administrador',
        }
        
class CreateServiceForm(forms.ModelForm):
    name_service = forms.CharField(max_length=80, required=True)

    class Meta:
        model = Service
        fields = ['name_service', 'description_service', 'price_service', 'category', 'duration', 'active']
        widgets = {
            'name_service': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'duration': forms.NumberInput(attrs={'class': 'form-control'}),
            'active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class UploadServiceFile(forms.Form):
    file = forms.FileField(label = "Subir carta de servicios (PDF o Imagen)")

class VinculationForm(forms.ModelForm):
    # comments = forms.CharField(max_length=80, required=True)
    document = forms.CharField(label='Documento del colaborador', max_length=15, required=True)

    class Meta:
        model = FlowInstance
        fields = ['workflow_type']#pendiente comentarios
        widgets = {
            'workflow_type': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        instance=super().save(commit=False)
        if commit:
            instance.save()
        return instance