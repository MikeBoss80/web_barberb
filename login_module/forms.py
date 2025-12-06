from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User, Group
from .models import Profile

class UserProfileForm(UserCreationForm):
    email = forms.EmailField(
        required=True, 
        label="Correo electrónico",
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'correo@ejemplo.com'})
    )
    first_name = forms.CharField(
        max_length=30, 
        required=True, 
        label="Nombre",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Juan'})
    )
    last_name = forms.CharField(
        max_length=30, 
        required=True, 
        label="Apellido",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Pérez'})
    )

    # Campos de Profile
    phone = forms.CharField(
        max_length=20, 
        required=False, 
        label="Teléfono", 
        widget=forms.TextInput(attrs={'type': 'tel', 'class': 'form-control', 'placeholder': '3001234567'})
    )
    address = forms.CharField(
        max_length=80, 
        required=True, 
        label="Dirección",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Calle 123 #45-67'})
    )
    birth_date = forms.DateField(
        required=True, 
        label="Fecha de nacimiento", 
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    document = forms.CharField(
        max_length=80, 
        required=True, 
        label="Documento de identidad",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '1234567890'})
    )
    type_group = forms.ModelChoiceField(
        queryset=Group.objects.all(),
        empty_label="Seleccione un tipo de usuario",
        widget=forms.Select(attrs={'class': 'form-select form-control'}),
        label="Tipo de usuario",
        required=True
    )
    # establishment = forms.ModelChoiceField(queryset=None, required=False)

    class Meta:
        model = User
        fields = ("username", "email", "first_name", "last_name", "password1", "password2")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Agregar clases CSS a los campos heredados de UserCreationForm
        self.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'nombre_usuario'
        })
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': '••••••••'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': '••••••••'
        })
        
        # Establecer el queryset aquí para evitar errores de migraciones
        # Este paso se puede saltar ya que la union del establecimiento debe ser solo para barberos
        # y realizada solamente por el administrador
        # from .models import Establishment
        # self.fields['establishment'].queryset = Establishment.objects.all()

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]

        if commit:
            user.save()  # Este método crea automáticamente el registro de Profile, por eso solo se actualiza
            
            # Convertir teléfono a entero si existe, sino usar None
            phone_value = self.cleaned_data.get("phone")
            if phone_value:
                try:
                    phone_value = int(phone_value.replace('+', '').replace('-', '').replace(' ', ''))
                except (ValueError, AttributeError):
                    phone_value = None
            
            Profile.objects.filter(user=user).update(
                phone=phone_value,
                address=self.cleaned_data.get("address"),
                birth_date=self.cleaned_data.get("birth_date"),
                document=self.cleaned_data.get("document"),
                data_complete=True
            )
        return user



class UserEditForm(forms.ModelForm):
    """Formulario para editar los datos básicos del usuario"""
    class Meta:
        model = User
        fields = ["username", "email", "first_name", "last_name"]
        labels = {
            "username": "Usuario",
            "email": "Correo electrónico",
            "first_name": "Nombre",
            "last_name": "Apellido",
        }
        widgets = {
            "username": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Nombre de usuario"
            }),
            "email": forms.EmailInput(attrs={
                "class": "form-control",
                "placeholder": "Correo electrónico"
            }),
            "first_name": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Nombre"
            }),
            "last_name": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Apellido"
            }),
        }

class ProfileEditForm(forms.ModelForm):
    """Formulario para editar los datos adicionales del perfil"""
    class Meta:
        model = Profile
        fields = ["phone", "address", "birth_date", "document",]
        labels = {
            "phone": "Teléfono",
            "address": "Dirección",
            "birth_date": "Fecha de nacimiento",
            "document": "Documento de identidad",
        }
        widgets = {
            "phone": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Teléfono"
            }),
            "address": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Dirección"
            }),
            "birth_date": forms.DateInput(attrs={
                "class": "form-control",
                "type": "date"  # input HTML5 de fecha
            },
            format='%Y-%m-%d'
            ),
            

            "document": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Documento de identidad"
            }),
        }