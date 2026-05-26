/* ============================================
   Silkensway — Admin Panel JS v5
   ============================================ */

document.addEventListener('DOMContentLoaded', function () {

  /* --- Sidebar toggle (mobile/tablet) --- */
  var toggleBtn = document.getElementById('sidebarToggle');
  var sidebar   = document.getElementById('adminSidebar');
  var overlay   = document.getElementById('sidebarOverlay');

  function closeSidebar() {
    if (sidebar) sidebar.classList.remove('show');
    if (overlay) overlay.classList.remove('active');
  }

  if (toggleBtn && sidebar) {
    toggleBtn.addEventListener('click', function () {
      sidebar.classList.toggle('show');
      if (overlay) overlay.classList.toggle('active');
    });
  }
  if (overlay) {
    overlay.addEventListener('click', closeSidebar);
  }

  /* Close sidebar on window resize to desktop */
  window.addEventListener('resize', function () {
    if (window.innerWidth >= 992) closeSidebar();
  });

  /* --- Confirm delete --- */
  document.querySelectorAll('.confirm-delete').forEach(function (form) {
    form.addEventListener('submit', function (e) {
      if (!confirm('Are you sure you want to delete this item? This cannot be undone.')) {
        e.preventDefault();
      }
    });
  });

  /* --- Image preview on file select --- */
  var imageInput = document.getElementById('product_images');
  var previewContainer = document.getElementById('imagePreview');
  if (imageInput && previewContainer) {
    imageInput.addEventListener('change', function () {
      previewContainer.innerHTML = '';
      Array.from(this.files).forEach(function (file) {
        if (!file.type.startsWith('image/')) return;
        var reader = new FileReader();
        reader.onload = function (e) {
          var img = document.createElement('img');
          img.src = e.target.result;
          img.className = 'rounded me-2 mb-2';
          img.style.width = '80px';
          img.style.height = '80px';
          img.style.objectFit = 'cover';
          previewContainer.appendChild(img);
        };
        reader.readAsDataURL(file);
      });
    });
  }

  /* --- CSRF helper --- */
  function getCsrf() {
    var el = document.querySelector('meta[name="csrf-token"]');
    return el ? el.content : '';
  }

  /* --- Order status update --- */
  document.querySelectorAll('.order-status-select').forEach(function (select) {
    select.addEventListener('change', function () {
      var orderId = this.dataset.orderId;
      var status  = this.value;

      fetch('/admin/orders/' + encodeURIComponent(orderId) + '/status', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': getCsrf()
        },
        body: JSON.stringify({ status: status })
      })
      .then(function (res) { return res.json(); })
      .then(function (data) {
        if (data.success) {
          if (typeof showToast === 'function') showToast('Order status updated', 'success');
        } else {
          if (typeof showToast === 'function') showToast(data.message || 'Update failed', 'danger');
        }
      })
      .catch(function () {
        if (typeof showToast === 'function') showToast('Something went wrong', 'danger');
      });
    });
  });

  /* --- Category toggle active/inactive --- */
  document.querySelectorAll('.category-toggle').forEach(function (toggle) {
    toggle.addEventListener('change', function () {
      var categoryId = this.dataset.categoryId;
      var isActive   = this.checked;

      fetch('/admin/categories/' + encodeURIComponent(categoryId) + '/toggle', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': getCsrf()
        },
        body: JSON.stringify({ is_active: isActive })
      })
      .then(function (res) { return res.json(); })
      .then(function (data) {
        if (data.success) {
          if (typeof showToast === 'function') showToast('Category updated', 'success');
        }
      });
    });
  });

  /* --- Select all checkbox --- */
  var selectAll = document.getElementById('selectAll');
  if (selectAll) {
    selectAll.addEventListener('change', function () {
      var checked = this.checked;
      document.querySelectorAll('.item-checkbox').forEach(function (cb) {
        cb.checked = checked;
      });
    });
  }

});
