(function () {
  "use strict";
  var C = window.CONTENT, S = C.screens, KEY = "ece-oryantasyon-v1";
  var app = document.getElementById("app"), toastEl = document.getElementById("toast");
  var API = null, scOk = false, t0Page = Date.now();

  // ---- SCORM 1.2 (LMS içinde açılırsa ilerleme ve puan LMS'ye de yazılır) ----
  function findAPI() {
    var w = window, n = 0;
    while (w && n++ < 10) { try { if (w.API) return w.API; } catch (e) {} if (w.parent === w) break; w = w.parent; }
    try { if (window.opener && window.opener.API) return window.opener.API; } catch (e) {}
    return null;
  }
  function scGet(k) { try { return String(API.LMSGetValue(k)); } catch (e) { return ""; } }
  function scSet(k, v) { try { API.LMSSetValue(k, String(v)); } catch (e) {} }
  function scInit() { API = findAPI(); if (API) { try { scOk = String(API.LMSInitialize("")) === "true"; } catch (e) {} } }
  // suspend_data (SCORM 1.2 sınırı 4096 karakter) için kompakt kodlama
  function encode() {
    var p = S.map(function (s) {
      var r = st.screens[s.id]; if (!r) return 0;
      var it = s.items.map(function (x, k) { var i = r.items[k]; return i ? (Math.min(i.tries, 9) + (i.ok ? 10 : 0)).toString(36) : "0"; }).join("");
      return [r.coins || 0, r.perfect ? 1 : 0, r.done ? 1 : 0, it];
    });
    return JSON.stringify({ v: 1, n: st.name, c: st.cur, s: st.started, f: st.finished, p: p });
  }
  function decode(str) {
    try {
      var d = JSON.parse(str); if (!d || d.v !== 1) return null;
      var out = { name: d.n || "", cur: d.c || 0, started: d.s, finished: d.f, screens: {} };
      S.forEach(function (s, i) {
        var a = d.p[i]; if (!a) return;
        var r = { items: {}, coins: a[0], perfect: !!a[1], done: !!a[2] };
        String(a[3]).split("").forEach(function (ch, k) { var v = parseInt(ch, 36); if (v) r.items[k] = { tries: v % 10, ok: v >= 10 }; });
        out.screens[s.id] = r;
      });
      return out;
    } catch (e) { return null; }
  }
  function allDone() { return S.every(function (x) { var r = st.screens[x.id]; return r && r.done; }); }
  function scPush() {
    if (!scOk) return;
    var t = total(), done = allDone();
    scSet("cmi.suspend_data", encode());
    scSet("cmi.core.lesson_location", st.cur);
    scSet("cmi.core.score.min", 0); scSet("cmi.core.score.max", 100);
    scSet("cmi.core.score.raw", Math.round(t / C.total * 100));
    scSet("cmi.core.lesson_status", done ? "completed" : "incomplete");
    scSet("cmi.core.exit", done ? "" : "suspend");
    var sec = Math.floor((Date.now() - t0Page) / 1000), p = function (n) { return ("0" + n).slice(-2); };
    scSet("cmi.core.session_time", p(Math.floor(sec / 3600)) + ":" + p(Math.floor(sec % 3600 / 60)) + ":" + p(sec % 60));
    try { API.LMSCommit(""); } catch (e) {}
  }
  function scClose() { if (scOk) { scPush(); try { API.LMSFinish(""); } catch (e) {} scOk = false; } }
  window.addEventListener("pagehide", scClose); window.addEventListener("beforeunload", scClose);

  scInit();
  var st = load(), timerId = null;

  function load() {
    if (scOk) {
      var d = decode(scGet("cmi.suspend_data"));
      if (d) return d;
      var sn = scGet("cmi.core.student_name"), m = /^([^,]+),\s*(.+)$/.exec(sn);
      return { name: m ? m[2] + " " + m[1] : sn, cur: 0, started: null, finished: null, screens: {} };
    }
    try { var s = JSON.parse(localStorage.getItem(KEY)); if (s && s.screens) return s; } catch (e) {}
    return { name: "", cur: 0, started: null, finished: null, screens: {} };
  }
  function save() { try { localStorage.setItem(KEY, JSON.stringify(st)); } catch (e) {} scPush(); }

  // ---- Sonuç dosyası (yönetici raporlaması için) ----
  function result() {
    var t = total(), items = 0, first = 0;
    var ekranlar = S.map(function (s) {
      var r = st.screens[s.id] || { items: {} }, f = 0, tr = 0;
      s.items.forEach(function (x, k) { var i = r.items[k]; items++; if (i) { tr += i.tries; if (i.ok && i.tries === 1) { first++; f++; } } });
      return { no: s.no, baslik: s.title, coin: r.coins || 0, maxCoin: s.coins, tamam: !!r.done, ilkDenemeDogru: f, soru: s.items.length, denemeSayisi: tr };
    });
    return {
      kurs: "Ece Kalibrasyon Oryantasyon", surum: 1, ad: st.name, baslangic: st.started, bitis: st.finished,
      tamamlandi: allDone(), coin: t, toplamCoin: C.total, seviye: level(t),
      rozetler: C.badges.filter(badgeOn).map(function (b) { return b.name; }),
      tamamlananEkran: S.filter(function (x, i) { return screenDone(i); }).length, toplamEkran: S.length,
      ilkDenemeDogruOrani: items ? Math.round(first / items * 100) : 0, ekranlar: ekranlar
    };
  }
  function download() {
    var blob = new Blob([JSON.stringify(result(), null, 1)], { type: "application/json" });
    var a = document.createElement("a"), safe = (st.name || "calisan").replace(/[^\wığüşöçİĞÜŞÖÇ]+/g, "_");
    a.href = URL.createObjectURL(blob); a.download = "oryantasyon-sonuc-" + safe + ".json";
    document.body.appendChild(a); a.click(); a.remove();
  }
  function el(h) { var d = document.createElement("div"); d.innerHTML = h; return d.firstElementChild; }
  function esc(s) { return String(s).replace(/[&<>"]/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]; }); }
  function rec(id) { return st.screens[id] || (st.screens[id] = { items: {}, perfect: true, done: false, coins: 0 }); }
  function total() { var t = 0; for (var k in st.screens) t += st.screens[k].coins || 0; return t; }
  function level(t) { var n = C.levels[0][1]; C.levels.forEach(function (l) { if (t >= l[0]) n = l[1]; }); return n; }
  function toast(m) { toastEl.textContent = m; toastEl.classList.add("show"); clearTimeout(toast.t); toast.t = setTimeout(function () { toastEl.classList.remove("show"); }, 3200); }
  function shuffle(a) { var r = a.map(function (v, i) { return i; }); for (var i = r.length - 1; i > 0; i--) { var j = Math.floor(Math.random() * (i + 1)); var t = r[i]; r[i] = r[j]; r[j] = t; } return r; }
  function screenDone(i) { return !!(st.screens[S[i].id] && st.screens[S[i].id].done); }
  function unlocked(i) { for (var k = 0; k < i; k++) if (!screenDone(k)) return false; return true; }
  function badgeOn(b) { return b.screens.every(function (i) { var r = st.screens[S[i].id]; return r && r.done && r.perfect; }); }

  function award(id, item, key, ok, late) {
    var r = rec(id), it = r.items[key] || (r.items[key] = { tries: 0, ok: false });
    if (it.ok) return 0;
    it.tries++;
    if (!ok) { r.perfect = false; save(); return 0; }
    it.ok = true;
    var c = (it.tries === 1 && !late) ? item.coin : Math.floor(item.coin / 2);
    if (it.tries > 1 || late) r.perfect = false;
    var before = level(total());
    r.coins += c; save();
    var after = level(total());
    if (after !== before) toast("Yeni seviye: " + after + "!");
    return c;
  }

  function hud() {
    var t = total(), pct = Math.round(t / C.total * 100), done = S.filter(function (s, i) { return screenDone(i); }).length;
    return '<div class="hud"><div class="coin">' + t + ' <small style="font-size:.9rem">Ece-Coin</small></div>' +
      '<div class="level">' + esc(level(t)) + '</div><div class="bar" aria-hidden="true"><i style="width:' + Math.round(done / S.length * 100) + '%"></i></div>' +
      '<small>' + done + ' / ' + S.length + ' ekran · coin %' + pct + '</small>' +
      '<div class="badges">' + C.badges.map(function (b) { return '<span class="badge' + (badgeOn(b) ? ' on' : '') + '">' + (badgeOn(b) ? '★ ' : '☆ ') + esc(b.name) + '</span>'; }).join("") + '</div></div>';
  }

  function navHtml() {
    var h = "", last = "";
    S.forEach(function (s, i) {
      if (s.module !== last) { h += '<div class="mod">' + esc(s.module) + '</div>'; last = s.module; }
      var ok = unlocked(i);
      h += '<button data-go="' + i + '"' + (ok ? "" : " disabled") + (i === st.cur ? ' class="cur" aria-current="step"' : "") + '>' +
        (screenDone(i) ? '<span class="ck">✓</span>' : "") + esc(s.no) + " · " + esc(s.title) + '</button>';
    });
    return h;
  }

  function shell(inner) {
    app.innerHTML = '<div class="layout"><aside><h1>ECE KALİBRASYON</h1><div>Oryantasyon Programı</div>' + hud() +
      '<button class="btn ghost menu-btn" id="mb">Menü</button><nav id="nav">' + navHtml() + '</nav>' +
      (scOk ? "" : '<div style="margin-top:18px;font-size:.8rem"><button class="btn ghost" id="reset" style="padding:6px 12px;font-size:.8rem">İlerlemeyi sıfırla</button></div>') + '</aside>' +
      '<main id="main" tabindex="-1">' + inner + '</main></div>';
    document.getElementById("mb").onclick = function () { document.getElementById("nav").classList.toggle("open"); };
    var rs = document.getElementById("reset");
    if (rs) rs.onclick = function () {
      if (confirm("Tüm ilerleme ve Ece-Coin silinecek. Emin misin?")) { localStorage.removeItem(KEY); st = load(); welcome(); }
    };
    Array.prototype.forEach.call(document.querySelectorAll("[data-go]"), function (b) { b.onclick = function () { go(+b.dataset.go); }; });
  }

  function welcome() {
    var started = st.started;
    app.innerHTML = '<div class="hero"><div class="avatar" style="margin:0 auto;width:72px;height:72px;font-size:2rem">M</div>' +
      '<p style="color:var(--teal);font-weight:700;letter-spacing:.05em;margin-top:18px">ECE KALİBRASYON · ORYANTASYON</p>' +
      '<h1>Hassas Metroloji Yolculuğu</h1><p>Ölçümün ve güvenin izinde. Metroli rehberliğinde 8 modülü tamamla, Ece-Coin topla, rozetleri kazan.</p>' +
      '<label for="nm">Adın ve soyadın (sertifikada görünecek)</label><input id="nm" autocomplete="name" value="' + esc(st.name) + '">' +
      '<button class="btn" id="go">' + (started ? "Kaldığın yerden devam et" : "Yolculuğa başla") + '</button>' +
      '<p style="font-size:.85rem;margin-top:24px">Süre: yaklaşık 60–90 dakika · Sesli anlatım içerir (hoparlör veya kulaklık önerilir) · İlerlemen bu tarayıcıda saklanır.</p></div>';
    document.getElementById("go").onclick = function () {
      var n = document.getElementById("nm").value.trim();
      if (!n) { document.getElementById("nm").focus(); toast("Lütfen adını yaz."); return; }
      st.name = n; if (!st.started) st.started = new Date().toISOString(); save(); go(st.cur);
    };
  }

  function go(i) {
    clearInterval(timerId); st.cur = i; save();
    var s = S[i], r = rec(s.id), late = false, left = s.timer, t0 = Date.now();
    var h = '<div class="mlabel">' + esc(s.module) + " · Ekran " + esc(s.no) + '</div><h2>' + esc(s.title) + '</h2>';
    if (s.timer) h += '<div class="timer" id="tm" role="timer">Kalan süre: 3:00</div>';
    h += '<div class="panel"><ul>' + s.bullets.map(function (b) { return "<li>" + esc(b) + "</li>"; }).join("") + '</ul>';
    if (s.table) h += "<table>" + s.table.map(function (row, k) { return "<tr>" + row.map(function (c) { return (k ? "<td>" : "<th>") + esc(c) + (k ? "</td>" : "</th>"); }).join("") + "</tr>"; }).join("") + "</table>";
    if (s.note) h += '<div class="note">' + esc(s.note) + "</div>";
    h += '<div class="player" style="margin-top:14px"><div class="avatar" aria-hidden="true">M</div><audio controls preload="none" src="' + s.audio + '" aria-label="Metroli sesli anlatım"></audio></div>' +
      '<details><summary>Seslendirme metni</summary><p>' + esc(s.voice) + '</p></details></div>';
    if (s.items.length) h += '<h3 class="noprint">Pekiştirme' + (s.critical ? " (kritik senaryo: tüm adımlar doğru yapılmalı)" : "") + " · " + s.coins + ' Ece-Coin</h3><div id="qs"></div>';
    h += '<div class="actions"><button class="btn ghost" id="prev"' + (i ? "" : " disabled") + '>← Geri</button><button class="btn" id="next" disabled>' + (i === S.length - 1 ? "Sertifikaya git" : "Devam →") + '</button></div>';
    shell(h);
    var main = document.getElementById("main"); main.focus({ preventScroll: true }); window.scrollTo(0, 0);
    document.getElementById("prev").onclick = function () { go(i - 1); };
    var next = document.getElementById("next");
    next.onclick = function () { if (i === S.length - 1) certificate(); else go(i + 1); };

    function check() {
      var all = s.items.every(function (it, k) { return r.items[k] && r.items[k].ok; });
      if (all && !r.done) {
        if (s.bonus && !late) { r.coins += s.bonus; toast("Süre dolmadan bitirdin! +" + s.bonus + " Ece-Coin"); }
        r.done = true; if (!st.finished && S.every(function (x, n) { return n === i || screenDone(n); })) st.finished = new Date().toISOString();
        save(); refreshHud();
      }
      next.disabled = !r.done;
    }
    function refreshHud() { var a = document.querySelector(".hud"); if (a) a.outerHTML = hud(); var n = document.getElementById("nav"); if (n) { n.innerHTML = navHtml(); Array.prototype.forEach.call(n.querySelectorAll("[data-go]"), function (b) { b.onclick = function () { go(+b.dataset.go); }; }); } }

    if (!s.items.length) { r.done = true; save(); next.disabled = false; refreshHud(); }
    else {
      var qs = document.getElementById("qs");
      s.items.forEach(function (it, k) {
        var box = el('<div class="q"><h3></h3><div class="opts"></div><div class="fb" aria-live="polite"></div></div>');
        box.querySelector("h3").textContent = it.q;
        var ob = box.querySelector(".opts"), fb = box.querySelector(".fb");
        function mark() { box.classList.add("done"); Array.prototype.forEach.call(ob.children, function (b) { b.disabled = true; }); }
        shuffle(it.opts).forEach(function (oi) {
          var b = el('<button class="opt"></button>'); b.textContent = it.opts[oi];
          b.onclick = function () {
            var ok = oi === it.c, got = award(s.id, it, k, ok, late);
            if (ok) { b.classList.add("ok"); fb.className = "fb ok"; fb.textContent = "✓ Doğru! " + it.why + (got ? "  +" + got + " Ece-Coin" : ""); mark(); }
            else { b.classList.add("bad"); b.disabled = true; fb.className = "fb bad"; fb.textContent = "Tekrar dene. İpucu: yukarıdaki anlatımı ve seslendirmeyi gözden geçir. (Sonraki doğru yanıt yarım coin kazandırır.)"; }
            refreshHud(); check();
          };
          ob.appendChild(b);
        });
        if (r.items[k] && r.items[k].ok) { Array.prototype.forEach.call(ob.children, function (b) { if (b.textContent === it.opts[it.c]) b.classList.add("ok"); }); fb.className = "fb ok"; fb.textContent = "✓ " + it.why; mark(); }
        qs.appendChild(box);
      });
      check();
      if (s.timer && !r.done) {
        var tm = document.getElementById("tm");
        timerId = setInterval(function () {
          left = s.timer - Math.floor((Date.now() - t0) / 1000);
          if (left <= 0) { late = true; clearInterval(timerId); tm.className = "timer late"; tm.textContent = "Süre doldu! Kalan kontrolleri yarım coinle tamamla."; return; }
          tm.textContent = "Kalan süre: " + Math.floor(left / 60) + ":" + ("0" + (left % 60)).slice(-2);
        }, 500);
      } else if (s.timer) document.getElementById("tm").style.display = "none";
    }
  }

  function certificate() {
    clearInterval(timerId);
    var t = total(), date = new Date(st.finished || Date.now()).toLocaleDateString("tr-TR");
    var all = S.every(function (x, i) { return screenDone(i); });
    shell('<div class="mlabel">KAPANIŞ</div><h2>' + (all ? "Tebrikler! Görev Tamamlandı" : "Eğitim Özeti") + '</h2>' +
      '<div class="panel"><p>Bu eğitim temel kavramları ve doğru eskalasyon adımlarını tanıtır; <b>bağımsız çalışma yetkisi vermez</b>. Her yöntem için gerekli gözetimli uygulama ve yetkinlik değerlendirmesi ayrıca tamamlanır.</p></div>' +
      (all ? '<div class="cert" id="cert"><h3>ORYANTASYON TAMAMLAMA KAYDI</h3><div>Ece Kalibrasyon · Hassas Metroloji Yolculuğu</div>' +
        '<div class="big">' + esc(st.name) + '</div><div>oryantasyon eğitimini tamamlamıştır.</div>' +
        '<p><b>' + t + ' / ' + C.total + '</b> Ece-Coin · Seviye: <b>' + esc(level(t)) + '</b></p>' +
        '<p>Rozetler: ' + (C.badges.filter(badgeOn).map(function (b) { return esc(b.name); }).join(", ") || "—") + '</p><p>Tarih: ' + date + '</p>' +
        '<small>Bu belge bir öğrenme kaydıdır; gerçek denetim sonucu, yetkilendirme veya bağımsız çalışma yetkisi belgesi değildir.</small></div>'
        : '<div class="panel">Sertifika için tüm ekranları tamamlamalısın. Soldaki menüden eksik ekranları görebilirsin.</div>') +
      '<div class="actions"><button class="btn ghost" id="prev">← Geri</button>' + '<button class="btn ghost" id="dl">Sonuç dosyasını indir</button>' + (all ? '<button class="btn" id="pr">Sertifikayı yazdır / PDF kaydet</button>' : "") + '</div>' +
      '<p class="noprint" style="color:var(--mute);font-size:.9rem">Sonuç dosyasını yöneticine ilet; eğitimin tamamlandığını ve puanını gösterir.' + (scOk ? " (Sonuçların LMS'ye de otomatik kaydedildi.)" : "") + '</p>');
    document.getElementById("dl").onclick = download;
    document.getElementById("prev").onclick = function () { go(S.length - 1); };
    var p = document.getElementById("pr"); if (p) p.onclick = function () { window.print(); };
  }

  if (st.started && st.name) { st.cur = Math.min(st.cur, S.length - 1); welcome(); } else welcome();
})();
