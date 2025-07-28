from django.shortcuts import render, redirect,get_object_or_404
from django.views.generic import ListView,TemplateView, UpdateView,CreateView,DeleteView 
from datetime import date, time
from django.utils import timezone
from django.views import View
from .utils.mixins import BreadcrumbMixin
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse, reverse_lazy
from django.db.models import Sum
from .models import Product, Establishment,Inventory, Service, Category
from workflows.models import FlowInstance
from services_module.models import ServiceDate
from django.contrib.auth.models import User
from barber_module.models import BarberRequest
from login_module.models import Profile
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from .forms import CreateProductForm, CreateEstablishmentForm,ServiceDateForm,EditarBarberoEstadoForm,BarberRequestAdminResponseForm, CreateServiceForm, VinculationForm
from django.views.generic.edit import FormView
from collections import defaultdict
from admin_module.models import Category 
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt



from admin_module.utils.mixins import CitasQuerysetMixin





class HomeadminView(BreadcrumbMixin, TemplateView):
    """Vista Principal Modulo Admin"""
    template_name = 'admin_module/main.html'
    login_url = '/login_module/login/'
    
    def get_breadcrumb(self):
        return []

    #DATPS TEMPORALES
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Obtener el establecimiento del admin
        perfil=Profile.objects.get(user=self.request.user)
        establecimiento = perfil.establishment

        today=timezone.localtime().date()

        #Citas del dia
        citas_hoy=ServiceDate.objects.filter(
            date=today,
            service__establishment=establecimiento
        ).count()

        #Barberos activos
        barberos_activos = Profile.objects.filter(
            establishment=establecimiento,
            user__is_active=True,
            user__groups__name='Barbero'  
        ).count()

        #Productos bajo stock
        bajo_stock= Inventory.objects.filter(
            establishment=establecimiento,
            product=5
        #Revisar aca quedamos  
        ).count()

        # Ingresos del día
        ingresos_hoy = ServiceDate.objects.filter(
            date=today,
            service__establishment=establecimiento
        ).aggregate(total=Sum('price_total'))['total'] or 0

        # Próximas citas (de hoy en adelante)
        proximas_citas = ServiceDate.objects.filter(
            date__gte=today,
            service__establishment=establecimiento
        ).order_by('date', 'date')[:5]

        # Notificaciones del sistema (ejemplo: solicitudes pendientes)
        solicitudes_pendientes = BarberRequest.objects.filter(
            establecimiento=establecimiento,
            estado='pendiente'
        ).count()

        notificaciones = []
        if solicitudes_pendientes:
            notificaciones.append(f"Tienes {solicitudes_pendientes} solicitudes de barberos pendientes por revisar.")

        context.update({
            'today': today,
            'citas_hoy': citas_hoy,
            'barberos_activos': barberos_activos,
            'bajo_stock': bajo_stock,
            'ingresos_hoy': ingresos_hoy,
            'proximas_citas': proximas_citas,
            'notificaciones': notificaciones,
        })

        return context

