// Validación en vivo para cambio de contraseña

document.addEventListener('DOMContentLoaded', function() {
    const nueva = document.getElementById('nueva');
    const confirmar = document.getElementById('confirmar');
    const feedbackNueva = document.getElementById('nuevaFeedback');
    const feedbackConfirmar = document.getElementById('confirmarFeedback');
    const form = document.getElementById('cambiarContrasenaForm');

    function validarPassword(pw) {
        const errores = [];
        if (pw.length < 8) errores.push('Mínimo 8 caracteres');
        if (!/[A-Z]/.test(pw)) errores.push('Al menos una mayúscula');
        if (!/[^A-Za-z0-9]/.test(pw)) errores.push('Al menos un carácter especial');
        return errores;
    }

    function mostrarFeedbackNueva() {
        const val = nueva.value;
        const errores = validarPassword(val);
        if (!val) {
            feedbackNueva.textContent = '';
            feedbackNueva.classList.remove('ok');
        } else if (errores.length === 0) {
            feedbackNueva.textContent = 'Contraseña segura ✓';
            feedbackNueva.classList.add('ok');
        } else {
            feedbackNueva.textContent = errores.join(', ');
            feedbackNueva.classList.remove('ok');
        }
    }

    function mostrarFeedbackConfirmar() {
        if (!confirmar.value) {
            feedbackConfirmar.textContent = '';
            feedbackConfirmar.classList.remove('ok');
        } else if (nueva.value === confirmar.value) {
            feedbackConfirmar.textContent = 'Las contraseñas coinciden ✓';
            feedbackConfirmar.classList.add('ok');
        } else {
            feedbackConfirmar.textContent = 'Las contraseñas no coinciden';
            feedbackConfirmar.classList.remove('ok');
        }
    }

    if (nueva) {
        nueva.addEventListener('input', mostrarFeedbackNueva);
        nueva.addEventListener('input', mostrarFeedbackConfirmar);
    }
    if (confirmar) {
        confirmar.addEventListener('input', mostrarFeedbackConfirmar);
    }

    // Validación final antes de enviar
    if (form) {
        form.addEventListener('submit', function(e) {
            mostrarFeedbackNueva();
            mostrarFeedbackConfirmar();
            if (feedbackNueva.textContent && !feedbackNueva.classList.contains('ok')) {
                nueva.focus();
                e.preventDefault();
            } else if (feedbackConfirmar.textContent && !feedbackConfirmar.classList.contains('ok')) {
                confirmar.focus();
                e.preventDefault();
            }
        });
    }
}); 