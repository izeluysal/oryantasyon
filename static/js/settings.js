(function () {
  'use strict';

  if (document.getElementById('userTable')) {
    TabloKur({
      tablo: 'userTable', url: '/ayarlar/kullanicilar/veri', arama: 'userSearch', toplam: 'userTotal',
      sayfalama: 'userPager', excel: 'userExport', kartlar: true, kartParametre: 'status',
      ozetAlanlari: {total: 'userCountAll', active: 'userCountActive', passive: 'userCountPassive'}
    });

    var modalEl = document.getElementById('userModal');
    if (modalEl) {
      var form = document.getElementById('userForm');
      var modal = bootstrap.Modal.getOrCreateInstance(modalEl);
      var title = document.getElementById('userModalTitle');
      var activeRow = document.getElementById('userActiveRow');

      // Tek form hem "yeni" hem "düzenle" modunu paylaşır: null verilirse yeni, kayıt verilirse düzenle.
      function openUserModal(record) {
        form.reset();
        var isEdit = !!record;
        form.action = isEdit ? '/ayarlar/kullanicilar/' + record.user_id + '/duzenle' : '/ayarlar/kullanicilar/yeni';
        title.textContent = isEdit ? form.getAttribute('data-title-edit') : form.getAttribute('data-title-new');
        activeRow.hidden = !isEdit;
        document.getElementById('userPassword').required = !isEdit;
        if (isEdit) {
          document.getElementById('userFullName').value = record.full_name;
          document.getElementById('userEmail').value = record.email;
          document.getElementById('userPhone').value = record.phone;
          document.getElementById('userRole').value = record.role;
          document.getElementById('userTheme').value = record.theme;
          document.getElementById('userActive').checked = !!record.is_active;
        }
        modal.show();
      }

      document.getElementById('userNew').addEventListener('click', function () { openUserModal(null); });
      document.querySelector('#userTable tbody').addEventListener('click', function (event) {
        var button = event.target.closest('[data-user-edit]');
        if (button) { openUserModal(JSON.parse(button.getAttribute('data-record'))); }
      });
    }
  }

  if (document.getElementById('actionLogTable')) {
    var loaded = {};
    function lazyTable(tabSelector, key, options) {
      var tab = document.querySelector(tabSelector);
      if (!tab) { return; }
      function start() { if (!loaded[key]) { loaded[key] = true; TabloKur(options); } }
      tab.addEventListener('shown.bs.tab', start);
      if (tab.classList.contains('active')) { start(); }
    }
    lazyTable('[data-bs-target="#tab-action-logs"]', 'action', {
      tablo: 'actionLogTable', url: '/ayarlar/loglar/islem/veri', arama: 'actionLogSearch',
      toplam: 'actionLogTotal', sayfalama: 'actionLogPager'
    });
    lazyTable('[data-bs-target="#tab-error-logs"]', 'error', {
      tablo: 'errorLogTable', url: '/ayarlar/loglar/hata/veri', arama: 'errorLogSearch',
      toplam: 'errorLogTotal', sayfalama: 'errorLogPager'
    });
  }
})();
