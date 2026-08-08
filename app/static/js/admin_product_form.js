(function () {
  const categoryMeta = window.PRODUCT_CATEGORY_META || {};
  const categorySelect = document.getElementById('category_id');
  const genderSelect = document.getElementById('gender');
  const genderHint = document.getElementById('gender-hint');
  const previewList = document.getElementById('listing-preview-list');
  const visibilityInputs = document.querySelectorAll('[data-visibility-field]');

  function updateGenderHint() {
    if (!categorySelect || !genderHint) return;
    const meta = categoryMeta[categorySelect.value];
    if (!meta || !meta.suggested_gender) {
      genderHint.textContent = 'Pick Boys, Girls, or Kids so shop filters work correctly.';
      genderHint.className = 'form-text';
      return;
    }
    const labels = { boys: 'Boys', girls: 'Girls', kids: 'Kids (Unisex)' };
    genderHint.textContent = 'Suggested for this category: ' + (labels[meta.suggested_gender] || meta.suggested_gender);
    genderHint.className = 'form-text text-primary fw-medium';
    if (genderSelect && !genderSelect.value) {
      genderSelect.value = meta.suggested_gender;
    }
  }

  function updateListingPreview() {
    if (!previewList) return;
    const places = [];
    const active = document.querySelector('[data-visibility-field="is_active"]')?.checked;
    if (!active) {
      places.push('Draft — hidden from customers');
    } else {
      places.push('Shop & category pages');
      if (document.querySelector('[data-visibility-field="is_new_arrival"]')?.checked) {
        places.push('Homepage → New Arrivals');
      }
      if (document.querySelector('[data-visibility-field="is_featured"]')?.checked) {
        places.push('Homepage → Parent Favorites');
      }
      if (document.querySelector('[data-visibility-field="is_trending"]')?.checked) {
        places.push('Trending badge on cards');
      }
      const ages = document.querySelectorAll('input[name="age_groups"]:checked').length;
      if (ages) places.push('Shop by age (' + ages + ' band' + (ages > 1 ? 's' : '') + ')');
    }
    previewList.innerHTML = places.map(function (p) {
      return '<li><i class="bi bi-check2-circle text-primary me-1"></i>' + p + '</li>';
    }).join('');
  }

  categorySelect?.addEventListener('change', updateGenderHint);
  visibilityInputs.forEach(function (el) {
    el.addEventListener('change', updateListingPreview);
  });
  document.querySelectorAll('input[name="age_groups"]').forEach(function (el) {
    el.addEventListener('change', updateListingPreview);
  });

  document.querySelectorAll('[data-age-preset]').forEach(function (btn) {
    btn.addEventListener('click', function () {
      const ages = (btn.getAttribute('data-age-preset') || '').split(',');
      document.querySelectorAll('input[name="age_groups"]').forEach(function (cb) {
        cb.checked = ages.indexOf(cb.value) !== -1;
      });
      updateListingPreview();
    });
  });

  document.querySelectorAll('[data-age-clear]').forEach(function (btn) {
    btn.addEventListener('click', function () {
      document.querySelectorAll('input[name="age_groups"]').forEach(function (cb) {
        cb.checked = false;
      });
      updateListingPreview();
    });
  });

  const rows = document.getElementById('variant-rows');
  const addBtn = document.getElementById('add-variant-row');
  const tpl = document.getElementById('variant-row-template');
  addBtn?.addEventListener('click', function () {
    rows.appendChild(tpl.content.cloneNode(true));
  });
  rows?.addEventListener('click', function (e) {
    const btn = e.target.closest('.remove-variant-row');
    if (!btn) return;
    const row = btn.closest('.variant-row');
    if (rows.querySelectorAll('.variant-row').length > 1) row.remove();
  });

  const imageInput = document.getElementById('product-images-input');
  const preview = document.getElementById('image-preview');
  let previewUrls = [];
  function clearPreviewUrls() {
    previewUrls.forEach(function (url) { URL.revokeObjectURL(url); });
    previewUrls = [];
  }
  imageInput?.addEventListener('change', function () {
    clearPreviewUrls();
    preview.innerHTML = '';
    Array.from(this.files || []).forEach(function (file, index) {
      if (!file.type.startsWith('image/')) return;
      const card = document.createElement('div');
      card.className = 'product-image-preview-item' + (index === 0 ? ' is-primary' : '');
      const img = document.createElement('img');
      const url = URL.createObjectURL(file);
      previewUrls.push(url);
      img.src = url;
      img.alt = file.name;
      const caption = document.createElement('div');
      caption.className = 'product-image-preview-caption';
      if (index === 0) {
        const badge = document.createElement('span');
        badge.className = 'badge bg-primary me-1';
        badge.textContent = 'Main';
        caption.appendChild(badge);
      }
      caption.appendChild(document.createTextNode(file.name));
      card.appendChild(img);
      card.appendChild(caption);
      preview.appendChild(card);
    });
  });

  updateGenderHint();
  updateListingPreview();
})();
