# admin_module/forms.py
from django import forms
from .models import BarberRequest


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
