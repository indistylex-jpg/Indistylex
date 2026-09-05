(function () {
    'use strict';

    var csrf = document.querySelector('meta[name="csrf-token"]');
    var urls = window.MARKETING_AI_URLS || {};

    function postForm(url, fields) {
        var fd = new FormData();
        if (csrf) fd.append('csrf_token', csrf.content);
        Object.keys(fields).forEach(function (k) {
            if (fields[k] != null && fields[k] !== '') fd.append(k, fields[k]);
        });
        return fetch(url, { method: 'POST', body: fd, credentials: 'same-origin' })
            .then(function (r) { return r.json(); });
    }

    function copyBtn() {
        return '<button type="button" class="btn btn-sm btn-outline-secondary copy-mkt"><i class="bi bi-clipboard"></i> Copy</button>';
    }

    function escapeHtml(s) {
        var d = document.createElement('div');
        d.textContent = s || '';
        return d.innerHTML;
    }

    function card(title, body) {
        return '<div class="col-md-6"><div class="card h-100 border-0 shadow-sm">' +
            '<div class="card-body"><div class="d-flex justify-content-between align-items-start gap-2 mb-2">' +
            '<h6 class="fw-semibold mb-0">' + escapeHtml(title) + '</h6>' + copyBtn() +
            '</div><pre class="small mb-0 mkt-pre">' + escapeHtml(body) + '</pre></div></div></div>';
    }

    document.addEventListener('click', function (e) {
        var btn = e.target.closest('.copy-mkt');
        if (!btn) return;
        var pre = btn.closest('.card-body, .list-group-item') && btn.closest('.card-body, .list-group-item').querySelector('.mkt-pre, pre');
        var text = pre ? pre.textContent : '';
        navigator.clipboard.writeText(text).then(function () {
            btn.innerHTML = '<i class="bi bi-check2"></i> Copied';
            setTimeout(function () {
                btn.innerHTML = '<i class="bi bi-clipboard"></i> Copy';
            }, 1500);
        });
    });

    var productBtn = document.getElementById('mkt-generate-product');
    if (productBtn) {
        productBtn.addEventListener('click', function () {
            var status = document.getElementById('mkt-product-status');
            var results = document.getElementById('mkt-product-results');
            var cards = document.getElementById('mkt-product-cards');
            var pid = document.getElementById('mkt-product-id').value;
            status.textContent = 'Generating… (10–20 sec)';
            productBtn.disabled = true;

            postForm(urls.product, { product_id: pid }).then(function (res) {
                productBtn.disabled = false;
                if (!res.success) {
                    status.textContent = res.message || 'Failed';
                    return;
                }
                var d = res.data;
                var items = [
                    ['Instagram caption', (d.instagram_caption || '') + '\n\n' + (d.instagram_hashtags || '')],
                    ['WhatsApp broadcast', d.whatsapp_broadcast],
                    ['Facebook post', d.facebook_post],
                    ['Reel hook', d.reel_hook],
                    ['SEO title', d.seo_title],
                    ['SEO description', d.seo_description],
                    ['Email promo', (d.email_subject || '') + '\n' + (d.email_snippet || '')],
                    ['Story overlay', d.story_text],
                ];
                cards.innerHTML = items.map(function (x) { return card(x[0], x[1]); }).join('');
                results.classList.remove('d-none');
                status.textContent = 'Done — copy and paste to Instagram / WhatsApp / Meta.';
            }).catch(function () {
                productBtn.disabled = false;
                status.textContent = 'Network error. Try again.';
            });
        });
    }

    var campBtn = document.getElementById('mkt-generate-campaigns');
    if (campBtn) {
        campBtn.addEventListener('click', function () {
            var status = document.getElementById('mkt-campaign-status');
            var box = document.getElementById('mkt-campaign-results');
            status.textContent = 'Planning your week…';
            campBtn.disabled = true;
            postForm(urls.campaigns, {}).then(function (res) {
                campBtn.disabled = false;
                if (!res.success) {
                    status.textContent = res.message || 'Failed';
                    return;
                }
                var d = res.data;
                var html = '<h6 class="fw-semibold">' + escapeHtml(d.week_theme || 'This week') + '</h6><div class="list-group">';
                (d.ideas || []).forEach(function (idea) {
                    html += '<div class="list-group-item">' +
                        '<strong>' + escapeHtml(idea.day) + ' · ' + escapeHtml(idea.channel) + '</strong>' +
                        '<div class="small text-muted">' + escapeHtml(idea.title) + '</div>' +
                        '<p class="small mb-1 mt-2">' + escapeHtml(idea.action) + '</p>' +
                        '<pre class="small bg-light p-2 rounded mb-2">' + escapeHtml(idea.caption_draft) + '</pre>' +
                        copyBtn() +
                        '</div>';
                });
                html += '</div>';
                box.innerHTML = html;
                box.classList.remove('d-none');
                status.textContent = 'Weekly plan ready.';
            }).catch(function () {
                campBtn.disabled = false;
                status.textContent = 'Network error.';
            });
        });
    }

    document.querySelectorAll('.mkt-brand-btn').forEach(function (btn) {
        btn.addEventListener('click', function () {
            var type = btn.getAttribute('data-type');
            var status = document.getElementById('mkt-brand-status');
            var box = document.getElementById('mkt-brand-results');
            status.textContent = 'Generating…';
            btn.disabled = true;
            postForm(urls.brand, { type: type }).then(function (res) {
                btn.disabled = false;
                if (!res.success) {
                    status.textContent = res.message || 'Failed';
                    return;
                }
                box.innerHTML = '<pre class="small bg-light p-3 rounded mb-2">' + escapeHtml(JSON.stringify(res.data, null, 2)) + '</pre>' + copyBtn();
                box.classList.remove('d-none');
                status.textContent = 'Brand copy ready — copy JSON or lines you need.';
            }).catch(function () {
                btn.disabled = false;
                status.textContent = 'Network error.';
            });
        });
    });
})();
