from django.shortcuts import render, redirect,get_object_or_404
from django.views.generic import ListView,TemplateView, UpdateView,CreateView,DeleteView, DetailView
from datetime import date, time
from django.utils import timezone
from django.views import View
from .utils.mixins import BreadcrumbMixin
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse, reverse_lazy
from django.db.models import Sum
from .models import Service, Category
from establishment.models import Establishment
from workflows.models import FlowInstance
from services_module.models import ServiceDate
from django.contrib.auth.models import User, Group
from barber_module.models import BarberRequest
from login_module.models import Profile
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from .forms import CreateEstablishmentForm,ServiceDateForm,EditarBarberoEstadoForm,BarberRequestAdminResponseForm, CreateServiceForm, VinculationForm, BarberRequestForm
from django.views.generic.edit import FormView
from workflows.models import FlowInstance, FlowStatus
from admin_module.utils.mixins import CitasQuerysetMixin
from login_module.forms import ProfileEditForm,UserEditForm


class HomeadminView(LoginRequiredMixin, BreadcrumbMixin, TemplateView):
    """Vista Principal Modulo Admin"""
    template_name = 'admin_module/main.html'
    login_url = '/login_module/login/'
    
    def get_breadcrumb(self):
        return [{'label': 'Inicio', 'url': reverse('admin_module:main'), 'icon': 'house-door'}]

    #DATPS TEMPORALES
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Obtener el establecimiento donde el usuario es administrador
        establecimiento = Establishment.objects.filter(id_admin=self.request.user).first()
        
        if not establecimiento:
            # Si el usuario no es admin de ningún establecimiento, retornar contexto vacío
            context.update({
                'today': timezone.now().date(),
                'citas_hoy': 0,
                'barberos_activos': 0,
                'bajo_stock': 0,
                'ingresos_hoy': 0,
                'proximas_citas': [],
                'notificaciones': ['No tienes un establecimiento asignado.'],
            })
            return context

        today=timezone.now().date()

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
        # bajo_stock= Inventory.objects.filter(
        #     establishment=establecimiento,
        #     product=5
        # #Revisar aca quedamos  
        # ).count()

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
            # 'bajo_stock': bajo_stock,
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
        return [{'label': 'Citas', 'url': reverse('admin_module:citas'), 'icon': 'calendar-check'}]

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

class EditarBarberoEstadoView(LoginRequiredMixin, UpdateView):
    model = ServiceDate
    form_class = EditarBarberoEstadoForm
    template_name = 'partials/form_editar_barbero_estado.html'
    success_url = reverse_lazy('admin_module:citas')
    login_url = '/login_module/login/'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

class CrearCitaRapidaView(LoginRequiredMixin, CreateView):
    model = ServiceDate
    form_class = ServiceDateForm
    template_name = 'partials/form_crear_cita.html'
    success_url = reverse_lazy('admin_module:citas')
    login_url = '/login_module/login/'

    def form_valid(self, form):
        # Asignar precio automático desde el servicio
        form.instance.price_total = form.instance.service.service.price_service
        return super().form_valid(form)
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request # Pasar el request al formulario    
        return kwargs
    
class CollapsView(LoginRequiredMixin, BreadcrumbMixin, TemplateView):  
     template_name= 'collabs/collabs.html'
     login_url = '/login_module/login/'
     
     def get_breadcrumb(self):
        return [{'label': 'Colaboradores', 'url': reverse('admin_module:collabs'), 'icon': 'people'}]

     def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        instances = FlowInstance.objects.filter(workflow_type_id=1)
        context['requests'] = instances
        estab_ids = self.request.user.admin_est.all().values_list('id', flat=True)
        users_team = User.objects.filter(profile__establishment_id__in=estab_ids)
        context['team'] = users_team

        return context

