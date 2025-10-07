from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import TemplateView, CreateView, DeleteView, UpdateView
from django.contrib.auth.mixins import UserPassesTestMixin
from .forms import CreateEstablishmentForm
from establishment.models import Establishment
from django.conf import settings
from django.http import JsonResponse
from decimal import Decimal, InvalidOperation

def parse_coordinate(value, default=None):
    if value is None or value == '':
        return default
    try:
        return round(Decimal(str(value)), 6)
    except (InvalidOperation, ValueError, TypeError):
        return default

class EstablishmentMainView(TemplateView):
    template_name= 'establishment/base.html'

    # def get_breadcrumb(self):
    #     return [{'label': 'Establecimiento', 'url': reverse('admin_module:establecimiento')}]

class EstablishmentManagementView(TemplateView):
    template_name= 'establishment/tabs/management.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['establecimientos'] = self.request.user.admin_est.all()
        context['form'] = CreateEstablishmentForm()
        return context

class UpdateEstablishmentView(UserPassesTestMixin, UpdateView):
    model = Establishment
    form_class = CreateEstablishmentForm
    template_name = 'establishment/modals/update.html'
    
    def get_success_url(self):
        return reverse_lazy('establishment:establishment_main') + '?tab=management'
    
    def get_queryset(self):
        return Establishment.objects.filter(id_admin_id=self.request.user.id)
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        
        if self.request.method == 'POST':
            data = self.request.POST.copy()
            
            if 'lat_est' in data and data['lat_est']:
                lat_parsed = parse_coordinate(data['lat_est'])
                if lat_parsed is not None:
                    data['lat_est'] = str(lat_parsed)
            
            if 'lng_est' in data and data['lng_est']:
                lng_parsed = parse_coordinate(data['lng_est'])
                if lng_parsed is not None:
                    data['lng_est'] = str(lng_parsed)
            
            form = self.get_form_class()(data, files=self.request.FILES, instance=self.get_object())
        
        return form
    
    def form_valid(self, form):
        try:
            form.instance.id_admin_id = self.request.user.id
            response = super().form_valid(form)
            
            if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({
                    "success": True,
                    "message": "Establecimiento creado exitosamente",
                    "id": self.object.id,
                    "name": self.object.name_est
                })

            return response
        except Exception as e:
            if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({
                    "success": False,
                    "message": "Error al guardar el establecimiento",
                    "error": str(e)
                }, status=500)
            raise
    
    def test_func(self):
        return self.request.user.groups.filter(name='Administrador').exists()
        
    def handle_no_permission(self):
        return redirect('not_in_group')

class CreateEstablishmentView(UserPassesTestMixin, CreateView):
    model = Establishment
    template_name = 'establishment/modals/add.html'
    form_class = CreateEstablishmentForm
    success_url = "/establishment/management/"

    def get_success_url(self):
        return reverse_lazy('establishment:establishment_main') + '?tab=management'

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        
        if self.request.method == 'POST':
            data = self.request.POST.copy()
            
            if 'lat_est' in data and data['lat_est']:
                lat_parsed = parse_coordinate(data['lat_est'])
                if lat_parsed is not None:
                    data['lat_est'] = str(lat_parsed)
            
            if 'lng_est' in data and data['lng_est']:
                lng_parsed = parse_coordinate(data['lng_est'])
                if lng_parsed is not None:
                    data['lng_est'] = str(lng_parsed)
            
            form = self.get_form_class()(data, files=self.request.FILES)
        
        return form

    def form_valid(self, form):
        try:
            form.instance.id_admin_id = self.request.user.id
            response = super().form_valid(form)
            
            if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({
                    "success": True,
                    "message": "Establecimiento creado exitosamente",
                    "id": self.object.id,
                    "name": self.object.name_est
                })

            return response
        except Exception as e:
            if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({
                    "success": False,
                    "message": "Error al guardar el establecimiento",
                    "error": str(e)
                }, status=500)
            raise

    def form_invalid(self, form):
        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            errors = {}
            for field, error_list in form.errors.items():
                errors[field] = list(error_list)
            
            return JsonResponse({
                "success": False,
                "message": "Por favor corrige los errores en el formulario",
                "errors": errors,
                "non_field_errors": list(form.non_field_errors())
            }, status=400)

        return super().form_invalid(form)

    def test_func(self):
        return self.request.user.groups.filter(name='Administrador').exists()

    def handle_no_permission(self):
        return redirect('not_in_group')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['MAPS_APIKEY'] = settings.MAPS_APIKEY
        return context
     
class DeleteEstablishmentView(DeleteView):
    
    def get_success_url(self):
        return reverse_lazy('establishment:establishment_main') + '?tab=management'
    
    def get_queryset(self):
        return Establishment.objects.filter(id_admin_id=self.request.user.id)
 
class ProfileEstablishmentView(TemplateView):
    template_name= 'establishment/tabs/profile_est.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['establecimientos'] = self.request.user.admin_est.all()
        return context
    
