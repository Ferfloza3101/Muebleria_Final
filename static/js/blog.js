// manejo de likes
document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('.like-form').forEach((form) => {
    form.addEventListener('submit', (e) => {
      e.preventDefault();
      const btn = form.querySelector('.like-btn');
      const icon = btn.querySelector('i');
      const countSpan = form.parentElement.querySelector('.like-count');
      const url = form.action;
      const csrf = form.querySelector('[name=csrfmiddlewaretoken]').value;

      fetch(url, {
        method: 'POST',
        headers: {
          'X-CSRFToken': csrf,
          'X-Requested-With': 'XMLHttpRequest',
        },
      })
        .then((res) => (res.ok ? res.json() : Promise.reject()))
        .then((data) => {
          if (!data || !data.success) return;
          if (data.liked) {
            icon.classList.remove('far');
            icon.classList.add('fas');
          } else {
            icon.classList.remove('fas');
            icon.classList.add('far');
          }
          if (countSpan) countSpan.textContent = data.likes;

          const detailIcon = document.querySelector('.blog-detalle-likes .like-btn i');
          const detailCount = document.querySelector('.blog-detalle-likes .like-count');
          if (detailIcon) {
            if (data.liked) {
              detailIcon.classList.remove('far');
              detailIcon.classList.add('fas');
            } else {
              detailIcon.classList.remove('fas');
              detailIcon.classList.add('far');
            }
          }
          if (detailCount) detailCount.textContent = data.likes;
        })
        .catch(() => {});
    });
  });
});