class CreateVinculationView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    template_name = 'collabs/solicitudes_barbero.html'
    form_class = VinculationForm
    success_url = reverse_lazy('admin_module:collabs')
    login_url = '/login_module/login/'

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

    
class VinculationDeleteView(LoginRequiredMixin, DeleteView):
    model = FlowInstance
    success_url = reverse_lazy('admin_module:barberos')
    login_url = '/login_module/login/'
     
class BarberRequestListView(LoginRequiredMixin,BreadcrumbMixin, ListView):
    model = BarberRequest
    template_name ='requets/solicitudes_list.html' #plantilla html
    success_url = reverse_lazy('admin_module:barber_solicitudes_list')  # Redirección tras guardar
    context_object_name = 'solicitudes' #nombre variable en el template
    paginate_by = 10 #paginar de 10

    def get_breadcrumb(self):
        return [{'label': 'Solicitudes', 'url': reverse('admin_module:barber_solicitudes_list'), 'icon': 'file-earmark-text'}]
    
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
        return redirect('admin_module:barber_solicitudes_list')

class BarberRequestDetailView(LoginRequiredMixin, BreadcrumbMixin, DetailView):
    model = BarberRequest
    template_name = 'requets/solicitudes_detail.html'
    context_object_name = 'solicitud'

    
    def get_queryset(self):
        """
        Asegura que el barbero solo pueda ver sus propias solicitudes.
        """
        return BarberRequest.objects.filter(barber=self.request.user)

class BarberRequestCreateView(LoginRequiredMixin, BreadcrumbMixin, CreateView):

    model = BarberRequest  # Modelo a crear
    form_class = BarberRequestForm  # Formulario personalizado
    template_name = 'requets/barber_request_form.html'  # HTML a renderizar
    success_url = reverse_lazy('admin_module:barber_solicitudes_list')  # Redirección tras guardar

    def get_breadcrumb(self):
        return [{'label': 'Solicitudes', 'url': reverse('admin_module:solicitud_barbero')}]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Obtener el establecimiento y su administrador
        try:
            perfil = Profile.objects.get(user=user)
            if perfil.establishment:
                context['establecimiento'] = perfil.establishment
                context['administrador'] = perfil.establishment.id_admin
        except Profile.DoesNotExist:
            context['establecimiento'] = None
            context['administrador'] = None
        
        return context

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

    
class CalendarioBarberoView(LoginRequiredMixin, View):
    login_url = '/login_module/login/'
    
    def get(self, request, barbero_id):
        # Aquí podrías cargar datos específicos del barbero, por ahora lo haremos estático
        context = {
            'barbero_id': barbero_id,
            'nombre_barbero': 'Carlos Pérez',  # Lo puedes modificar según el barbero
        }
        return render(request, 'calendario_barbero.html', context)

# Vista para mostrar servicios
class ServiciosView(LoginRequiredMixin, BreadcrumbMixin, TemplateView):
    template_name = 'admin_module/servicios.html'
    login_url = '/login_module/login/'

    def get_breadcrumb(self):
        return [{'label': 'Productos & Servicios', 'url': reverse('admin_module:servicios'), 'icon': 'grid'}]
    
    
   
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        # Traer solo los servicios relacionados al establecimiento
        try:
            # Primero intentar obtener el establecimiento donde el usuario es admin
            establecimiento = Establishment.objects.filter(id_admin=user).first()
            
            # Si no es admin, intentar obtenerlo desde el perfil (para barberos)
            if not establecimiento:
                perfil = Profile.objects.get(user=user)
                establecimiento = perfil.establishment
            
            if establecimiento:
                servicios = (
                    Service.objects.filter(establishmentservice__establishment=establecimiento)
                    .select_related('category')
                    .distinct()
                )
            else:
                servicios = Service.objects.none()
        except (Establishment.DoesNotExist, Profile.DoesNotExist):
            servicios = Service.objects.none()

        context['servicios'] = servicios
        return context

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

