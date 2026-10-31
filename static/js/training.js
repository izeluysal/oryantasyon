(function () {
  'use strict';

  var list = document.getElementById('questionList');
  var nextBtn = document.getElementById('nextBtn');

  function shuffle(items) {
    var order = items.map(function (value, index) { return index; });
    for (var i = order.length - 1; i > 0; i--) {
      var j = Math.floor(Math.random() * (i + 1));
      var tmp = order[i]; order[i] = order[j]; order[j] = tmp;
    }
    return order;
  }

  function format(template, values) {
    return Object.keys(values).reduce(function (text, key) { return text.split('{' + key + '}').join(values[key]); }, template);
  }

  // HUD: sunucudan gelen özetle Ece-Coin, seviye, ilerleme ve rozetler anında güncellenir.
  function updateHud(totals) {
    document.getElementById('hudCoins').textContent = totals.coins.toLocaleString(document.documentElement.getAttribute('data-yerel-ayar'));
    document.getElementById('hudLevel').textContent = totals.level;
    document.getElementById('hudDone').textContent = totals.done;
    var percent = Math.round(100 * totals.done / totals.total);
    document.getElementById('hudProgress').style.width = percent + '%';
    document.getElementById('hudProgressBar').setAttribute('aria-valuenow', totals.done);
    var badges = document.getElementById('hudBadges');
    badges.textContent = '';
    totals.badges.forEach(function (badge) {
      var el = document.createElement('span');
      el.className = 'badge text-bg-warning';
      var icon = document.createElement('i');
      icon.className = 'bi bi-star-fill me-1';
      icon.setAttribute('aria-hidden', 'true');
      el.appendChild(icon);
      el.appendChild(document.createTextNode(badge.label));
      badges.appendChild(el);
    });
  }

  function lock(box) {
    box.classList.add('done');
    box.setAttribute('data-solved', '1');
    Array.prototype.forEach.call(box.querySelectorAll('.opt'), function (button) { button.disabled = true; });
  }

  function allSolved() {
    return Array.prototype.every.call(list.querySelectorAll('.q'), function (box) { return box.getAttribute('data-solved') === '1'; });
  }

  function submitAnswer(box, optionIndex, button) {
    var feedback = box.querySelector('.fb');
    window.postData(list.getAttribute('data-answer-url'), {question_id: box.getAttribute('data-question-id'), option: optionIndex})
      .then(function (response) { return response.json(); })
      .then(function (data) {
        if (!data.ok) { window.toast(data.message || '', false); return; }
        updateHud(data.totals);
        if (data.correct) {
          button.classList.add('ok');
          feedback.className = 'fb ok';
          var text = format(list.getAttribute('data-msg-correct'), {why: data.explanation});
          if (data.coins) { text += '  ' + format(list.getAttribute('data-msg-earned'), {coins: data.coins}); }
          feedback.textContent = text;
          lock(box);
          if (data.coins) { window.toast(format(list.getAttribute('data-msg-earned'), {coins: data.coins}), true); }
          if (data.bonus) { window.toast(format(list.getAttribute('data-msg-bonus'), {coins: data.bonus}), true); }
          if (data.level_up) { window.toast(format(list.getAttribute('data-msg-level'), {level: data.totals.level}), true); }
          data.new_badges.forEach(function (label) { window.toast(format(list.getAttribute('data-msg-badge'), {badge: label}), true); });
          if (data.screen_completed || allSolved()) { nextBtn.disabled = false; nextBtn.setAttribute('data-done', '1'); }
        } else {
          button.classList.add('bad');
          button.disabled = true;
          feedback.className = 'fb bad';
          feedback.textContent = list.getAttribute('data-msg-wrong');
        }
      });
  }

  if (list) {
    Array.prototype.forEach.call(list.querySelectorAll('.q'), function (box) {
      var holder = box.querySelector('.opts');
      var options = JSON.parse(holder.getAttribute('data-options'));
      shuffle(options).forEach(function (originalIndex) {
        var button = document.createElement('button');
        button.type = 'button';
        button.className = 'opt';
        button.textContent = options[originalIndex];  // metin veritabanından gelir: textContent
        button.addEventListener('click', function () { submitAnswer(box, originalIndex, button); });
        holder.appendChild(button);
      });
      if (box.getAttribute('data-solved') === '1') { lock(box); }
    });
    if (allSolved() && nextBtn) { nextBtn.disabled = false; }
  }

  // Sorusuz ekranda "Devam" ekranı tamamlandı işaretler; sonra sonraki ekrana geçer.
  if (nextBtn) {
    nextBtn.addEventListener('click', function () {
      var go = function () { window.location.href = nextBtn.getAttribute('data-next-url'); };
      if (nextBtn.getAttribute('data-has-questions') === '1' || nextBtn.getAttribute('data-done') === '1') { go(); return; }
      nextBtn.disabled = true;
      window.postData(nextBtn.getAttribute('data-complete-url'), {}).then(function (response) { return response.json(); })
        .then(function (data) { if (data.ok) { go(); } else { nextBtn.disabled = false; window.toast(data.message || '', false); } });
    });
  }

  // Süreli ekran: geri sayım yalnızca bilgi içindir; puan kararı sunucudadır.
  var timer = document.getElementById('trainingTimer');
  if (timer) {
    var remaining = parseInt(timer.getAttribute('data-remaining'), 10);
    var text = document.getElementById('timerText');
    var tick = function () {
      if (remaining <= 0) { timer.classList.add('late'); text.textContent = timer.getAttribute('data-late'); return; }
      var minutes = Math.floor(remaining / 60), seconds = ('0' + (remaining % 60)).slice(-2);
      text.textContent = format(timer.getAttribute('data-left'), {time: minutes + ':' + seconds});
      remaining -= 1;
      setTimeout(tick, 1000);
    };
    tick();
  }
})();
