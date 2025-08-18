// reenviar resumen desde mis pedidos
document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('.js-reenviar-resumen').forEach((btn) => {
    btn.addEventListener('click', () => {
      const pedidoId = btn.getAttribute('data-pedido-id');
      const url = btn.getAttribute('data-url');
      if (!pedidoId || !url) return;
      if (!confirm('¿Desea reenviar el resumen por email?')) return;

      fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': getCookie('csrftoken'),
        },
        body: JSON.stringify({ pedido_id: Number(pedidoId) }),
      })
        .then((r) => r.json())
        .then((data) => {
          if (data && data.success) {
            alert('Resumen enviado exitosamente por email.');
          } else {
            alert((data && data.error) || 'Error al enviar el email.');
          }
        })
        .catch(() => alert('Error de conexión.'));
    });
  });
});

function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}