(function () {
  'use strict';

  TabloKur({
    tablo: 'businessTable', url: '/isletmeler/veri', arama: 'businessSearch', toplam: 'businessTotal',
    sayfalama: 'businessPager', excel: 'businessExport', kartlar: true, kartParametre: 'status',
    ozetAlanlari: {total: 'businessCountAll', active: 'businessCountActive', passive: 'businessCountPassive'}
  });

  var modalEl = document.getElementById('businessModal');
  var form = document.getElementById('businessForm');
  var modal = bootstrap.Modal.getOrCreateInstance(modalEl);
  var title = document.getElementById('businessModalTitle');

  // Tek form hem "yeni" hem "düzenle" modunu paylaşır.
  function openBusinessModal(record) {
    form.reset();
    var isEdit = !!record;
    form.action = isEdit ? '/isletmeler/' + record.business_id + '/duzenle' : '/isletmeler/yeni';
    title.textContent = isEdit ? form.getAttribute('data-title-edit') : form.getAttribute('data-title-new');
    if (isEdit) {
      document.getElementById('businessName').value = record.business_name;
      document.getElementById('businessUrl').value = record.publish_url;
    }
    modal.show();
  }

  document.getElementById('businessNew').addEventListener('click', function () { openBusinessModal(null); });
  document.querySelector('#businessTable tbody').addEventListener('click', function (event) {
    var button = event.target.closest('[data-business-edit]');
    if (button) { openBusinessModal(JSON.parse(button.getAttribute('data-record'))); }
  });
})();
