/* ============================================
   Indistylex — Main JavaScript
   ============================================ */

document.addEventListener('DOMContentLoaded', function () {

  /* --- Hero Carousel auto-slide fix --- */
  var heroEl = document.getElementById('heroCarousel');
  if (heroEl) {
    new bootstrap.Carousel(heroEl, {
      interval: 4500,
      ride: 'carousel',
      pause: 'hover',
      wrap: true
    });
  }

  /* --- Flash message auto-dismiss --- */
  document.querySelectorAll('.alert-dismissible').forEach(function (alert) {
    setTimeout(function () {
      var bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
      bsAlert.close();
    }, 5000);
  });

  /* --- Password toggle --- */
  document.querySelectorAll('.toggle-password').forEach(function (btn) {
    btn.addEventListener('click', function () {
      var group = this.closest('.input-group');
      var input = group ? group.querySelector('input') : null;
      if (!input) return;
      var icon = this.querySelector('i');
      if (input.type === 'password') {
        input.type = 'text';
        if (icon) { icon.classList.remove('bi-eye'); icon.classList.add('bi-eye-slash'); }
      } else {
        input.type = 'password';
        if (icon) { icon.classList.remove('bi-eye-slash'); icon.classList.add('bi-eye'); }
      }
    });
  });

  /* --- CSRF token helper --- */
  function getCsrf() {
    var el = document.querySelector('meta[name="csrf-token"]');
    return el ? el.content : '';
  }

  /* --- Cart: update quantity (AJAX) --- */
  document.querySelectorAll('.cart-qty-input').forEach(function (input) {
    input.addEventListener('change', function () {
      var itemId = this.dataset.itemId;
      var quantity = parseInt(this.value, 10);
      if (quantity < 1) { this.value = 1; quantity = 1; }

      fetch('/cart/update/' + encodeURIComponent(itemId), {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': getCsrf()
        },
        body: JSON.stringify({ quantity: quantity })
      })
      .then(function (res) { return res.json(); })
      .then(function (data) {
        if (data.success) {
          location.reload();
        } else {
          showToast(data.message || 'Could not update quantity', 'danger');
        }
      })
      .catch(function () {
        showToast('Something went wrong', 'danger');
      });
    });
  });

  /* --- Cart: remove item (AJAX) --- */
  document.querySelectorAll('.cart-remove-btn').forEach(function (btn) {
    btn.addEventListener('click', function (e) {
      e.preventDefault();
      if (!confirm('Remove this item from cart?')) return;

      var itemId = this.dataset.itemId;
      fetch('/cart/remove/' + encodeURIComponent(itemId), {
        method: 'POST',
        headers: { 'X-CSRFToken': getCsrf() }
      })
      .then(function (res) { return res.json(); })
      .then(function (data) {
        if (data.success) {
          location.reload();
        } else {
          showToast(data.message || 'Could not remove item', 'danger');
        }
      })
      .catch(function () {
        showToast('Something went wrong', 'danger');
      });
    });
  });

  /* --- Wishlist toggle --- */
  document.querySelectorAll('.wishlist-toggle').forEach(function (btn) {
    btn.addEventListener('click', function (e) {
      e.preventDefault();
      var productId = this.dataset.productId;

      fetch('/user/wishlist/toggle/' + encodeURIComponent(productId), {
        method: 'POST',
        headers: { 'X-CSRFToken': getCsrf() }
      })
      .then(function (res) { return res.json(); })
      .then(function (data) {
        if (data.status === 'added' || data.status === 'removed') {
          var icon = btn.querySelector('i');
          if (icon) {
            icon.classList.toggle('bi-heart');
            icon.classList.toggle('bi-heart-fill');
            icon.classList.toggle('text-danger');
          }
          // Remove card from wishlist page if removed
          if (data.status === 'removed') {
            var card = btn.closest('.col-md-4');
            if (card && document.querySelector('.wishlist-section')) {
              card.remove();
            }
          }
        }
      });
    });
  });

  /* --- Product detail: thumbnail click --- */
  document.querySelectorAll('.thumbnail-item').forEach(function (thumb) {
    thumb.addEventListener('click', function () {
      var mainImage = document.getElementById('mainImage');
      if (mainImage) {
        mainImage.src = this.querySelector('img').dataset.full || this.querySelector('img').src;
      }
      document.querySelectorAll('.thumbnail-item').forEach(function (t) { t.classList.remove('active'); });
      this.classList.add('active');
    });
  });

  /* --- Product detail: size & color selectors --- */
  document.querySelectorAll('.size-btn').forEach(function (btn) {
    btn.addEventListener('click', function () {
      document.querySelectorAll('.size-btn').forEach(function (b) { b.classList.remove('active'); });
      this.classList.add('active');
      var sizeInput = document.getElementById('selectedSize');
      if (sizeInput) sizeInput.value = this.dataset.size;
    });
  });
  document.querySelectorAll('.color-btn').forEach(function (btn) {
    btn.addEventListener('click', function () {
      document.querySelectorAll('.color-btn').forEach(function (b) { b.classList.remove('active'); });
      this.classList.add('active');
      var colorInput = document.getElementById('selectedColor');
      if (colorInput) colorInput.value = this.dataset.color;
    });
  });

  /* --- Quantity +/- buttons on product detail --- */
  document.querySelectorAll('.qty-btn').forEach(function (btn) {
    btn.addEventListener('click', function () {
      var input = document.getElementById('qtyInput');
      if (!input) return;
      var val = parseInt(input.value, 10) || 1;
      if (this.dataset.action === 'increase' && val < 10) {
        input.value = val + 1;
      } else if (this.dataset.action === 'decrease' && val > 1) {
        input.value = val - 1;
      }
    });
  });

  /* --- Newsletter form --- */
  var nlForm = document.getElementById('newsletter-form');
  if (nlForm) {
    nlForm.addEventListener('submit', function (e) {
      e.preventDefault();
      var email = nlForm.querySelector('input[type="email"]').value;
      if (!email) return;
      showToast('Thank you for subscribing!', 'success');
      nlForm.reset();
    });
  }

  /* --- Back to top --- */
  var backToTop = document.getElementById('backToTop');
  if (backToTop) {
    window.addEventListener('scroll', function () {
      if (window.scrollY > 400) {
        backToTop.classList.add('visible');
      } else {
        backToTop.classList.remove('visible');
      }
    }, { passive: true });
    backToTop.addEventListener('click', function () {
      window.scrollTo({ top: 0, behavior: 'smooth' });
    });
  }

  /* --- Close mobile nav on link click --- */
  var navCollapse = document.getElementById('mainNav');
  if (navCollapse) {
    navCollapse.querySelectorAll('.nav-link:not(.dropdown-toggle)').forEach(function (link) {
      link.addEventListener('click', function () {
        var bsCollapse = bootstrap.Collapse.getInstance(navCollapse);
        if (bsCollapse) bsCollapse.hide();
      });
    });
  }

});

/* --- Toast notification helper --- */
function showToast(message, type) {
  type = type || 'info';
  var container = document.getElementById('toast-container');
  if (!container) {
    container = document.createElement('div');
    container.id = 'toast-container';
    container.className = 'position-fixed bottom-0 end-0 p-3';
    container.style.zIndex = '1090';
    document.body.appendChild(container);
  }

  var toast = document.createElement('div');
  toast.className = 'toast align-items-center text-bg-' + type + ' border-0';
  toast.setAttribute('role', 'alert');
  toast.innerHTML =
    '<div class="d-flex">' +
      '<div class="toast-body">' + escapeHtml(message) + '</div>' +
      '<button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>' +
    '</div>';

  container.appendChild(toast);
  var bsToast = new bootstrap.Toast(toast, { autohide: true, delay: 4000 });
  bsToast.show();
  toast.addEventListener('hidden.bs.toast', function () { toast.remove(); });
}

/* --- HTML escape helper --- */
function escapeHtml(str) {
  var div = document.createElement('div');
  div.appendChild(document.createTextNode(str));
  return div.innerHTML;
}
