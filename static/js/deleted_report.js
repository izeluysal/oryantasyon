(function () {
  'use strict';

  TabloKur({
    tablo: 'deletedTable', url: '/silinme-raporu/veri', arama: 'deletedSearch', toplam: 'deletedTotal',
    sayfalama: 'deletedPager'
  });

  var modal = bootstrap.Modal.getOrCreateInstance(document.getElementById('detailModal'));
  var body = document.getElementById('detailBody');

  function cell(value) {
    var td = document.createElement('td');
    td.textContent = value === null || value === undefined ? '-' : String(value);  // kullanıcı verisi: textContent
    return td;
  }

  // Ayrıntı: işlemin kolon / eski değer / yeni değer tablosu.
  document.querySelector('#deletedTable tbody').addEventListener('click', function (event) {
    var button = event.target.closest('[data-detail]');
    if (!button) { return; }
    fetch(button.getAttribute('data-detail'), {headers: {'X-Requested-With': 'XMLHttpRequest'}, credentials: 'same-origin'})
      .then(function (response) { return response.json(); })
      .then(function (data) {
        body.textContent = '';
        data.changes.forEach(function (change) {
          var tr = document.createElement('tr');
          tr.appendChild(cell(change.column));
          tr.appendChild(cell(change.old));
          tr.appendChild(cell(change.new));
          body.appendChild(tr);
        });
        modal.show();
      });
  });
})();
