/**
 * Zora E-commerce - Custom Number Input Logic
 * Maneja los incrementos de 10,000 y 10 evitando validaciones nativas molestas.
 */

// Lógica de clics para el overlay invisible
function handleSpinClick(event, inputId, step) {
    const input = document.getElementById(inputId);
    if (!input) return;

    const rect = event.target.getBoundingClientRect();
    const relativeY = event.clientY - rect.top;
    const currentVal = Math.round(parseFloat(input.value)) || 0;

    if (relativeY < rect.height / 2) {
        input.value = currentVal + step;
    } else {
        input.value = Math.max(0, currentVal - step);
    }
    
    // Disparar evento para que otros scripts detecten el cambio
    input.dispatchEvent(new Event('change'));
}

// Lógica para flechas del teclado
function setupZoraKeys(id, step) {
    const input = document.getElementById(id);
    if (!input) return;

    input.addEventListener('keydown', (e) => {
        if (e.key === 'ArrowUp') {
            e.preventDefault();
            input.value = (Math.round(parseFloat(input.value)) || 0) + step;
        } else if (e.key === 'ArrowDown') {
            e.preventDefault();
            input.value = Math.max(0, (Math.round(parseFloat(input.value)) || 0) - step);
        }
    });
}

// Previsualización de imagen universal
function setupImagePreview(inputId, imgId) {
    const fileInput = document.getElementById(inputId);
    const preview = document.getElementById(imgId);
    
    if (fileInput && preview) {
        fileInput.onchange = () => {
            const [file] = fileInput.files;
            if (file) preview.src = URL.createObjectURL(file);
        };
    }
}