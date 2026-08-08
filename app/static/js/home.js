(function () {
  document.addEventListener('DOMContentLoaded', function () {
    var toggle = document.getElementById('genderToggle');
    if (toggle) {
      var buttons = toggle.querySelectorAll('[data-gender-filter]');
      var icons = document.querySelectorAll('[data-shop-gender]');
      var cards = document.querySelectorAll('.home-product-card[data-gender]');

      function applyGender(gender) {
        buttons.forEach(function (btn) {
          btn.classList.toggle('is-active', btn.getAttribute('data-gender-filter') === gender);
        });
        icons.forEach(function (icon) {
          var g = icon.getAttribute('data-shop-gender');
          icon.hidden = g !== 'all' && g !== gender;
        });
        cards.forEach(function (card) {
          var g = card.getAttribute('data-gender') || 'kids';
          var show = gender === 'girls' ? (g === 'girls' || g === 'kids') :
            gender === 'boys' ? (g === 'boys' || g === 'kids') : true;
          card.style.display = show ? '' : 'none';
        });
      }

      buttons.forEach(function (btn) {
        btn.addEventListener('click', function () {
          applyGender(btn.getAttribute('data-gender-filter'));
        });
      });
      applyGender('girls');
    }

    document.querySelectorAll('.home-carousel-arrow').forEach(function (btn) {
      var track = document.querySelector(btn.getAttribute('data-target'));
      if (!track) return;
      btn.addEventListener('click', function () {
        var dir = btn.getAttribute('data-dir');
        var amount = track.clientWidth * 0.85;
        track.scrollBy({ left: dir === 'prev' ? -amount : amount, behavior: 'smooth' });
      });
    });

    document.querySelectorAll('.home-product-size').forEach(function (select) {
      select.addEventListener('change', function () {
        var opt = select.options[select.selectedIndex];
        var form = select.closest('form');
        var colorInput = form && form.querySelector('input[name="color"]');
        if (colorInput && opt && opt.dataset.color) {
          colorInput.value = opt.dataset.color;
        }
        if (form && opt && opt.dataset.variantId) {
          var variantInput = form.querySelector('input[name="variant_id"]');
          if (!variantInput) {
            variantInput = document.createElement('input');
            variantInput.type = 'hidden';
            variantInput.name = 'variant_id';
            form.appendChild(variantInput);
          }
          variantInput.value = opt.dataset.variantId;
        }
      });
    });
  });
})();
