from django.shortcuts import render, redirect,get_object_or_404
from django.views.generic import ListView,TemplateView, UpdateView,CreateView,DeleteView 
from datetime import date, time
from django.utils import timezone
from django.views import View
from .utils.mixins import BreadcrumbMixin
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse, reverse_lazy
from .models import Product, Establishment
from services_module.models import ServiceDate
from django.contrib.auth.models import User

from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from .forms import CreateProductForm, CreateEstablishmentForm
from django.views.generic.edit import FormView




class HomeadminView(BreadcrumbMixin, TemplateView):
    """Vista Principal Modulo Admin"""
    template_name = 'admin_module/main.html'
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


class CitasView(UserPassesTestMixin, BreadcrumbMixin, TemplateView):
    template_name = 'citas/citas.html'

    def test_func(self):
        return self.request.user.groups.filter(name='Administrator').exists()

    def handle_no_permission(self):
        return redirect('not_in_group')
    
    def get_breadcrumb(self):
        return [{'label': 'Citas', 'url': reverse('admin_module:citas')}]


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)


        # Cargar citas relacionadas con los establecimientos administrados por el usuario
       # admin_establishment  = self.request.user.admin_est.all()

        """ ids_est =[]        
        for establishment in admin_establishment:
            ids_est.append(establishment.id) """

        """ response=[]
        dates_est = ServiceDate.objects.select_related('customer', 'barber', 'service')
        for date in dates_est:
            customer_info=User.objects.filter(id=date.customer_id)
            response.append({
                "date" : date.date,
                "customer_id": date.customer_id.customer_dates.first_name,
                "barber_id" : "date.barber_id.first_name",
                "service_id": "date.service_id.name_service",
                "price_total":"date.price_total",
            }) """

        context['dates'] = ServiceDate.objects.select_related('customer', 'barber', 'service')
        context['barberos'] = User.objects.filter(groups__name='Barber')



    # Puedes pasar un formulario vacío si quieres editar desde modal
    #    context['form'] = AppointmentForm()
        return context

class ActualizarCitaView(View):
    def post(self, request):
        cita_id = request.POST.get('date_id')
        nuevo_barbero_id = request.POST.get('barber_id')
        nuevo_estado = request.POST.get('status')

        cita = get_object_or_404(ServiceDate, id=cita_id)

        # Actualizar campos permitidos
        cita.barber_id = nuevo_barbero_id
        cita.status = nuevo_estado
        cita.save()

        return redirect('admin_module:citas')  # o a donde estés redirigiendo luego


class BarberosView(BreadcrumbMixin, TemplateView):  
     template_name= 'barberos/barberos.html'
     
     def get_breadcrumb(self):
        return [{'label': 'Barberos', 'url': reverse('admin_module:barberos')}]

     #DATOS TEMPORALES
     def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['barberos'] = [
            {
                'id': 1,
                'nombre': 'Miguel Bolivar',
                'foto_url': 'https://via.placeholder.com/150',
                'especialidades': 'Cortes Masculinos, Tinte',
                'horario': 'Lunes a Miércoles, 9am - 5pm',
                'ingresos_generados': 1500.00,  # Ejemplo de otro barbero
                'rating': 4.9,
            },
            {
                'id': 2,
                'nombre': 'Carlos Pérez',
                'foto_url': 'https://via.placeholder.com/150',
                'especialidades': 'Cortes modernos, Barba',
                'horario': 'Lunes a Viernes, 10am - 6pm',
                'ingresos_generados': 450.00,  # Aquí van los ingresos estáticos
                'rating': 4.8,
            },
            {
                'id': 3,
                'nombre': 'Luis Martínez',
                'foto_url': 'https://via.placeholder.com/150',
                'especialidades': 'Afeitados, Degradados',
                'horario': 'Martes a Sábado, 12pm - 8pm',
                'ingresos_generados': 320.00,  # Ingresos estáticos también
                'rating': 4.5,
            },
            {
                'id': 4,
                'nombre': 'Ana Gómez',
                'foto_url': 'https://via.placeholder.com/150',
                'especialidades': 'Cortes femeninos, Tinte',
                'horario': 'Lunes a Miércoles, 9am - 5pm',
                'ingresos_generados': 500.00,  # Ejemplo de otro barbero
                'rating': 4.9,
            },
        ]
        return context
     
class CalendarioBarberoView(View):
    def get(self, request, barbero_id):
        # Aquí podrías cargar datos específicos del barbero, por ahora lo haremos estático
        context = {
            'barbero_id': barbero_id,
            'nombre_barbero': 'Carlos Pérez',  # Lo puedes modificar según el barbero
        }
        return render(request, 'calendario_barbero.html', context)
    

class ServiciosView(BreadcrumbMixin, TemplateView):
     template_name= 'establecimiento\servicios.html'
     def get_breadcrumb(self):
        return [{'label': 'Servicios', 'url': reverse('admin_module:servicios')}]

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
    template_name = 'inventario/add_product.html'
    form_class = CreateProductForm
    
    def get_success_url(self):
        return '/admin_module/inventario/'

    def form_valid(self, form):
        product=form.save(commit=False)
        # product.id_admin_id=self.request.user.id
        product.save()
        return super().form_valid(form)

class ProductoUpdateView(SuccessMessageMixin, UpdateView):
    model = Product
    # form_class = ProductoForm
    # template_name = 'establecimiento/modal_producto.html'
    # success_url = reverse_lazy('inventario')
    # success_message = "Producto actualizado exitosamente"

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
        return self.request.user.groups.filter(name='Administrator').exists()
        
    def handle_no_permission(self):
        return redirect('not_in_group')
    
    def get_breadcrumb(self):
        return [{'label': 'Registro Establecimiento', 'url': reverse('admin_module:registro_est')}]

class DeleteEstablishmentView(DeleteView):
    
    def get_success_url(self):
        return '/admin_module/contenidos/'
    
    def get_queryset(self):
        return Establishment.objects.filter(id_admin_id=self.request.user.id)
    