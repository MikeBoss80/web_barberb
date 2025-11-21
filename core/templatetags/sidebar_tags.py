from django import template

register = template.Library()

@register.simple_tag(takes_context=True)
def modules_sidebar(context):
    request = context['request']
    user = request.user
    current_role = request.session.get('current_role')


    if not user.is_authenticated:
        return []

    if user.is_superuser:
        return [
            # ('admin_dashboard', 'Administrador'),
            # ('usuarios', 'Gestión de usuarios'),
        ]
    if current_role == 'Administrador':
        return [
            ('admin_module:main', 'person-circle' , 'Dashboard'),
            ('admin_module:citas','calendar2-date-fill','Citas'),
            ('admin_module:collabs','people-fill','Colaboradores'),
            ('product:product_list','receipt-cutoff','Inventario'),
            ('admin_module:admin_solicitudes_list','device-ssd-fill','Solicitudes'),
            ('establishment:establishment_main','shop','Establecimiento'),
            ('admin_module:soporte','info-circle','Soporte'),
        ]
    if current_role == 'Barbero':
        return [
            ('admin_module:main', 'person-circle' , 'Dashboard'),
            ('admin_module:citas','calendar2-date-fill','Citas'),
            ('admin_module:barber_solicitudes_list','device-ssd-fill','Solicitudes'),
            ('admin_module:soporte','info-circle','Soporte'),
        ]
    return [
        ('services_module:services_main', 'globe-americas' , 'Reservar'),
        ('admin_module:citas','calendar2-date-fill','Citas'),
        ('admin_module:soporte','info-circle','Soporte'),


    ]
