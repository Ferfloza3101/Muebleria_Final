// seleccionar direccion
document.addEventListener('DOMContentLoaded', () => {
  const btn = document.getElementById('continuarDireccion');
  if (!btn) return;
  btn.addEventListener('click', () => {
    const checked = document.querySelector('input[name="direccion"]:checked');
    if (!checked) {
      alert('Selecciona una dirección para continuar.');
      return;
    }
    const id = checked.value;
    window.location.href = `/productos/carrito/confirmar/?direccion_id=${id}`;
  });
});