class ContenidosView(LoginRequiredMixin, BreadcrumbMixin, TemplateView):
    template_name= 'establecimiento/contenidos.html'
    login_url = '/login_module/login/'
    
    def get_breadcrumb(self):
        return [{'label': 'Establecimiento', 'url': reverse('admin_module:establecimiento'), 'icon': 'building'}]
     
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
            return redirect('/admin_module/establecimiento/')  # o el name de tu url para esta vista

     
# class InventarioView(LoginRequiredMixin, BreadcrumbMixin, TemplateView):
#     template_name= 'inventario/inventario.html'
#     login_url = '/login_module/login/'
    
#     def get_breadcrumb(self):
#         return [{'label': 'Inventario', 'url': reverse('admin_module:inventario'), 'icon': 'box-seam'}]
        
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)

#         context['products'] = Product.objects.all()
#         return context

# class InventarioListView(LoginRequiredMixin, BreadcrumbMixin, ListView):
#     template_name = 'inventario/inventario.html'
#     login_url = '/login_module/login/'
    
#     def get_breadcrumb(self):
#         return [{'label': 'Inventario', 'url': reverse('admin_module:inventario'), 'icon': 'box-seam'}]
    
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)

#         context['products'] = Product.objects.all()
#         return context

# class ProductCreateView(LoginRequiredMixin, BreadcrumbMixin, SuccessMessageMixin, CreateView):
#     template_name = 'inventario/form_product.html'
#     form_class = CreateProductForm
#     success_url = reverse_lazy('admin_module:inventario')
#     login_url = '/login_module/login/'

#     def get_breadcrumb(self):
#         return [
#             {'label': 'Inventario', 'url': reverse('admin_module:inventario'), 'icon': 'box-seam'},
#             {'label': 'Crear Producto', 'url': '', 'icon': 'plus-circle'}
#         ]

#     def form_valid(self, form):
#         product=form.save(commit=False)
#         form.instance.created_by = self.request.user
#         form.instance.updated_by = self.request.user
#         product.save()
#         return super().form_valid(form)

# class ProductUpdateView(LoginRequiredMixin, BreadcrumbMixin, SuccessMessageMixin, UpdateView):
#     model = Product
#     template_name = 'inventario/form_product.html'
#     form_class = CreateProductForm
#     success_url = reverse_lazy('admin_module:inventario')
#     login_url = '/login_module/login/'

#     def get_breadcrumb(self):
#         return [
#             {'label': 'Inventario', 'url': reverse('admin_module:inventario'), 'icon': 'box-seam'},
#             {'label': 'Editar Producto', 'url': '', 'icon': 'pencil-square'}
#         ]

#     def form_valid(self, form):
#         form.instance.updated_by = self.request.user
#         return super().form_valid(form)

# class ProductDeleteView(LoginRequiredMixin, DeleteView):
#     model = Product
#     success_url = reverse_lazy('admin_module:inventario')
#     login_url = '/login_module/login/'
    
     
class ReportesView(LoginRequiredMixin, BreadcrumbMixin, TemplateView):
     template_name= 'reportes/reportes.html'
     login_url = '/login_module/login/'
     
     def get_breadcrumb(self):
        return [{'label': 'Reportes', 'url': reverse('admin_module:reportes'), 'icon': 'graph-up'}]

class SeguridadView(LoginRequiredMixin, BreadcrumbMixin, TemplateView):
     template_name= 'perfil/seguridad.html'
     login_url = '/login_module/login/'
     
     def get_breadcrumb(self):
        return [{'label': 'Seguridad', 'url': reverse('admin_module:seguridad'), 'icon': 'shield-lock'}]

class SoporteView(LoginRequiredMixin, BreadcrumbMixin, TemplateView):
     template_name= 'perfil/soporte.html'
     login_url = '/login_module/login/'
     
     def get_breadcrumb(self):
        return [{'label': 'Soporte', 'url': reverse('admin_module:soporte'), 'icon': 'headset'}]

