from datetime import date
from admin_module.models import Inventory, Establishment
from barber_module.models import BarberRequest
from login_module.models import Profile
from services_module.models import ServiceDate 
from django.db.models import DateField
from django.db.models.functions import Cast

def get_daily_info(data):
    today = date.today()
    profile_user=Profile.objects.get(user=data.user)
    establishment_user = Establishment.objects.get(id_admin=profile_user.id)
    info_daily = []

    info_daily.append({
        'title': 'Citas',
        'value': ServiceDate.objects.annotate(date_only=Cast('date', DateField())).filter(
            date_only=today,
            service__establishment=establishment_user
        ).count(),
        'subtitle': 'Citas programadas para hoy',
        'icon': '<i class="bi bi-calendar-check"></i>',
        'btn_url': ''
    })

    info_daily.append({
        'title': 'Barberos activos',
        'value': Profile.objects.filter(
            establishment=establishment_user,
            user__is_active=True,
            user__groups__name="Barbero"  
        ).count(),
        'subtitle': 'Barberos disponibles en el establecimiento',
        'icon': '<i class="bi bi-person-fill-check"></i>',
        'btn_url': 'admin_module:collabs'
    })

    info_daily.append({
        'title': 'Productos Bajo Stock',
        'value': Inventory.objects.filter(
            establishment=establishment_user,
            product=5
        ).count(),
        'subtitle': 'Productos que necesitan reposición',
        'icon': '<i class="bi bi-box-seam"></i>',
        'btn_url': ''
    })

    # info_daily.append({
    #     'title': 'Ingresos',
    #     'value': f"${ServiceDate.objects.filter(
    #         date=today,
    #         service__establishment=establishment_user
    #     ).aggregate(total=Sum('price_total'))['total'] or 0:,.2f}",
    #     'subtitle': 'Total de ingresos generados hoy',
    #     'icon': '<i class="bi bi-cash-stack"></i>',
    #     'btn_url': ''
    # })

    #TODO: Cambiar por cantidad de actividades por barbero 
    # Próximas citas (de hoy en adelante)
    proximas_citas = ServiceDate.objects.filter(
        date__gte=today,
        service__establishment=establishment_user
    ).order_by('date', 'date')[:5]

    #TODO: Revisar si se deja
    # Notificaciones del sistema (ejemplo: solicitudes pendientes)
    solicitudes_pendientes = BarberRequest.objects.filter(
        establecimiento=establishment_user,
        estado='pendiente'
    ).count()

    notificaciones = []
    if solicitudes_pendientes:
        notificaciones.append(f"Tienes {solicitudes_pendientes} solicitudes de barberos pendientes por revisar.")

    return {
        'cards_metrics_data': info_daily,
        'today': today
    }

#TODO: Crear las funciones para obtener la información por separado