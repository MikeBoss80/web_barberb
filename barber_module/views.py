from django.shortcuts import get_object_or_404, render, redirect
from django.views.generic import ListView,TemplateView, UpdateView,CreateView,DeleteView ,DetailView
from datetime import date, time
from django.utils import timezone
from django.views import View
from admin_module.models import Establishment
from workflows.models import FlowInstance, FlowStatus
from .utils.mixins import BreadcrumbMixin
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse, reverse_lazy
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from login_module.models import Profile  # Si tienes relación barbero <-> establecimiento en Profile
from .models import BarberRequest
from .forms import BarberRequestForm
from admin_module.utils.mixins import CitasQuerysetMixin



from django.views.generic import TemplateView


# Create your views here.

class HomeBarberView(BreadcrumbMixin, TemplateView):
    """Vista Principal Modulo Barber"""
    template_name = 'barber_module/main.html'
    login_url = '/login_module/login/'
    
    def get_breadcrumb(self):
        return []

    #DATPS TEMPORALES
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context.update({
            'user': self.request.user,
            'today': timezone.now(),
            'citas_hoy': 8,
            'ingresos_hoy': 420.00,
            'barberos_activos': 3,
            'bajo_stock': 2,
            'proximas_citas': [
                {'hora': '10:00', 'cliente': 'Carlos Pérez', 'servicio': 'Corte', 'barbero': 'Andrés'},
                {'hora': '11:00', 'cliente': 'Luis Soto', 'servicio': 'Barba', 'barbero': 'Miguel'}
            ],
            'labels': ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes'],
            'ingresos_data': [100, 200, 150, 300, 250],
            'servicios_labels': ['Corte', 'Barba', 'Corte + Barba'],
            'servicios_data': [10, 5, 8],
            'notificaciones': [
                'Hay 2 productos con stock bajo.',
                'Un barbero no ha iniciado su turno.',
            ]
        })

        return context

class barberView(TemplateView):
    template_name = 'historial_servicios.html'
    
class BarberCitasView(UserPassesTestMixin, BreadcrumbMixin, TemplateView,CitasQuerysetMixin):
    template_name = 'citas_barbero.html'

    def test_func(self):
        return self.request.user.groups.filter(name='Administrador').exists()

    def handle_no_permission(self):
        return redirect('not_in_group')
    
    def get_breadcrumb(self):
        return [{'label': 'Citas Barbero', 'url': reverse('barber_module:citas_barbero')}]

    context_object_name = 'dates'

    def get_queryset(self):
        return self.get_citas_queryset(user=self.request.user, filter_by_barber=True)


class BarberRequestCreateView(LoginRequiredMixin, BreadcrumbMixin, CreateView):

    model = BarberRequest  # Modelo a crear
    form_class = BarberRequestForm  # Formulario personalizado
    template_name = 'requets/barber_request_form.html'  # HTML a renderizar
    success_url = reverse_lazy('barber_module:barber_solicitudes_list')  # Redirección tras guardar

    def get_breadcrumb(self):
        return [{'label': 'Solicitudes', 'url': reverse('barber_module:solicitud_barbero')}]


    def form_valid(self, form):
        """
        Este método se ejecuta si el formulario es válido.
        Aquí se asignan automáticamente el barbero y el establecimiento.
        """
        user = self.request.user  # Barbero autenticado

        form.instance.barber = user  # Asigna el barbero automáticamente

        # Asignar el establecimiento al que pertenece este barbero
        # Si usas un modelo Profile, y allí está la relación con el establecimiento:
        perfil = Profile.objects.get(user=user)
        form.instance.establecimiento = perfil.establishment  # Asegúrate que esto esté definido en Profile

        return super().form_valid(form)

