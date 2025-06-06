from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Profile

class UserProfileForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)

    # Campos de Profile
    phone = forms.IntegerField(required=False)
    address = forms.CharField(max_length=80, required=True)
    birth_date = forms.DateField(required=True, widget=forms.DateInput(attrs={'type': 'date'}))
    document = forms.CharField(max_length=80, required=True)
    # establishment = forms.ModelChoiceField(queryset=None, required=False)

    class Meta:
        model = User
        fields = ("username", "email", "first_name", "last_name", "password1", "password2")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Estableces el queryset aquí para evitar errores de migraciones
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
            user.save()#Este metodo crea automaticamente el registro de Profile, por eso solo se actualiza 
            Profile.objects.filter(user=user).update(
                phone=self.cleaned_data.get("phone"),
                address=self.cleaned_data.get("address"),
                birth_date=self.cleaned_data.get("birth_date"),
                document=self.cleaned_data.get("document"),
                data_complete=True
            )
        return user


class UserEstablishmentForm(UserCreationForm):
    name_est = forms.CharField(max_length=50, required=True)
    address_est = forms.CharField(max_length=80, required=True)
    city_est = forms.CharField(max_length=20, required=True)
    country_est = forms.CharField(max_length=20, required=True)
    phone_est = forms.IntegerField(max_length=10, required=True)
    email_est = forms.CharField(max_length=100, required=True)
    description = forms.CharField(max_length=100, required=True)
    lat_est = forms.DecimalField()


    
    