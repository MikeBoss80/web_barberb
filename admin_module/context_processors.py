from barber_module.models import BarberRequest
from login_module.models import Profile

def solicitudes_pendientes(request):
    if request.user.is_authenticated and request.user.groups.filter(name='Administrador').exists():
        try:
            perfil = Profile.objects.get(user=request.user)
            establecimiento = perfil.establishment
            count = BarberRequest.objects.filter(establecimiento=establecimiento, estado='pendiente').count()
            return {'solicitudes_pendientes_count': count}
        except Profile.DoesNotExist:
            pass
    return {'solicitudes_pendientes_count': 0}
