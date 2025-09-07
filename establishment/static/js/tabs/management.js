// Función para inicializar componentes del módulo de gestión
function initializeManagementComponents() {
    $('#tablaEstablecimientos').DataTable({
        language: {
            url: 'https://cdn.datatables.net/plug-ins/2.3.2/i18n/es-ES.json'
        },
        dom: '<"d-flex justify-content-between mb-2"fB>rt<"d-flex justify-content-between mt-2"lip>',
        buttons: [
            'copy', 'csv', 'excel', 'pdf', 'print'
        ],
        pageLength: 10,
    });

    $('.btnActualizarEst').on('click', function () {
        const id = $(this).data('id');
        const nombre = $(this).data('nombre');
        const direccion = $(this).data('direccion');
        const ciudad = $(this).data('ciudad');
        const pais = $(this).data('pais');
        const telefono = $(this).data('telefono');
        const email = $(this).data('email');
        const descripcion = $(this).data('descripcion');
        const lat = $(this).data('lat');
        const lng = $(this).data('lng');

        // Llenar los campos del formulario
        $('#inputEstablecimientoId').val(id);
        $('#inputNombre').val(nombre);
        $('#inputDireccion').val(direccion);
        $('#inputCiudad').val(ciudad);
        $('#inputPais').val(pais);
        $('#inputTelefono').val(telefono);
        $('#inputCorreo').val(email);
        $('#inputDescripcion').val(descripcion);
        $('#inputLat').val(lat);
        $('#inputLng').val(lng);

        $('#formUpdateEstablishment').attr('action', `./management/update/${id}/`);
    });

    $('.btnDelEstablishment').on('click', function () {
        var btn = $(this);
        var id = btn.data('id');
        var estName = btn.data('name');
        $('#labelEstName').text(estName);
        $('#formEliminarEst').attr('action', `./management/delete/${id}/`);

        var modalEliminarEst = new bootstrap.Modal(document.getElementById('delEstablishment'));
        modalEliminarEst.show();
    });
}
