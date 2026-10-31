/* Sunucu taraflı tablo: arama (300 ms debounce), kolon filtreleri, sayaç kartları ve sayfalama.
 * Her zaman AJAX ile sunucudan çeker; istemcide satır gizleyerek filtreleme yapılmaz. */
(function () {
  'use strict';

  window.TabloKur = function (options) {
    var table = document.getElementById(options.tablo);
    var tbody = table.querySelector('tbody');
    var search = options.arama ? document.getElementById(options.arama) : null;
    var totalEl = options.toplam ? document.getElementById(options.toplam) : null;
    var pager = options.sayfalama ? document.getElementById(options.sayfalama) : null;
    var clearBtn = document.querySelector('[data-filtre-temizle="' + options.tablo + '"]');
    var cards = options.kartlar ? document.querySelectorAll('[data-filtre]') : [];
    var state = {page: 1, card: ''};
    var timer = null;

    function columnFilters() { return table.querySelectorAll('[data-kolon-filtre]'); }

    function query() {
      var params = new URLSearchParams();
      if (search && search.value.trim()) { params.set('q', search.value.trim()); }
      if (state.card && options.kartParametre) { params.set(options.kartParametre, state.card); }
      columnFilters().forEach(function (select) {
        if (select.value) { params.set(select.getAttribute('data-kolon-filtre'), select.value); }
      });
      return params;
    }

    function updateClear() {
      var filled = !!(search && search.value.trim()) || Array.prototype.some.call(columnFilters(), function (s) { return s.value; });
      if (clearBtn) { clearBtn.hidden = !filled; }
    }

    function updateExport() {
      if (!options.excel) { return; }
      var link = document.getElementById(options.excel);
      if (link) { link.href = link.getAttribute('data-base') + (query().toString() ? '?' + query().toString() : ''); }
    }

    function renderPager(pages) {
      if (!pager) { return; }
      pager.hidden = pages <= 1;
      pager.textContent = '';
      if (pages <= 1) { return; }
      [['prev', 'bi-chevron-left', state.page > 1, state.page - 1], ['next', 'bi-chevron-right', state.page < pages, state.page + 1]]
        .forEach(function (item) {
          var button = document.createElement('button');
          button.type = 'button';
          button.className = 'btn btn-sm btn-outline-secondary';
          button.disabled = !item[2];
          button.setAttribute('aria-label', item[0]);
          button.innerHTML = '<i class="bi ' + item[1] + '" aria-hidden="true"></i>';
          button.addEventListener('click', function () { state.page = item[3]; load(); });
          pager.appendChild(button);
        });
      var label = document.createElement('span');
      label.className = 'mx-2 text-muted small';
      label.textContent = state.page + ' / ' + pages;
      pager.insertBefore(label, pager.lastChild);
    }

    function load() {
      var params = query();
      if (state.page > 1) { params.set('page', state.page); }
      updateClear();
      updateExport();
      return fetch(options.url + '?' + params.toString(), {
        headers: {'X-Requested-With': 'XMLHttpRequest'}, credentials: 'same-origin'
      }).then(function (response) { return response.json(); }).then(function (data) {
        tbody.innerHTML = data.html;
        if (totalEl) { totalEl.textContent = data.total; }
        renderPager(data.pages);
        if (data.ozet && options.ozetAlanlari) {
          Object.keys(options.ozetAlanlari).forEach(function (key) {
            var el = document.getElementById(options.ozetAlanlari[key]);
            if (el) { el.textContent = data.ozet[key]; }
          });
        }
        if (window.initTooltips) { window.initTooltips(tbody); }
      }).catch(function () { window.toast(document.documentElement.getAttribute('data-network-error') || '', false); });
    }

    function reset() { state.page = 1; load(); }

    if (search) {
      search.addEventListener('input', function () { clearTimeout(timer); timer = setTimeout(reset, 300); });
    }
    columnFilters().forEach(function (select) { select.addEventListener('change', reset); });
    Array.prototype.forEach.call(cards, function (card) {
      card.addEventListener('click', function () {
        state.card = card.getAttribute('data-filtre');
        Array.prototype.forEach.call(cards, function (other) {
          var active = other === card;
          other.classList.toggle('active', active);
          other.setAttribute('aria-pressed', active ? 'true' : 'false');
        });
        reset();
      });
    });
    if (clearBtn) {
      clearBtn.addEventListener('click', function () {
        if (search) { search.value = ''; }
        columnFilters().forEach(function (select) { select.value = ''; });
        reset();
      });
    }
    document.addEventListener('tablo:yenile', function (event) {
      if (event.detail.id === options.tablo) { load(); }
    });

    var exportLink = options.excel ? document.getElementById(options.excel) : null;
    if (exportLink) { exportLink.setAttribute('data-base', exportLink.getAttribute('href')); }
    load();
    return {yenile: load};
  };
})();