class PerfilUsuarioView(BreadcrumbMixin, TemplateView):
    template_name = 'perfil/perfil_usuario.html'

    def get_breadcrumb(self):
        return [{'label': 'Perfil', 'url': reverse('admin_module:perfil_usuario'), 'icon': 'person-circle'}]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        usuario = self.request.user
        profile = Profile.objects.get(user=usuario)

        context['usuario'] = usuario
        context['profile'] = profile    
        context['profile_form'] = ProfileEditForm(instance=profile)
        context["user_form"] = UserEditForm(instance=usuario)

        return context

    #
    def post(self, request, *args, **kwargs):
        """ Maneja la actualización del perfil desde el formulario """
        usuario = request.user
        profile = Profile.objects.get(user=usuario)
        user_form = UserEditForm(request.POST, instance=usuario)
        profile_form = ProfileEditForm(request.POST, request.FILES, instance=profile)

        # Validar y guardar el formulario
        if profile_form.is_valid() and user_form.is_valid():
            profile_form.save()
            user_form.save()
            messages.success(request, 'Perfil actualizado correctamente.')
            return redirect('admin_module:perfil_usuario')
        else:
            messages.error(request, 'Por favor corrige los errores en el formulario.')

        context = self.get_context_data(**kwargs)
        context["user_form"] = user_form
        context['profile_form'] = profile_form
        return self.render_to_response(context)
  

""" # Editar perfil 
class EditarPerfilView(LoginRequiredMixin, UpdateView):
#    model = usuario
    fields = ['first_name', 'last_name', 'email', 'username', 'profile__phone', 'profile__address', 'profile__birth_date', 'profile__document']
    template_name = 'perfil/editar_perfil.html'
    success_url = reverse_lazy('perfil:perfil_usuario')

    def get_object(self):
        return self.request.user
 """

class CreateEstablishmentView(BreadcrumbMixin,UserPassesTestMixin, FormView):
    template_name = 'establecimiento/registro_est.html'
    form_class = CreateEstablishmentForm

    def get_success_url(self):
        return '/admin_module/establecimiento/'

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
        return [{'label': 'Registro Establecimiento', 'url': reverse('admin_module:registro_est'), 'icon': 'building-add'}]

class DeleteEstablishmentView(DeleteView):
    
    def get_success_url(self):
        return '/admin_module/establecimiento/'
    
    def get_queryset(self):
        return Establishment.objects.filter(id_admin_id=self.request.user.id)
    
#Solicitudes Barberos
class AdminSolicitudesListView(LoginRequiredMixin,BreadcrumbMixin, ListView):
    model = BarberRequest
    template_name = 'admin_module/solicitudes_list.html'
    context_object_name = 'solicitudes'

    # Breadcrumb (navegación)
    def get_breadcrumb(self):
        return [{'label': 'Solicitudes', 'url': reverse('admin_module:admin_solicitudes_list'), 'icon': 'file-earmark-text'}]

    def get_queryset(self):
        """
        Muestra solo las solicitudes de barberos que pertenecen
        al establecimiento del administrador actual.
        """
        user = self.request.user
        # Obtener el establecimiento donde el usuario es administrador
        establecimiento = Establishment.objects.filter(id_admin=user).first()
        if establecimiento:
            return BarberRequest.objects.filter(establecimiento=establecimiento).order_by('-fecha_solicitud')
        return BarberRequest.objects.none()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        queryset = self.get_queryset()
        
        # Contadores por estado
        context['pendientes_count'] = queryset.filter(estado='pendiente').count()
        context['aprobadas_count'] = queryset.filter(estado='aprobada').count()
        context['rechazadas_count'] = queryset.filter(estado='rechazada').count()
        
        return context
    
