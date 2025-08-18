// abrir modal de producto
document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('.product-card.open-modal-btn').forEach((card) => {
    card.addEventListener('click', (e) => {
      if (e.target.closest('button')) return;
      const productId = card.getAttribute('data-product-id');
      if (productId && typeof openProductModal === 'function') openProductModal(productId);
    });
  });
});