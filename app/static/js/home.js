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

    document.querySelectorAll('.home-carousel-nav').forEach(function (nav) {
      var track = document.querySelector(nav.getAttribute('data-target'));
      if (!track) return;
      nav.querySelector('[data-dir="prev"]')?.addEventListener('click', function () {
        track.scrollBy({ left: -track.clientWidth * 0.85, behavior: 'smooth' });
      });
      nav.querySelector('[data-dir="next"]')?.addEventListener('click', function () {
        track.scrollBy({ left: track.clientWidth * 0.85, behavior: 'smooth' });
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
      });
    });
  });
})();
