document.addEventListener('DOMContentLoaded', function () {
    const btnReservar = document.getElementById('btnReservar');

    btnReservar.addEventListener('click', function () {
      const modalServicio = bootstrap.Modal.getInstance(document.getElementById('staticBackdrop'));
      modalServicio.hide(); // Cierra el modal actual

      // Espera un poco antes de abrir el otro para evitar superposición de animaciones
      setTimeout(() => {
        const modalConfirmacion = new bootstrap.Modal(document.getElementById('modalConfirmacion'));
        modalConfirmacion.show();
      }, 500); // 500ms = duración típica de fade
    });
});