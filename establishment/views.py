from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import TemplateView, FormView, DeleteView, UpdateView
from django.contrib.auth.mixins import UserPassesTestMixin
from .forms import CreateEstablishmentForm
from admin_module.models import Establishment
from django.conf import settings
from django.http import JsonResponse



class EstablishmentMainView(TemplateView):
    template_name= 'establishment_base.html'

    # def get_breadcrumb(self):
    #     return [{'label': 'Establecimiento', 'url': reverse('admin_module:establecimiento')}]

class EstablishmentManagementView(TemplateView):
    template_name= 'tabs/management.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['establecimientos'] = self.request.user.admin_est.all()
        context['form'] = CreateEstablishmentForm()
        return context

class UpdateEstablishmentView(UserPassesTestMixin, UpdateView):
    model = Establishment
    form_class = CreateEstablishmentForm
    template_name = 'modals/update.html'
    
    def get_success_url(self):
        return reverse_lazy('establishment:establishment_main') + '?tab=management'
    
    def get_queryset(self):
        return Establishment.objects.filter(id_admin_id=self.request.user.id)
    
    def test_func(self):
        return self.request.user.groups.filter(name='Administrador').exists()
        
    def handle_no_permission(self):
        return redirect('not_in_group')

class CreateEstablishmentView(UserPassesTestMixin, FormView):
    template_name = 'modals/add.html'
    form_class = CreateEstablishmentForm
    success_url = "/establishment/management/"  # Ajusta según tu proyecto


    def get_success_url(self):
        return reverse_lazy('establishment:establishment_main') + '?tab=management'

    def form_valid(self, form):
        try:
            establishment = form.save(commit=False)
            establishment.id_admin_id = self.request.user.id
            establishment.save()

            # Si es AJAX, devolver JSON con mensaje de éxito
            if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({
                    "success": True,
                    "message": "Establecimiento creado exitosamente",
                    "id": establishment.id,
                    "name": establishment.name_est
                })

            return super().form_valid(form)
        except Exception as e:
            if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({
                    "success": False,
                    "message": "Error al guardar el establecimiento",
                    "error": str(e)
                }, status=500)
            raise

    def form_invalid(self, form):
        # Si es AJAX, devolver errores estructurados en JSON
        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            errors = {}
            for field, error_list in form.errors.items():
                errors[field] = list(error_list)  # Convertir ErrorList a lista
            
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
    template_name= 'tabs/profile_est.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['establecimientos'] = self.request.user.admin_est.all()
        return context
    
