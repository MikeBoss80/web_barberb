# admin_modulo/utils/mixins.py
from django.urls import reverse

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
