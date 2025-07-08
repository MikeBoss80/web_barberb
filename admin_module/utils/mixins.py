# admin_modulo/utils/mixins.py
from django.urls import reverse
from services_module.models import ServiceDate


class BreadcrumbMixin:
    breadcrumb = []

    def get_breadcrumb(self):
        return ['Inicio'] + self.breadcrumb

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
# admin_module/utils/mixins.py

class BreadcrumbMixin:
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        breadcrumb = []
        if hasattr(self, 'get_breadcrumb'):
            breadcrumb = self.get_breadcrumb()
        elif hasattr(self, 'breadcrumb'):
            breadcrumb = self.breadcrumb

        # Insertamos "Inicio" como primer breadcrumb
        context['breadcrumb'] = [{'label': 'Inicio', 'url': reverse('admin_module:admin_main')}] + breadcrumb
        return context


class CitasQuerysetMixin:
    def get_citas_queryset(self, user=None, filter_by_barber=False, filter_by_client=False):
        queryset = ServiceDate.objects.all()
        
        if filter_by_barber and user:
            queryset = queryset.filter(barber=user.profile)  # Asegúrate que tengas relación Profile-Barber
        if filter_by_client and user:
            queryset = queryset.filter(client=user.profile)  # Igual relación Profile-Client
        
        return queryset