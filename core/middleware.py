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


class NoCacheMiddleware:
    """
    Middleware para prevenir el caché de páginas en el navegador.
    Esto previene que al usar el botón 'Atrás' se muestren páginas 
    que requieren autenticación después de hacer logout.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        # Solo aplicar a páginas que requieren autenticación
        # Excluir archivos estáticos y páginas públicas
        if not request.path.startswith('/static/') and not request.path.startswith('/media/'):
            # Prevenir caché del navegador
            response['Cache-Control'] = 'no-cache, no-store, must-revalidate, private'
            response['Pragma'] = 'no-cache'
            response['Expires'] = '0'
        
        return response


class SecurityHeadersMiddleware:
    """
    Middleware para agregar headers de seguridad adicionales.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        # Prevenir que la página se cargue en un iframe (excepto SAMEORIGIN)
        if 'X-Frame-Options' not in response:
            response['X-Frame-Options'] = 'SAMEORIGIN'
        
        # Prevenir MIME type sniffing
        response['X-Content-Type-Options'] = 'nosniff'
        
        # Habilitar protección XSS en navegadores antiguos
        response['X-XSS-Protection'] = '1; mode=block'
        
        return response
