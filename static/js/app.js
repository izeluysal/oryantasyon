(function () {
  'use strict';

  var shell = document.body;

  function csrfToken() {
    var meta = document.querySelector('meta[name="csrf-token"]');
    return meta ? meta.getAttribute('content') : '';
  }

  function post(url, data) {
    return fetch(url, {
      method: 'POST',
      headers: {'X-CSRFToken': csrfToken(), 'X-Requested-With': 'XMLHttpRequest'},
      body: new URLSearchParams(data),
      credentials: 'same-origin'
    });
  }
  window.postData = post;

  // Sidebar daralt/genişlet: sınıf anında uygulanır, tercih DB'ye ve çereze AJAX ile yazılır.
  var sidebarToggle = document.getElementById('sidebarToggle');
  if (sidebarToggle) {
    sidebarToggle.addEventListener('click', function () {
      var collapsed = shell.classList.toggle('sidebar-collapsed');
      post(sidebarToggle.dataset.sidebarUrl, {collapsed: collapsed ? '1' : '0'});
    });
  }

  // Mobil hamburger ve karartma: aynı aç/kapa mantığını paylaşır.
  var mobileBtn = document.getElementById('mobileMenuBtn');
  var backdrop = document.getElementById('sidebarBackdrop');
  if (mobileBtn) {
    mobileBtn.addEventListener('click', function () { shell.classList.toggle('sidebar-mobile-open'); });
  }
  if (backdrop) {
    backdrop.addEventListener('click', function () { shell.classList.remove('sidebar-mobile-open'); });
  }

  // Tema: data-theme her zaman <html> üzerinde açık değerle tutulur.
  var themeToggle = document.getElementById('themeToggle');
  if (themeToggle) {
    themeToggle.addEventListener('click', function () {
      var root = document.documentElement;
      var next = root.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
      root.setAttribute('data-theme', next);
      post(themeToggle.dataset.themeUrl, {theme: next});
    });
  }

  // Tooltip: kök düğüm verilir ki AJAX ile eklenen parçalar için tekrar çağrılabilsin.
  function initTooltips(root) {
    (root || document).querySelectorAll('[data-bs-toggle="tooltip"]').forEach(function (el) {
      if (!bootstrap.Tooltip.getInstance(el)) { new bootstrap.Tooltip(el); }
    });
  }
  window.initTooltips = initTooltips;
  document.addEventListener('DOMContentLoaded', function () { initTooltips(document); });
  document.addEventListener('shown.bs.modal', function (event) { initTooltips(event.target); });

  // Toast: sağ altta, 20 sn sonra kapanır; kapsayıcı aria-live bölgesidir.
  window.toast = function (message, ok) {
    var container = document.getElementById('toastContainer');
    var el = document.createElement('div');
    el.className = 'toast align-items-center border-0 text-bg-' + (ok ? 'success' : 'danger');
    el.setAttribute('role', ok ? 'status' : 'alert');
    var wrapper = document.createElement('div');
    wrapper.className = 'd-flex';
    var body = document.createElement('div');
    body.className = 'toast-body';
    body.textContent = message;  // kullanıcı verisi içerebilir: textContent
    var close = document.createElement('button');
    close.type = 'button';
    close.className = 'btn-close btn-close-white me-2 m-auto';
    close.setAttribute('data-bs-dismiss', 'toast');
    wrapper.appendChild(body);
    wrapper.appendChild(close);
    el.appendChild(wrapper);
    container.appendChild(el);
    el.addEventListener('hidden.bs.toast', function () { el.remove(); });
    new bootstrap.Toast(el, {delay: 20000}).show();
  };

  // Onay penceresi: tek ortak modal; Vazgeç/Esc/dış tıklama false, yalnızca Onayla true döndürür.
  window.onayIste = function (message) {
    var modalEl = document.getElementById('onayModal');
    if (!modalEl) { return Promise.resolve(window.confirm(message)); }
    return new Promise(function (resolve) {
      var modal = bootstrap.Modal.getOrCreateInstance(modalEl);
      var result = false;
      document.getElementById('onayModalBody').textContent = message;
      function onOk() { result = true; modal.hide(); }
      function onCancel() { modal.hide(); }
      function onHidden() {
        okBtn.removeEventListener('click', onOk);
        cancelBtn.removeEventListener('click', onCancel);
        modalEl.removeEventListener('hidden.bs.modal', onHidden);
        resolve(result);
      }
      var okBtn = document.getElementById('onayModalOk');
      var cancelBtn = document.getElementById('onayModalCancel');
      okBtn.addEventListener('click', onOk);
      cancelBtn.addEventListener('click', onCancel);
      modalEl.addEventListener('hidden.bs.modal', onHidden);
      modal.show();
    });
  };

  // AJAX form: data-ajax. Sonuç toast ile bildirilir; sayfa yenilenmez.
  function setBusy(form, busy) {
    var button = form.querySelector('button[type="submit"]');
    if (!button) { return; }
    button.disabled = busy;
    var spinner = button.querySelector('.spinner-border');
    if (spinner) { spinner.classList.toggle('d-none', !busy); }
  }

  function sendAjaxForm(form) {
    setBusy(form, true);
    return fetch(form.action, {
      method: 'POST',
      headers: {'X-CSRFToken': csrfToken(), 'X-Requested-With': 'XMLHttpRequest'},
      body: new FormData(form),
      credentials: 'same-origin'
    }).then(function (response) {
      return response.json().then(function (data) { return data; });
    }).then(function (data) {
      window.toast(data.message || '', !!data.ok);
      if (data.ok) {
        var modalId = form.getAttribute('data-modal');
        if (modalId) { bootstrap.Modal.getOrCreateInstance(document.getElementById(modalId)).hide(); }
        if (form.hasAttribute('data-reload')) { window.location.reload(); }
        var tableId = form.getAttribute('data-refresh');
        if (tableId) { document.dispatchEvent(new CustomEvent('tablo:yenile', {detail: {id: tableId}})); }
      }
    }).catch(function () {
      // Ağ hatası: spinner kalkar, kullanıcı bilgilendirilir (sonsuz dönme yok).
      window.toast(document.documentElement.getAttribute('data-network-error') || '', false);
    }).then(function () { setBusy(form, false); });
  }

  document.addEventListener('submit', function (event) {
    var form = event.target;
    if (!form.matches('form[data-ajax], form[data-confirm]')) { return; }
    if (form.hasAttribute('data-confirmed')) { form.removeAttribute('data-confirmed'); return; }
    var ajax = form.hasAttribute('data-ajax');
    var confirmText = form.getAttribute('data-confirm');
    event.preventDefault();
    var proceed = confirmText ? window.onayIste(confirmText) : Promise.resolve(true);
    proceed.then(function (ok) {
      if (!ok) { return; }
      if (ajax) { sendAjaxForm(form); } else { form.setAttribute('data-confirmed', '1'); form.submit(); }
    });
  });
})();
