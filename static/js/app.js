(function () {
  'use strict';

  var shell = document.body;

  function csrfToken() {
    var meta = document.querySelector('meta[name="csrf-token"]');
    return meta ? meta.getAttribute('content') : '';
  }

  function post(url, data) {
    var body = new URLSearchParams(data);
    return fetch(url, {
      method: 'POST',
      headers: {'X-CSRFToken': csrfToken(), 'X-Requested-With': 'XMLHttpRequest'},
      body: body,
      credentials: 'same-origin'
    });
  }

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
})();