class CitasView(UserPassesTestMixin, BreadcrumbMixin, TemplateView, CitasQuerysetMixin):
    template_name = 'citas/citas.html'

    # Validación: solo los usuarios en el grupo 'Administrador' pueden acceder
    def test_func(self):
        User = self.request.user
        return (
            User.groups.filter(name='Administrador').exists() or
            User.groups.filter(name='Barbero').exists() or 
            User.groups.filter(name='Cliente').exists()
        )       

    # Redirección si no tiene permiso
    def handle_no_permission(self):
        return redirect('not_in_group')
    
    # Breadcrumb (navegación)
    def get_breadcrumb(self):
        return [{'label': 'Citas', 'url': reverse('admin_module:citas')}]

    # Contexto que se pasa a la plantilla
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Obtener el usuario actual
        user = self.request.user
        establishment = None
        rol = self.request.session.get('current_role')


        # ADMINISTRADOR
        # Buscar el establecimiento que administra este usuario
          # ADMINISTRADOR
        if rol == 'Administrador':
            try:
                establecimiento = Establishment.objects.get(id_admin=user)
                citas = ServiceDate.objects.select_related(
                    'service', 'service__establishment', 'barber', 'customer'
                ).filter(service__establishment=establecimiento)
            except Establishment.DoesNotExist:
                pass

        # BARBERO
        elif rol == 'Barbero':
            establecimiento = getattr(user.profile, 'establishment_id', None)
            if establecimiento:
                citas = ServiceDate.objects.select_related(
                    'service', 'service__establishment', 'barber', 'customer'
                ).filter(service__establishment=establecimiento, barber=user)

        # CLIENTE
        elif rol == 'Cliente':
            citas = ServiceDate.objects.select_related(
                'service', 'service__establishment', 'barber', 'customer'
            ).filter(customer=user)

        # Agregar citas al contexto
        context['dates'] = citas

        # Mostrar barberos si es administrador con establecimiento
        if rol == 'Administrador' and establecimiento:
            context['barberos'] = User.objects.filter(
                groups__name='Barbero',
                profile__establishment=establecimiento
            )
        else:
            context['barberos'] = None

        # Resumen de citas
        context['resumen'] = {
            'total_dates': citas.count(),
            'completadas': citas.filter(status='Completada').count(),
            'agendadas': citas.filter(status='Agendada').count(),
            'canceladas': citas.filter(status='Cancelada').count(),
        }

        context['fecha_actual'] = date.today()
        return context

def cancelar_cita(request):
    if request.method == "POST":
        date_id = request.POST.get("date_id")
        date = get_object_or_404(ServiceDate, id=date_id)
        date.status = 'Cancelada'
        date.save()
    return redirect('admin_module:citas')

class EditarBarberoEstadoView(UpdateView):
    model = ServiceDate
    form_class = EditarBarberoEstadoForm
    template_name = 'partials/form_editar_barbero_estado.html'
    success_url = reverse_lazy('admin_module:citas')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

class CrearCitaRapidaView(CreateView):
    model = ServiceDate
    form_class = ServiceDateForm
    template_name = 'partials/form_crear_cita.html'
    success_url = reverse_lazy('admin_module:citas')

    def form_valid(self, form):
        # Asignar precio automático desde el servicio
        form.instance.price_total = form.instance.service.service.price_service
        return super().form_valid(form)
    
class CrearCitaFormView(View):
     def get(self, request, *args, **kwargs):
        form = ServiceDateForm
        return render(request, 'partials/form_crear_cita.html', {'form': form})
    
class CollapsView(BreadcrumbMixin, TemplateView):  
     template_name= 'collabs/collabs.html'
     
     def get_breadcrumb(self):
        return [{'label': 'Colaboradores', 'url': reverse('admin_module:collabs')}]

     def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        instances = FlowInstance.objects.filter(workflow_type_id=1)
        context['requests'] = instances
        estab_ids = self.request.user.admin_est.all().values_list('id', flat=True)
        users_team = User.objects.filter(profile__establishment_id__in=estab_ids)
        context['team'] = users_team

        return context

class CreateVinculationView(SuccessMessageMixin, CreateView):
    template_name = 'collabs/solicitudes_barbero.html'
    form_class = VinculationForm
    success_url = reverse_lazy('admin_module:collabs')

    def form_valid(self, form):
        documento = form.cleaned_data.get('document')
        instance=form.save(commit=False)
        instance.created_by = self.request.user
        instance.updated_by = self.request.user

        try:
            colaborator = User.objects.filter(profile__document=documento).last() #Se toma el ultimo
            #TODO: Esto debe cambiarse, no deberia existir usuarios con el mismo documento 
            # o si no, realizar la validacion por algun id unico
            instance.status_id =  4
            instance.recipient = colaborator  # lo vinculamos si existe
            # messages.success(self.request, "Colaborador encontrado, solicitud enviada.")
        except User.DoesNotExist:
            instance.status_id =  4
            instance.recipient = self.request.user  # o dejar el campo nulo

        instance.save()
        return super().form_valid(form)
    
