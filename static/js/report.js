(function () {
  'use strict';

  TabloKur({
    tablo: 'reportTable', url: '/egitim-raporu/veri', arama: 'reportSearch', toplam: 'reportTotal',
    sayfalama: 'reportPager', excel: 'reportExport', kartlar: true, kartParametre: 'status',
    ozetAlanlari: {total: 'reportCountAll', completed: 'reportCountCompleted', in_progress: 'reportCountProgress',
                   not_started: 'reportCountNotStarted'}
  });
})();