class BarberRequestListView(LoginRequiredMixin,BreadcrumbMixin, ListView):
    model = BarberRequest
    template_name ='requets/solicitudes_list.html' #plantilla html
    success_url = reverse_lazy('barber_module:barber_solicitudes_list')  # Redirección tras guardar
    context_object_name = 'solicitudes' #nombre variable en el template
    paginate_by = 10 #paginar de 10

    def get_queryset(self):
        #Filtra las solicitudes para que el barbero solo vea las suyas,
        #ordenadas por fecha descendente.
        return BarberRequest.objects.filter(barber=self.request.user).order_by('-fecha_solicitud')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        request_vinculation = FlowInstance.objects.filter(workflow_type_id=1,recipient=self.request.user).order_by('-created_at')
        context['requests'] = request_vinculation

        return context

class BarberValidateVinculation(View):
    def post(self, request, *args, **kwargs):
        pk = self.kwargs['pk']
        value = self.kwargs['value']
        solicitud = get_object_or_404(FlowInstance, pk=pk)

        if bool(value):
            new_status = get_object_or_404(FlowStatus, name='Confirmada')
            vinculation_est = solicitud.created_by.admin_est.first()
            print(vinculation_est)
            self.request.user.profile.establishment = vinculation_est
            profile = self.request.user.profile
            profile.establishment = vinculation_est
            profile.save()
        else:
            new_status = get_object_or_404(FlowStatus, name='Cancelada')
        # else:
        #     messages.error(request, 'Acción no válida.')
        #     return redirect('admin_module:barberos')  # Ajusta el nombre de redirección
        solicitud.status = new_status
        solicitud.save()

        # messages.success(request, f'Solicitud actualizada a {new_status.name}')
        return redirect('barber_module:barber_solicitudes_list')

class BarberRequestDetailView(LoginRequiredMixin, BreadcrumbMixin, DetailView):
    model = BarberRequest
    template_name = 'requets/solicitudes_detail.html'
    context_object_name = 'solicitud'

    def get_queryset(self):
        """
        Asegura que el barbero solo pueda ver sus propias solicitudes.
        """
        return BarberRequest.objects.filter(barber=self.request.user)


class BarberContenidosView(BreadcrumbMixin, TemplateView):
     template_name= 'contenidos_barbero.html'
     def get_breadcrumb(self):
        return [{'label': 'Contenidos', 'url': reverse('barber_module:contenidos')}]
     
class InventarioView(BreadcrumbMixin, TemplateView):
     template_name= 'inventario.html'
     def get_breadcrumb(self):
        return [{'label': 'Inventario', 'url': reverse('barber_module:inventario')}]


class BarberReportesView(BreadcrumbMixin, TemplateView):
     template_name= 'reportes.html'
     def get_breadcrumb(self):
        return [{'label': 'Reportes', 'url': reverse('barber_module:reportes')}]



class BarberSeguridadView(BreadcrumbMixin, TemplateView):
     template_name= 'seguridad.html'
     def get_breadcrumb(self):
        return [{'label': 'Seguridad', 'url': reverse('barber_module:seguridad')}]


class SoporteView(BreadcrumbMixin, TemplateView):
     template_name= 'soporte.html'
     def get_breadcrumb(self):
        return [{'label': 'Soporte', 'url': reverse('barber_module:soporte')}]


class PerfilUsuarioView(BreadcrumbMixin, TemplateView):
     template_name ='perfil_usuario.html'
     def get_breadcrumb(self):
        return [{'label': 'Perfil', 'url': reverse('barber_module:perfil_usuario')}]
    
    
     def get_context_data(self, **kwargs):
        usuario = "Miguel Bolivar"
        context = super().get_context_data(**kwargs)
        context['usuario'] = self.request.user  # Agrega el usuario autenticado al contexto
        return context

# Editar perfil (nombre y email básico)
class EditarPerfilView(LoginRequiredMixin, UpdateView):
#    model = usuario
    fields = ['first_name', 'last_name', 'email']
    template_name = 'perfil/editar_perfil.html'
    success_url = reverse_lazy('perfil:perfil_usuario')

    def get_object(self):
        return self.request.user
    
class LogoutView(BreadcrumbMixin, TemplateView):
    template_name='core/login.html'