class VinculationDeleteView(DeleteView):
    model = FlowInstance
    success_url = reverse_lazy('admin_module:barberos')
     
class CalendarioBarberoView(View):
    def get(self, request, barbero_id):
        # Aquí podrías cargar datos específicos del barbero, por ahora lo haremos estático
        context = {
            'barbero_id': barbero_id,
            'nombre_barbero': 'Carlos Pérez',  # Lo puedes modificar según el barbero
        }
        return render(request, 'calendario_barbero.html', context)

# Vista para mostrar servicios
class ServiciosView(View):
    def get(self, request):
        servicios = Service.objects.all().select_related('category')
        return render(request, 'admin_module/servicios.html', {'servicios': servicios})

# Agregar servicio
def agregar_servicio(request):
    if request.method == 'POST':
        form = CreateServiceForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('admin_module:servicios')
        else:
            # Aquí se imprime en consola si hay errores
            print("⚠️ Errores del formulario:", form.errors)
    else:
        form = CreateServiceForm()
    
    return render(request, 'admin_module/form_servicio.html', {
    'form': form,
    'action_url': reverse('admin_module:agregar_servicio')
})# Editar servicio
def editar_servicio(request, id):
    servicio = get_object_or_404(Service, id=id)
    if request.method == 'POST':
        form = CreateServiceForm(request.POST, instance=servicio)
        if form.is_valid():
            form.save()
            return redirect('admin_module:servicios')
    else:
        form = CreateServiceForm(instance=servicio)
        return render(request, 'admin_module/form_servicio.html', {
    'form': form,
    'action_url': reverse('admin_module:editar_servicio', args=[servicio.id])
})
# Eliminar servicio
def eliminar_servicio(request, id):
    servicio = get_object_or_404(Service, id=id)
    servicio.delete()
    return redirect('admin_module:servicios')

class ContenidosView(BreadcrumbMixin, TemplateView):
    template_name= 'establecimiento/contenidos.html'
    def get_breadcrumb(self):
        return [{'label': 'Contenidos', 'url': reverse('admin_module:contenidos')}]
     
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Cargar todos los establecimientos (o el actual del admin, si aplica)
        context['establecimientos'] = self.request.user.admin_est.all()

        # Si se quiere pasar un formulario vacío para registrar o editar desde modal
        context['form'] = CreateEstablishmentForm()
        return context
    
    def post(self, request, *args, **kwargs):
        # Captura del establecimiento a editar (por ejemplo, con un input hidden)
        establishment_id = request.POST.get('establishment_id')
        if establishment_id:
            # Es edición
            establishment = get_object_or_404(Establishment, pk=establishment_id)
            form = CreateEstablishmentForm(request.POST, instance=establishment)
        else:
            # Es creación
            form = CreateEstablishmentForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect('/admin_module/contenidos/')  # o el name de tu url para esta vista

        # Si hay errores, recarga la página con el mismo contexto
        context = self.get_context_data(instance=establishment)
        context['form'] = form
        return self.render_to_response(context)
     
class InventarioView(BreadcrumbMixin, TemplateView):
    template_name= 'inventario/inventario.html'
    def get_breadcrumb(self):
        return [{'label': 'Inventario', 'url': reverse('admin_module:inventario')}]
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['products'] = Product.objects.all()
        return context

class InventarioListView(ListView):

    
    # product = Product
    template_name = 'inventario/inventario.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['products'] = Product.objects.all()
        return context

class ProductCreateView(SuccessMessageMixin, CreateView):
    template_name = 'inventario/form_product.html'
    form_class = CreateProductForm
    success_url = reverse_lazy('admin_module:inventario')

    def form_valid(self, form):
        product=form.save(commit=False)
        form.instance.created_by = self.request.user
        form.instance.updated_by = self.request.user
        product.save()
        return super().form_valid(form)

