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
  const primaryNewIndexInput = document.getElementById('primary-new-upload-index');
  let previewUrls = [];

  function clearPreviewUrls() {
    previewUrls.forEach(function (url) { URL.revokeObjectURL(url); });
    previewUrls = [];
  }

  function markNewUploadPrimary(index) {
    if (primaryNewIndexInput) {
      primaryNewIndexInput.value = String(index);
    }
    preview?.querySelectorAll('.product-image-preview-item').forEach(function (card, i) {
      card.classList.toggle('is-primary', i === index);
      const caption = card.querySelector('.product-image-preview-caption');
      if (!caption) return;
      caption.innerHTML = '';
      if (i === index) {
        const badge = document.createElement('span');
        badge.className = 'badge bg-primary me-1';
        badge.textContent = 'Main';
        caption.appendChild(badge);
      }
      caption.appendChild(document.createTextNode('New upload ' + (i + 1)));
    });
  }

  imageInput?.addEventListener('change', function () {
    clearPreviewUrls();
    preview.innerHTML = '';
    const files = Array.from(this.files || []).filter(function (file) {
      return file.type.startsWith('image/');
    });

    files.forEach(function (file, index) {
      const card = document.createElement('div');
      card.className = 'product-image-preview-item is-selectable' + (index === 0 ? ' is-primary' : '');
      card.setAttribute('role', 'button');
      card.setAttribute('tabindex', '0');
      card.setAttribute('aria-label', 'Set new upload ' + (index + 1) + ' as main photo');
      card.dataset.uploadIndex = String(index);

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
      caption.appendChild(document.createTextNode('New upload ' + (index + 1)));

      card.appendChild(img);
      card.appendChild(caption);
      preview.appendChild(card);
    });

    if (files.length) {
      markNewUploadPrimary(0);
    } else if (primaryNewIndexInput) {
      primaryNewIndexInput.value = '';
    }
  });

  preview?.addEventListener('click', function (e) {
    const card = e.target.closest('.product-image-preview-item');
    if (!card || card.dataset.uploadIndex === undefined) return;
    markNewUploadPrimary(parseInt(card.dataset.uploadIndex, 10));
  });

  preview?.addEventListener('keydown', function (e) {
    if (e.key !== 'Enter' && e.key !== ' ') return;
    const card = e.target.closest('.product-image-preview-item');
    if (!card || card.dataset.uploadIndex === undefined) return;
    e.preventDefault();
    markNewUploadPrimary(parseInt(card.dataset.uploadIndex, 10));
  });

  /* Ensure CSRF token is present on multipart save (meta → hidden field). */
  const productForm = document.getElementById('product-form');
  const saveErrors = document.getElementById('product-form-save-errors');
  const isNewProduct = productForm?.dataset.isNew === 'true';

  function showSaveErrors(messages) {
    if (!saveErrors) return;
    if (!messages.length) {
      saveErrors.classList.add('d-none');
      saveErrors.innerHTML = '';
      return;
    }
    saveErrors.classList.remove('d-none');
    saveErrors.innerHTML =
      '<h6 class="alert-heading mb-2"><i class="bi bi-exclamation-triangle me-1"></i>Please fix the following before saving</h6>' +
      '<ul class="mb-0 ps-3">' +
      messages.map(function (msg) { return '<li>' + msg + '</li>'; }).join('') +
      '</ul>';
    saveErrors.scrollIntoView({ behavior: 'smooth', block: 'center' });
  }

  function fieldValue(name) {
    const el = productForm?.querySelector('[name="' + name + '"]');
    return el ? String(el.value || '').trim() : '';
  }

  function validateProductForm() {
    const errors = [];
    if (!fieldValue('name')) {
      errors.push('Product name is required.');
    }
    if (!fieldValue('category_id')) {
      errors.push('Category is required.');
    }
    const price = parseFloat(fieldValue('price'));
    if (!fieldValue('price') || Number.isNaN(price) || price <= 0) {
      errors.push('Selling price is required and must be greater than zero.');
    }
    const compareAt = fieldValue('compare_at_price');
    if (compareAt) {
      const compareVal = parseFloat(compareAt);
      if (!Number.isNaN(compareVal) && !Number.isNaN(price) && compareVal <= price) {
        errors.push('Compare-at price must be higher than selling price.');
      }
    }
    const agesChecked = productForm.querySelectorAll('input[name="age_groups"]:checked').length;
    if (!agesChecked) {
      errors.push('Select at least one suitable age band.');
    }
    const isLive = document.querySelector('[data-visibility-field="is_active"]')?.checked;
    if (isLive && !fieldValue('gender')) {
      errors.push('Gender is required for products that are live on the store.');
    }
    const variantRows = productForm.querySelectorAll('#variant-rows .variant-row');
    let completeVariants = 0;
    let partialVariants = 0;
    variantRows.forEach(function (row) {
      const size = (row.querySelector('[name="variant_size[]"]')?.value || '').trim();
      const color = (row.querySelector('[name="variant_color[]"]')?.value || '').trim();
      const sku = (row.querySelector('[name="variant_sku[]"]')?.value || '').trim();
      if (size && color && sku) {
        completeVariants += 1;
      } else if (size || color || sku) {
        partialVariants += 1;
      }
    });
    if (partialVariants) {
      errors.push('Each variant row needs Size, Color, and SKU — or leave the row blank.');
    }
    if (isNewProduct && !completeVariants) {
      errors.push('Add at least one complete variant (size, color, SKU).');
    }
    if (isNewProduct) {
      const imageInputEl = document.getElementById('product-images-input');
      const hasNewImages = imageInputEl && imageInputEl.files && imageInputEl.files.length > 0;
      if (!hasNewImages) {
        errors.push('Upload at least one product photo.');
      }
    }
    return errors;
  }

  productForm?.addEventListener('submit', function (e) {
    const validationErrors = validateProductForm();
    if (validationErrors.length) {
      e.preventDefault();
      showSaveErrors(validationErrors);
      return;
    }
    showSaveErrors([]);

    const meta = document.querySelector('meta[name="csrf-token"]');
    const token = meta ? meta.content : '';
    if (!token) return;
    let field = productForm.querySelector('input[name="csrf_token"]');
    if (!field) {
      field = document.createElement('input');
      field.type = 'hidden';
      field.name = 'csrf_token';
      productForm.prepend(field);
    }
    field.value = token;
  });

  const serverErrors = document.getElementById('product-form-server-errors');
  if (serverErrors) {
    serverErrors.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }

  updateGenderHint();
  updateListingPreview();
})();
