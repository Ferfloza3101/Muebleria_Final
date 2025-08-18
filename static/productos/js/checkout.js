// checkout
document.addEventListener('DOMContentLoaded', () => {
  const btnPagar = document.getElementById('btnPagarConfirmar');
  if (btnPagar) {
    btnPagar.addEventListener('click', () => {
      btnPagar.disabled = true;
      btnPagar.textContent = 'Procesando...';
      const match = window.location.search.match(/direccion_id=(\d+)/);
      if (!match) {
        alert('No se encontró la dirección de envío.');
        btnPagar.disabled = false;
        btnPagar.textContent = 'Pagar con MercadoPago';
        return;
      }
      fetch('/productos/carrito/pago-mercadopago/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': getCookie('csrftoken'),
        },
        body: JSON.stringify({ direccion_id: match[1] })
      })
        .then((r) => r.json())
        .then((data) => {
          if (data && data.url) {
            window.location.href = data.url;
          } else {
            alert((data && data.error) || 'Error al generar el pago.');
            btnPagar.disabled = false;
            btnPagar.textContent = 'Pagar con MercadoPago';
          }
        })
        .catch(() => {
          alert('Error de red al intentar procesar el pago.');
          btnPagar.disabled = false;
          btnPagar.textContent = 'Pagar con MercadoPago';
        });
    });
  }

  const formPagoPrueba = document.getElementById('formPagoPrueba');
  if (formPagoPrueba) {
    formPagoPrueba.addEventListener('submit', (e) => {
      e.preventDefault();
      const btn = formPagoPrueba.querySelector('button[type="submit"]');
      btn.disabled = true;
      btn.textContent = 'Procesando...';
      fetch(formPagoPrueba.action, {
        method: 'POST',
        headers: { 'X-CSRFToken': getCookie('csrftoken') },
        body: new FormData(formPagoPrueba)
      })
        .then((response) => {
          if (response.redirected) {
            window.location.href = response.url;
            return null;
          }
          return response.json();
        })
        .then((data) => {
          if (data && data.error) {
            alert(data.error);
            btn.disabled = false;
            btn.textContent = 'Pago de prueba';
          }
        })
        .catch(() => {
          alert('Error de red al intentar procesar el pago de prueba.');
          btn.disabled = false;
          btn.textContent = 'Pago de prueba';
        });
    });
  }
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