class ProductUpdateView(SuccessMessageMixin, UpdateView):
    model = Product
    template_name = 'inventario/form_product.html'
    form_class = CreateProductForm
    success_url = reverse_lazy('admin_module:inventario')

    def form_valid(self, form):
        form.instance.updated_by = self.request.user
        return super().form_valid(form)

class ProductDeleteView(DeleteView):
    model = Product
    success_url = reverse_lazy('admin_module:inventario')
    
    # Filtrar o determinar por aquello que si puedo eliminar y si no cumple pues lanzar error
    # def get_queryset(self):
    #     return Product.objects.filter(id_admin_id=self.request.user.id)   
     
class ReportesView(BreadcrumbMixin, TemplateView):
     template_name= 'reportes/reportes.html'
     def get_breadcrumb(self):
        return [{'label': 'Reportes', 'url': reverse('admin_module:reportes')}]

class SeguridadView(BreadcrumbMixin, TemplateView):
     template_name= 'perfil/seguridad.html'
     def get_breadcrumb(self):
        return [{'label': 'Seguridad', 'url': reverse('admin_module:seguridad')}]

class SoporteView(BreadcrumbMixin, TemplateView):
     template_name= 'perfil/soporte.html'
     def get_breadcrumb(self):
        return [{'label': 'Soporte', 'url': reverse('admin_module:soporte')}]

class PerfilUsuarioView(BreadcrumbMixin, TemplateView):
     template_name ='perfil/perfil_usuario.html'
     def get_breadcrumb(self):
        return [{'label': 'Perfil', 'url': reverse('admin_module:perfil_usuario')}]
    
    
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

class CreateEstablishmentView(BreadcrumbMixin,UserPassesTestMixin , FormView):
    template_name = 'establecimiento/registro_est.html'
    form_class = CreateEstablishmentForm

    def get_success_url(self):
        return '/admin_module/contenidos/'

    def form_valid(self, form):
        establishment=form.save(commit=False)
        establishment.id_admin_id=self.request.user.id
        establishment.save()
        return super().form_valid(form)


    def test_func(self):
        return self.request.user.groups.filter(name='Administrador').exists()
        
    def handle_no_permission(self):
        return redirect('not_in_group')
    
    def get_breadcrumb(self):
        return [{'label': 'Registro Establecimiento', 'url': reverse('admin_module:registro_est')}]

class DeleteEstablishmentView(DeleteView):
    
    def get_success_url(self):
        return '/admin_module/contenidos/'
    
    def get_queryset(self):
        return Establishment.objects.filter(id_admin_id=self.request.user.id)
    
#Solicitudes Barberos
class AdminSolicitudesListView(LoginRequiredMixin, ListView):
    model = BarberRequest
    template_name = 'admin_module/solicitudes_list.html'
    context_object_name = 'solicitudes'

    def get_queryset(self):
        """
        Muestra solo las solicitudes de barberos que pertenecen
        al establecimiento del administrador actual.
        """
        user = self.request.user
        perfil_admin = Profile.objects.get(user=user)
        establecimiento = perfil_admin.establishment
        return BarberRequest.objects.filter(establecimiento=establecimiento).order_by('-fecha_solicitud')
    
class AdminSolicitudesDetailView(LoginRequiredMixin, UpdateView):
    model = BarberRequest
    form_class = BarberRequestAdminResponseForm
    template_name = 'admin_module/solicitudes_detail.html'
    context_object_name = 'solicitud'

    def form_valid(self, form):
        # Estado enviado en POST (desde los botones)
        estado_nuevo = self.request.POST.get('accion_estado')

        if estado_nuevo in ['aprobada', 'rechazada']:
            form.instance.estado = estado_nuevo

        return super().form_valid(form)

def get_success_url(self):
        return reverse_lazy('admin_module:admin_solicitudes_list')    
    
