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
  const uploadDropzone = document.getElementById('product-upload-dropzone');
  const uploadAddBtn = document.getElementById('product-upload-add-btn');
  const uploadCount = document.getElementById('product-upload-count');
  const preview = document.getElementById('image-preview');
  const primaryNewIndexInput = document.getElementById('primary-new-upload-index');
  let previewUrls = [];
  let pendingUploadFiles = [];
  let primaryUploadIndex = 0;

  function fileKey(file) {
    return [file.name, file.size, file.lastModified].join('|');
  }

  function syncInputFromPending() {
    if (!imageInput) return;
    try {
      const dt = new DataTransfer();
      pendingUploadFiles.forEach(function (file) {
        dt.items.add(file);
      });
      imageInput.files = dt.files;
    } catch (err) {
      /* DataTransfer unsupported in very old browsers */
    }
    updateUploadCount();
  }

  function updateUploadCount() {
    if (!uploadCount) return;
    const count = pendingUploadFiles.length;
    uploadCount.textContent = count
      ? count + ' photo' + (count === 1 ? '' : 's') + ' ready to upload'
      : 'No photos selected yet';
  }

  function clearPreviewUrls() {
    previewUrls.forEach(function (url) { URL.revokeObjectURL(url); });
    previewUrls = [];
  }

  function renderUploadPreview() {
    if (!preview) return;
    clearPreviewUrls();
    preview.innerHTML = '';

    pendingUploadFiles.forEach(function (file, index) {
      const card = document.createElement('div');
      card.className = 'product-image-preview-item is-selectable' + (index === primaryUploadIndex ? ' is-primary' : '');
      card.setAttribute('role', 'button');
      card.setAttribute('tabindex', '0');
      card.setAttribute('aria-label', 'Set photo ' + (index + 1) + ' as main image');
      card.dataset.uploadIndex = String(index);

      const removeBtn = document.createElement('button');
      removeBtn.type = 'button';
      removeBtn.className = 'product-image-preview-remove';
      removeBtn.setAttribute('aria-label', 'Remove photo ' + (index + 1));
      removeBtn.innerHTML = '&times;';
      removeBtn.addEventListener('click', function (e) {
        e.stopPropagation();
        removePendingFile(index);
      });

      const img = document.createElement('img');
      const url = URL.createObjectURL(file);
      previewUrls.push(url);
      img.src = url;
      img.alt = file.name;

      const caption = document.createElement('div');
      caption.className = 'product-image-preview-caption';
      if (index === primaryUploadIndex) {
        const badge = document.createElement('span');
        badge.className = 'badge bg-primary me-1';
        badge.textContent = 'Main';
        caption.appendChild(badge);
      }
      caption.appendChild(document.createTextNode(file.name));

      card.appendChild(removeBtn);
      card.appendChild(img);
      card.appendChild(caption);
      preview.appendChild(card);
    });

    if (primaryNewIndexInput) {
      primaryNewIndexInput.value = pendingUploadFiles.length ? String(primaryUploadIndex) : '';
    }
  }

  function addPendingFiles(fileList) {
    const seen = new Set(pendingUploadFiles.map(fileKey));
    Array.from(fileList || []).forEach(function (file) {
      if (!file || !file.type || !file.type.startsWith('image/')) return;
      const key = fileKey(file);
      if (seen.has(key)) return;
      seen.add(key);
      pendingUploadFiles.push(file);
    });
    if (primaryUploadIndex >= pendingUploadFiles.length) {
      primaryUploadIndex = Math.max(0, pendingUploadFiles.length - 1);
    }
    syncInputFromPending();
    renderUploadPreview();
  }

  function removePendingFile(index) {
    pendingUploadFiles.splice(index, 1);
    if (primaryUploadIndex >= pendingUploadFiles.length) {
      primaryUploadIndex = Math.max(0, pendingUploadFiles.length - 1);
    }
    syncInputFromPending();
    renderUploadPreview();
  }

  function markNewUploadPrimary(index) {
    if (!pendingUploadFiles.length) return;
    primaryUploadIndex = Math.max(0, Math.min(index, pendingUploadFiles.length - 1));
    if (primaryNewIndexInput) {
      primaryNewIndexInput.value = String(primaryUploadIndex);
    }
    renderUploadPreview();
  }

  function openFilePicker() {
    if (!imageInput) return;
    imageInput.click();
  }

  imageInput?.addEventListener('change', function () {
    const picked = Array.from(this.files || []);
    if (!picked.length) return;
    addPendingFiles(picked);
  });

  uploadAddBtn?.addEventListener('click', function (e) {
    e.preventDefault();
    e.stopPropagation();
    openFilePicker();
  });

  uploadDropzone?.addEventListener('click', function (e) {
    if (e.target.closest('#product-upload-add-btn')) return;
    if (e.target.closest('.product-image-preview-remove')) return;
    openFilePicker();
  });

  uploadDropzone?.addEventListener('dragover', function (e) {
    e.preventDefault();
    uploadDropzone.classList.add('is-dragover');
  });
  uploadDropzone?.addEventListener('dragleave', function () {
    uploadDropzone.classList.remove('is-dragover');
  });
  uploadDropzone?.addEventListener('drop', function (e) {
    e.preventDefault();
    uploadDropzone.classList.remove('is-dragover');
    if (e.dataTransfer && e.dataTransfer.files) {
      addPendingFiles(e.dataTransfer.files);
    }
  });

  preview?.addEventListener('click', function (e) {
    if (e.target.closest('.product-image-preview-remove')) return;
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
    if (isNewProduct && !pendingUploadFiles.length) {
      errors.push('Upload at least one product photo.');
    }
    return errors;
  }

  productForm?.addEventListener('submit', function (e) {
    syncInputFromPending();
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

  /* --- AI product photo autofill --- */
  const aiInput = document.getElementById('ai-product-scan-input');
  const aiBtn = document.getElementById('ai-product-scan-btn');
  const aiStatus = document.getElementById('ai-product-scan-status');
  const aiPreview = document.getElementById('ai-product-scan-preview');
  const analyzeUrl = productForm?.dataset.analyzeUrl;
  let aiScanFile = null;

  function setAiStatus(message, type) {
    if (!aiStatus) return;
    aiStatus.textContent = message || '';
    aiStatus.className = 'small mt-2' + (type ? ' text-' + type : ' text-muted');
  }

  let lastAiProductType = 'other';

  function setFieldValue(id, value) {
    if (value === null || value === undefined || value === '') return;
    const el = document.getElementById(id);
    if (el) el.value = value;
  }

  function fillVariantRows(rows) {
    const tbody = document.getElementById('variant-rows');
    const template = document.getElementById('variant-row-template');
    if (!tbody || !template || !Array.isArray(rows) || !rows.length) return;

    tbody.innerHTML = '';
    rows.forEach(function (row, index) {
      const tr = template.content.cloneNode(true);
      const sizeInput = tr.querySelector('[name="variant_size[]"]');
      const colorInput = tr.querySelector('[name="variant_color[]"]');
      const skuInput = tr.querySelector('[name="variant_sku[]"]');
      const stockInput = tr.querySelector('[name="variant_stock[]"]');
      if (sizeInput) sizeInput.value = row.size || '';
      if (colorInput) colorInput.value = row.color || '';
      if (skuInput) skuInput.value = row.sku || '';
      if (stockInput) stockInput.value = row.stock != null ? row.stock : 10;
      const removeBtn = tr.querySelector('.remove-variant-row');
      if (removeBtn && index === 0) removeBtn.remove();
      tbody.appendChild(tr);
    });
  }

  function applyAutofill(data) {
    setFieldValue('name', data.name);
    if (data.category_id) {
      const cat = document.getElementById('category_id');
      if (cat) cat.value = String(data.category_id);
    }
    setFieldValue('short_description', data.short_description);
    setFieldValue('description', data.description);
    setFieldValue('brand', data.brand || 'Indistylex');
    setFieldValue('material', data.material);
    setFieldValue('hsn_code', data.hsn_code);
    if (data.gender && genderSelect) genderSelect.value = data.gender;
    if (data.product_type) lastAiProductType = data.product_type;

    if (Array.isArray(data.age_groups)) {
      document.querySelectorAll('input[name="age_groups"]').forEach(function (cb) {
        cb.checked = data.age_groups.indexOf(cb.value) !== -1;
      });
    }

    if (Array.isArray(data.variant_draft_rows) && data.variant_draft_rows.length) {
      fillVariantRows(data.variant_draft_rows);
    } else {
      const colorInput = document.querySelector('#variant-rows input[name="variant_color[]"]');
      if (colorInput && data.variant_color) colorInput.value = data.variant_color;
    }

    updateGenderHint();
    updateListingPreview();

    document.querySelector('.product-form-section')?.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }

  function attachImageToProductForm(file) {
    if (!file) return;
    addPendingFiles([file]);
  }

  function showAiPreview(file) {
    if (!aiPreview || !file) return;
    aiPreview.classList.remove('d-none');
    aiPreview.innerHTML = '';
    const img = document.createElement('img');
    img.src = URL.createObjectURL(file);
    img.alt = 'Product photo for AI analysis';
    img.onload = function () { URL.revokeObjectURL(img.src); };
    aiPreview.appendChild(img);
  }

  aiInput?.addEventListener('change', function () {
    aiScanFile = aiInput.files && aiInput.files[0] ? aiInput.files[0] : null;
    if (aiScanFile) {
      showAiPreview(aiScanFile);
      setAiStatus('Photo ready — analyzing…', 'primary');
      if (aiBtn && !aiBtn.disabled) aiBtn.click();
    } else {
      aiPreview?.classList.add('d-none');
      setAiStatus('');
    }
  });

  function parseAnalyzeResponse(res) {
    return res.text().then(function (text) {
      var payload;
      try {
        payload = text ? JSON.parse(text) : {};
      } catch (parseErr) {
        if (res.status === 401 || res.status === 403) {
          throw new Error('Session expired. Refresh the page and log in again.');
        }
        if (res.status === 404) {
          throw new Error('Analyze endpoint not found — deploy latest code on the server (git pull + restart).');
        }
        if (res.status === 413) {
          throw new Error('Photo is too large. Use an image under 5 MB.');
        }
        if (res.status === 429) {
          throw new Error('Too many requests. Wait a minute and try again.');
        }
        if (/csrf|session expired/i.test(text || '')) {
          throw new Error('Session expired. Refresh the page and try again.');
        }
        throw new Error('Server returned an unexpected response. Refresh the page and try again.');
      }
      if (!res.ok || payload.success === false) {
        throw new Error(payload.message || payload.error || 'Could not analyze photo.');
      }
      return payload.data;
    });
  }

  aiBtn?.addEventListener('click', function () {
    if (!analyzeUrl) return;
    if (!aiScanFile) {
      setAiStatus('Choose a product photo first.', 'danger');
      aiInput?.focus();
      return;
    }

    aiBtn.disabled = true;
    setAiStatus('Analyzing photo… this may take a few seconds.', 'primary');

    const body = new FormData();
    body.append('image', aiScanFile);
    const csrf = document.querySelector('meta[name="csrf-token"]')?.content || '';
    if (csrf) {
      body.append('csrf_token', csrf);
    }

    fetch(analyzeUrl, {
      method: 'POST',
      headers: {
        'X-CSRFToken': csrf,
        'Accept': 'application/json',
        'X-Requested-With': 'XMLHttpRequest',
      },
      body: body,
      credentials: 'same-origin',
    })
      .then(parseAnalyzeResponse)
      .then(function (data) {
        applyAutofill(data);
        attachImageToProductForm(aiScanFile);
        setAiStatus(
          'Details filled — HSN ' + (data.hsn_code || '—') + ', '
          + ((data.variant_draft_rows && data.variant_draft_rows.length) || 0) + ' SKU row(s). '
          + 'Set selling & cost price, then save.',
          'success'
        );
      })
      .catch(function (err) {
        setAiStatus(err.message || 'Analysis failed.', 'danger');
      })
      .finally(function () {
        aiBtn.disabled = false;
      });
  });

  const generateSkusBtn = document.getElementById('generate-skus-btn');
  const suggestSkusUrl = productForm?.dataset.suggestSkusUrl;

  generateSkusBtn?.addEventListener('click', function () {
    if (!suggestSkusUrl) return;
    const color = document.querySelector('#variant-rows input[name="variant_color[]"]')?.value?.trim()
      || document.getElementById('name')?.value?.trim()
      || 'Multi';
    const ageGroups = Array.from(document.querySelectorAll('input[name="age_groups"]:checked'))
      .map(function (cb) { return cb.value; });
    if (!ageGroups.length) {
      alert('Select at least one age band in section 2, then generate SKUs.');
      return;
    }
    const fd = new FormData();
    const csrf = document.querySelector('meta[name="csrf-token"]')?.content || '';
    if (csrf) fd.append('csrf_token', csrf);
    fd.append('product_type', lastAiProductType);
    fd.append('color', color);
    ageGroups.forEach(function (a) { fd.append('age_groups', a); });

    generateSkusBtn.disabled = true;
    fetch(suggestSkusUrl, { method: 'POST', body: fd, credentials: 'same-origin' })
      .then(function (r) { return r.json(); })
      .then(function (res) {
        if (!res.success) {
          alert(res.message || 'Could not generate SKUs.');
          return;
        }
        if (res.data.hsn_code) setFieldValue('hsn_code', res.data.hsn_code);
        fillVariantRows(res.data.variant_draft_rows || []);
      })
      .catch(function () { alert('Network error generating SKUs.'); })
      .finally(function () { generateSkusBtn.disabled = false; });
  });

  const mktBtn = document.getElementById('product-marketing-gen-btn');
  const mktOut = document.getElementById('product-marketing-output');
  const mktStatus = document.getElementById('product-marketing-status');
  const mktUrl = productForm?.dataset.marketingUrl;
  const productId = productForm?.dataset.productId;

  function setMktStatus(msg, tone) {
    if (!mktStatus) return;
    mktStatus.textContent = msg;
    mktStatus.className = 'small mt-2 text-' + (tone || 'muted');
  }

  mktBtn?.addEventListener('click', function () {
    if (!mktUrl) return;
    const name = document.getElementById('name')?.value?.trim();
    if (!name && !productId) {
      setMktStatus('Enter a product name first.', 'danger');
      return;
    }
    mktBtn.disabled = true;
    setMktStatus('Generating marketing copy…', 'primary');
    const fd = new FormData();
    const csrf = document.querySelector('meta[name="csrf-token"]')?.content || '';
    if (csrf) fd.append('csrf_token', csrf);
    if (productId) fd.append('product_id', productId);
    else {
      fd.append('name', name);
      fd.append('short_description', document.getElementById('short_description')?.value || '');
      fd.append('description', document.getElementById('description')?.value || '');
      fd.append('price', document.getElementById('price')?.value || '');
      fd.append('compare_at_price', document.getElementById('compare_at_price')?.value || '');
      fd.append('material', document.getElementById('material')?.value || '');
      fd.append('brand', document.getElementById('brand')?.value || '');
      fd.append('gender', document.getElementById('gender')?.value || '');
    }
    fetch(mktUrl, { method: 'POST', body: fd, credentials: 'same-origin' })
      .then(function (r) { return r.json(); })
      .then(function (res) {
        if (!res.success) {
          setMktStatus(res.message || 'Failed', 'danger');
          return;
        }
        const d = res.data;
        const blocks = [
          ['Instagram', (d.instagram_caption || '') + '\n\n' + (d.instagram_hashtags || '')],
          ['WhatsApp', d.whatsapp_broadcast],
          ['SEO title', d.seo_title],
          ['SEO description', d.seo_description],
        ];
        mktOut.innerHTML = blocks.map(function (b) {
          return '<div class="border rounded p-3 mb-2"><strong class="small d-block mb-1">' + b[0] +
            '</strong><pre class="small mb-0" style="white-space:pre-wrap">' + (b[1] || '') + '</pre></div>';
        }).join('') + '<a href="' + (window.location.origin || '') + '/admin/marketing-ai" class="small">Open full Marketing AI →</a>';
        mktOut.classList.remove('d-none');
        setMktStatus('Copy ready — paste to Instagram or WhatsApp.', 'success');
      })
      .catch(function () { setMktStatus('Network error.', 'danger'); })
      .finally(function () { mktBtn.disabled = false; });
  });
})();
