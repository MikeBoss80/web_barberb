from django.urls import path
from admin_module.views import CitasView,InventarioListView,ProductCreateView,ProductoUpdateView,ProductDeleteView, BarberosView, ServiciosView, InventarioView, ReportesView, SeguridadView, SoporteView, ContenidosView, CalendarioBarberoView, LogoutView, PerfilUsuarioView, EditarPerfilView, CreateEstablishmentView, HomeadminView,DeleteEstablishmentView
from django.contrib.auth.views import LogoutView

"""//🔥 Nota: Usamos Class-Based View (HomePageView) lo cual es moderno."""
app_name = 'admin_module'

urlpatterns = [
    path('', HomeadminView.as_view(), name='admin_main'),
    path('citas/', CitasView.as_view(), name='citas'),
    path('barberos/', BarberosView.as_view(), name='barberos'),
    path('servicios/', ServiciosView.as_view(), name='servicios'),
    path('inventario/', InventarioView.as_view(), name='inventario'),
    path('reportes/', ReportesView.as_view(), name='reportes'),
    path('seguridad/', SeguridadView.as_view(), name='seguridad'),
    path('soporte/', SoporteView.as_view(), name='soporte'),
    path('contenidos/', ContenidosView.as_view(), name='contenidos'),
    path('barberos/<int:barbero_id>/calendario/', CalendarioBarberoView.as_view(), name='calendario_barbero'),
    path("perfil/", PerfilUsuarioView.as_view(), name="perfil_usuario"),
    path('perfil/editar/', EditarPerfilView.as_view(), name='editar_perfil'),
    path('producto/agregar/', ProductCreateView.as_view(), name='producto_create'),
    path('producto/editar/<int:pk>/', ProductoUpdateView.as_view(), name='producto_update'),
    path('producto/eliminar/<int:pk>/', ProductDeleteView.as_view(), name='product_delete'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    path('registro_est/', CreateEstablishmentView.as_view(), name='registro_est'),
    path('eliminar_est/<int:pk>/', DeleteEstablishmentView.as_view(), name='eliminar_est'),

]   
