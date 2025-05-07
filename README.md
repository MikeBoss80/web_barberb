# web_barberb

✅ Clases → PascalCase
    Se usan para modelos, vistas, formularios, etc.
    Empiezan con mayúscula y cada palabra en mayúscula.

    Ejmplo:
    Class UserProfile

✅ Variables → snake_case
    Se usan para guardar datos temporales o constantes dentro de funciones, métodos, etc.
    Todas en minúsculas, separadas por guión bajo.

    Ejemplo:
    user_name = "Juan"
    total_price = 50.5

✅ Funciones / Métodos → snake_case
    Funciones normales o dentro de clases.
    Empiezan en minúscula, con guión bajo si hay más palabras.
    
    Ejemplo:
    def calculate_total(price, quantity):
    return price * quantity

✅ Constantes → UPPER_CASE
    Valores que no cambiarán.
    Todo en mayúsculas, con guión bajo.
    
    Ejemplo:
    MAX_USERS = 100
    DEFAULT_LANGUAGE = 'es'

✅ Objetos → snake_case (como variables normales)
    Cuando creas una instancia de una clase.
    
    Ejemplo:
    user = UserProfile(name="Carlos")
    

Tipo | Estilo | Ejemplo
Clase | PascalCase | UserProfile
Variable | snake_case | user_name
Función | snake_case | get_user_email()
Constante | UPPER_CASE | MAX_RETRIES
Objeto | snake_case | my_user


ACTIVAR ENTORNO VIRTUAL
.venv\Scripts\activate

CORRER SERVICIO
Hacerlo con el entorno virtual activado!!!
python manage.py runserver



                AGREGAR A BARBEROS.HTML DIV BARBEROS CONTAINER /DIV ACCIONES LINEA 96
                ESTOS SE ACTIVARAN CUANDO CREEMOS LOS ARCHIVOS DE LAS RUTAS 
                <a href="{% url 'editar_barbero' barbero.id %}">Editar</a>
                <a href="{% url 'desactivar_barbero' barbero.id %}">Desactivar</a>