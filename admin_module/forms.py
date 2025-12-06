# admin_module/forms.py
from django import forms
from workflows.models import FlowInstance
from .models import Service
from services_module.models import ServiceDate,EstablishmentService
from django.contrib.auth.models import User
from barber_module.models import BarberRequest
from establishment.models import Establishment


# class CreateProductForm(forms.ModelForm):
#     name_product = forms.CharField(max_length=40, required=True, label="Nombre", widget=forms.TextInput(attrs={'placeholder': 'Nombre del producto'}))
#     description_product = forms.CharField(max_length=80, required=True, label="Descripcion")
#     amount = forms.IntegerField(required=True, initial=0, label="Cantidad")
#     minimun_stock = forms.IntegerField(required=True, initial=0, label="Cantidad Minima")
#     price_product = forms.IntegerField(required=True, initial=0, label="Precio")

#     class Meta:
#         model = Product
#         # exclude=["id_admin_id"]
#         fields = ["name_product", "description_product", "amount", "minimun_stock", "price_product", "category"]


#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)

#     def save(self, commit=True):
#         product=super().save(commit=False)
#         if commit:
#             product.save()
#         return product

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
        labels = {
            'customer': 'Cliente',
            'barber': 'Barbero',
            'service': 'Servicio',
            'date': 'Fecha y Hora',
        }
        widgets = {
            'customer': forms.Select(attrs={'class': 'form-control select2'}),
            'barber': forms.Select(attrs={'class': 'form-control'}),
            'service': forms.Select(attrs={'class': 'form-control'}),
            'date': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)

        establishment = None
        if request:
            user = request.user

            # Si es barbero
            if user.groups.filter(name='Barbero').exists():
                establishment = getattr(user.profile, 'establishment_id', None)

            # Si es administrador
            elif user.groups.filter(name='Administrador').exists():
                try:
                    establishment = Establishment.objects.get(id_admin=user).id
                except Establishment.DoesNotExist:
                    establishment = None

        # 1) BARBEROS solo del establecimiento
        queryset_barberos = User.objects.none()
        if establishment:
            queryset_barberos = User.objects.filter(
                groups__name='Barbero',
                profile__establishment_id=establishment
            )
        self.fields['barber'].queryset = queryset_barberos
        self.fields['barber'].label_from_instance = lambda obj: f"{obj.first_name} {obj.last_name}"

        # 2) SERVICIOS por tabla intermedia
        queryset_servicios = EstablishmentService.objects.none()
        if establishment:
            queryset_servicios = EstablishmentService.objects.filter(
                establishment_id=establishment,
                service__active=True
            )
        self.fields['service'].queryset = queryset_servicios
        self.fields['service'].label_from_instance = lambda obj: f"{obj.service.name_service} - ${obj.service.price_service}"

        # 3) CLIENTES (puedes filtrar por establecimiento si también los tienes asociados)
        self.fields['customer'].queryset = User.objects.filter(groups__name='Cliente')
        self.fields['customer'].label_from_instance = lambda obj: f"{obj.first_name} {obj.last_name}"

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

    class Meta:
        model = Service
        fields = ['name_service', 'description_service', 'price_service', 'category', 'duration', 'active']
        labels = {
            'name_service':'Nombre',
            'description_service': 'Descripción',
            'price_service': 'Precio',
            'category': 'Categoría',
            'duration': 'Duración',
            'active': 'Activo',
        }
        widgets = {
            'name_service': forms.TextInput(attrs={'class': 'form-control'}),
            'description_service': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
            'price_service': forms.NumberInput(attrs={'class': 'form-control'}),
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
    
class BarberRequestForm(forms.ModelForm):
    class Meta:
        model = BarberRequest
        fields = ['tipo', 'fecha_inicio', 'fecha_fin', 'comentario',]
        widgets = {
            'tipo': forms.Select(attrs={'class': 'form-select'}),
            'fecha_inicio': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'fecha_fin': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'comentario': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Puedes personalizar etiquetas aquí si lo deseas
        self.fields['tipo'].label = "Tipo de Solicitud"
        self.fields['fecha_inicio'].label = "Fecha de Inicio"
        self.fields['fecha_fin'].label = "Fecha de Fin"
        self.fields['comentario'].label = "Comentario"


# ============================================================================
# FORMULARIOS PARA CONFIGURACIÓN DE HORARIOS Y SLOTS
# ============================================================================

from django.forms import ModelForm, inlineformset_factory
from django.core.exceptions import ValidationError
from datetime import time

from admin_module.models import (
    EstablishmentSchedule, 
    BarberAvailability, 
)
from admin_module.slot_config_models import (
    EstablishmentSlotConfiguration
)


class EstablishmentScheduleForm(ModelForm):
    """
    Formulario para configurar horarios del establecimiento por día de la semana.
    """
    
    class Meta:
        model = EstablishmentSchedule
        fields = ['day_of_week', 'opening_time', 'closing_time', 'is_open']
        widgets = {
            'opening_time': forms.TimeInput(
                attrs={
                    'type': 'time',
                    'class': 'form-control',
                    'step': '900'  # 15 minutes intervals
                }
            ),
            'closing_time': forms.TimeInput(
                attrs={
                    'type': 'time',
                    'class': 'form-control',
                    'step': '900'
                }
            ),
            'day_of_week': forms.Select(attrs={'class': 'form-control'}),
            'is_open': forms.CheckboxInput(attrs={'class': 'form-check-input'})
        }
        labels = {
            'day_of_week': 'Día de la semana',
            'opening_time': 'Hora de apertura',
            'closing_time': 'Hora de cierre',
            'is_open': '¿Abre este día?'
        }
    
    def clean(self):
        cleaned_data = super().clean()
        opening_time = cleaned_data.get('opening_time')
        closing_time = cleaned_data.get('closing_time')
        is_open = cleaned_data.get('is_open')
        
        if is_open and opening_time and closing_time:
            if opening_time >= closing_time:
                raise ValidationError(
                    'La hora de apertura debe ser anterior a la hora de cierre'
                )
            
            # Validar horarios razonables
            if opening_time < time(6, 0):
                raise ValidationError(
                    'La hora de apertura no puede ser antes de las 6:00 AM'
                )
            
            if closing_time > time(23, 0):
                raise ValidationError(
                    'La hora de cierre no puede ser después de las 11:00 PM'
                )
        
        return cleaned_data


class EstablishmentSlotConfigurationForm(ModelForm):
    """
    Formulario para configuración avanzada de slots del establecimiento.
    """
    
    class Meta:
        model = EstablishmentSlotConfiguration
        exclude = ['establishment', 'created_at', 'updated_at', 'updated_by']
        
        widgets = {
            'default_slot_duration': forms.NumberInput(attrs={'class': 'form-control', 'min': 15, 'max': 120}),
            'allow_custom_slot_duration': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'advance_booking_days': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 365}),
            'min_advance_booking_hours': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'max': 72}),
            'buffer_time_between_appointments': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'max': 60}),
            'lunch_break_start': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'lunch_break_end': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'allow_same_day_booking': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'business_type': forms.Select(attrs={'class': 'form-control'})
        }


