from django.shortcuts import redirect
from django.urls import reverse

class CurrentRolMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self,request):
        

        if request.user.is_authenticated:
            current_role = request.session.get('current_role')
            groups = list(request.user.groups.values_list('name', flat=True))

            especial_roles = ['Administrador','Barbero']
            user_rols = [g for g in groups if g in especial_roles]

            #Clientes
            if not user_rols:
                # Es Cliente (no tiene roles especiales)
                request.session['current_role'] = 'Cliente'
                return self.get_response(request)
            
            # Si no hay rol actual, decidir qué hacer
            if not current_role:
                if len(user_rols) == 1:
                    # Solo tiene un rol especial: asignarlo directamente
                    request.session['current_role'] = user_rols[0]
                elif len(user_rols) > 1 and request.path != reverse('login_module:rol_actual'):
                    # Tiene más de un rol especial: redirigir a elegir
                    return redirect('login_module:rol_actual')

        return self.get_response(request)
