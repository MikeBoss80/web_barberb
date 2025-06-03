from django.views.generic import TemplateView


# Create your views here.
class barberView(TemplateView):
    template_name = 'historial_servicios.html'