class AdminSolicitudesDetailView(LoginRequiredMixin, BreadcrumbMixin, UpdateView):
    model = BarberRequest
    form_class = BarberRequestAdminResponseForm
    template_name = 'admin_module/solicitudes_detail.html'
    context_object_name = 'solicitud'

    def get_breadcrumb(self):
        return [
            {'label': 'Solicitudes', 'url': reverse('admin_module:admin_solicitudes_list'), 'icon': 'file-earmark-text'},
            {'label': 'Detalle', 'url': '', 'icon': 'eye'}
        ]

    def dispatch(self, request, *args, **kwargs):
        # Obtener la solicitud
        solicitud = self.get_object()
        
        # Si la solicitud ya fue procesada (aprobada o rechazada), no permitir modificaciones
        if solicitud.estado != 'pendiente' and request.method == 'POST':
            from django.contrib import messages
            messages.warning(request, 'Esta solicitud ya ha sido procesada y no puede ser modificada.')
            return redirect('admin_module:admin_solicitudes_list')
        
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        # Estado enviado en POST (desde los botones)
        estado_nuevo = self.request.POST.get('accion_estado')

        if estado_nuevo in ['aprobada', 'rechazada']:
            form.instance.estado = estado_nuevo

        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('admin_module:admin_solicitudes_list')


class SelecGrupoView(LoginRequiredMixin, TemplateView):
    """Vista para visualizar y modificar los roles activos del usuario en el sistema"""
    template_name = 'perfil/seleccionar_rol.html'
    
    def dispatch(self, request, *args, **kwargs):
        """Permitir que esta vista se cargue en un iframe"""
        response = super().dispatch(request, *args, **kwargs)
        # Eliminar la restricción X-Frame-Options para permitir iframe
        response['X-Frame-Options'] = 'SAMEORIGIN'
        return response
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Obtener grupos actuales del usuario
        user_groups = user.groups.values_list('name', flat=True)
        
        context['user_groups'] = list(user_groups)
        context['has_role'] = user.groups.exists()
        
        # Información de cada rol
        context['roles_info'] = {
            'Cliente': {
                'icon': 'person',
                'description': 'Acceso como cliente de la barbería',
                'features': ['Reservar citas', 'Ver servicios disponibles', 'Historial de citas', 'Calificar servicios']
            },
            'Barbero': {
                'icon': 'scissors',
                'description': 'Acceso como barbero profesional',
                'features': ['Gestionar agenda', 'Atender clientes', 'Ver solicitudes', 'Vincularse a establecimientos']
            },
            'Administrador': {
                'icon': 'gear',
                'description': 'Gestión completa del establecimiento',
                'features': ['Crear establecimientos', 'Gestionar barberos', 'Aprobar solicitudes', 'Ver reportes']
            }
        }
        
        return context
    
    def post(self, request, *args, **kwargs):
        """Manejar la modificación de roles del usuario"""
        user = request.user
        selected_roles = request.POST.getlist('roles')  # Lista de roles seleccionados
        
        # Roles válidos en el sistema
        valid_roles = ['Cliente', 'Barbero', 'Administrador']
        
        # Validar que al menos se seleccionó un rol
        if not selected_roles:
            messages.warning(request, 'Debes seleccionar al menos un rol.')
            return redirect('admin_module:seleccionar_rol')
        
        # Validar que todos los roles seleccionados sean válidos
        for role in selected_roles:
            if role not in valid_roles:
                messages.error(request, f'El rol "{role}" no es válido.')
                return redirect('admin_module:seleccionar_rol')
        
        try:
            # Limpiar todos los grupos actuales del usuario
            user.groups.clear()
            
            # Agregar los nuevos grupos seleccionados
            for role_name in selected_roles:
                group, created = Group.objects.get_or_create(name=role_name)
                user.groups.add(group)
            
            messages.success(request, 'Tus roles se han actualizado correctamente.')
            
        except Exception as e:
            messages.error(request, f'Error al actualizar roles: {str(e)}')
        
        return redirect('admin_module:seleccionar_rol')
    
    
    
    
    

