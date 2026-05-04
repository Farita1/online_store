/**
 * admin_actions.js - Funciones globales para el panel administrativo
 */

// 1. Confirmar eliminación con SweetAlert2
function confirmDelete(deleteUrl, productName) {
    Swal.fire({
        title: '¿Estás seguro?',
        text: `Vas a eliminar "${productName}". Esta acción no se puede deshacer.`,
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#ff4b2b',
        cancelButtonColor: '#6c757d',
        confirmButtonText: 'Sí, eliminar',
        cancelButtonText: 'Cancelar',
        background: '#1a1a1a',
        color: '#ffffff'
    }).then((result) => {
        if (result.isConfirmed) {
            window.location.href = deleteUrl;
        }
    });
}

// 2. Mostrar imagen en Modal (Global)
function showFullImage(src, name) {
    const modalElement = document.getElementById('imageModal');
    if (modalElement) {
        const modal = new bootstrap.Modal(modalElement);
        document.getElementById('modalImg').src = src;
        document.getElementById('modalTitle').innerText = name;
        modal.show();
    }
}