class BulkScheduleConfigForm(forms.Form):
    """
    Formulario para configurar horarios en lote para todos los días.
    """
    
    DAYS_CHOICES = [
        ('weekdays', 'Lunes a Viernes'),
        ('weekend', 'Sábados y Domingos'),
        ('all', 'Todos los días'),
        ('custom', 'Días específicos')
    ]
    
    apply_to = forms.ChoiceField(
        choices=DAYS_CHOICES,
        widget=forms.RadioSelect(),
        label="Aplicar a"
    )
    
    custom_days = forms.MultipleChoiceField(
        choices=EstablishmentSchedule.DAYS_OF_WEEK,
        widget=forms.CheckboxSelectMultiple(),
        required=False,
        label="Días específicos"
    )
    
    opening_time = forms.TimeField(
        widget=forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
        label="Hora de apertura"
    )
    
    closing_time = forms.TimeField(
        widget=forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
        label="Hora de cierre"
    )
    
    is_open = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label="¿Abierto estos días?"
    )


# FormSets para manejo múltiple de horarios
EstablishmentScheduleFormSet = inlineformset_factory(
    Establishment,
    EstablishmentSchedule,
    form=EstablishmentScheduleForm,
    extra=7,  # 7 días de la semana
    max_num=7,
    can_delete=False
)
