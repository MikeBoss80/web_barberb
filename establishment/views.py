from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import TemplateView, FormView, DeleteView, UpdateView
from django.contrib.auth.mixins import UserPassesTestMixin
from .forms import CreateEstablishmentForm
from admin_module.models import Establishment

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
    
    def get_success_url(self):
        return reverse_lazy('establishment:establishment_main') + '?tab=management'

    def form_valid(self, form):
        establishment = form.save(commit=False)
        establishment.id_admin_id = self.request.user.id
        establishment.save()
        return super().form_valid(form)

    def test_func(self):
        return self.request.user.groups.filter(name='Administrador').exists()
        
    def handle_no_permission(self):
        return redirect('not_in_group')

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
    
