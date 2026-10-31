"""Oryantasyon programının içeriğini (content.js) ve seslendirmelerini (audio/*.mp3) üretir.

Kullanım:  python program/build_program.py [--force]
İçerik kaynağı: bu dosya + video/scenes.py (seslendirme metinleri ve ekran maddeleri).
"""
import asyncio
import hashlib
import json
import os
import sys

import edge_tts

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(ROOT, "..", "video"))
from scenes import SCENES  # noqa: E402

AUDIO = os.path.join(ROOT, "audio")
VOICE = "tr-TR-EmelNeural"
DY = ["Doğru", "Yanlış"]
SB = ["Başla", "Durdur ve danış"]


def Q(q, opts, c, why, coin=None):
    """Soru: opts içindeki c. seçenek doğru; why geri bildirim metni."""
    return {"q": q, "opts": opts, "c": c, "why": why, "coin": coin}


# (sahne indeksi, ekran no, coin, sorular, ekstra alanlar)
S = lambda idx, no, coins, items, **kw: dict(idx=idx, no=no, coins=coins, items=items, **kw)

SCREENS = [
    S(0, "1.1", 100, [Q("Eğitime başlamaya hazır mısın?", ["Evet, yolculuğa başlıyorum!"], 0, "Harika! Metroli seninle.")]),
    S(1, "1.2", 0, []),
    S(2, "1.3", 150, [
        Q("“Laboratuvar akrediteyse yaptığı her ölçüm akreditasyon kapsamındadır.”", DY, 1,
          "Akreditasyon; yayımlanmış kapsamdaki ölçüm türü, aralık, yöntem ve lokasyonla sınırlıdır."),
        Q("“Akreditasyon, her ölçüm sonucunun hatasız olduğunun garantisidir.”", DY, 1,
          "Akreditasyon yetkinlik ve kalite sistemi güvencesidir; sonuçlar yine belirsizlik ve koşullarla değerlendirilir."),
        Q("“Bir hizmetin akreditasyon kapsamında olup olmadığı güncel TÜRKAK kapsam ekinden doğrulanır.”", DY, 0,
          "Doğru. Hizmet sunmak ile akreditasyon kapsamı farklı kavramlardır."),
    ], note="Doğru/yanlış kartları: her biri 50 Ece-Coin."),
    S(3, "1.4", 150, [
        Q("Müşteri, teslim tarihine yetişmek için uygun olmayan bir ölçüm sonucunu rapordaki değerden farklı yazmanı istiyor. Ne yaparsın?",
          ["İstediği gibi düzenlerim; müşteri memnuniyeti önemli", "Reddeder, kayıtları olduğu gibi korur, kalite sorumlusuna/yöneticiye bildiririm", "Değiştirir ama not düşerim"], 1,
          "Müşteri memnuniyeti, tarafsız ve güvenilir hizmetin yerine geçmez.", 75),
        Q("Bir ölçümde kendi hatanı fark ettin. Ne yaparsın?",
          ["Kimse fark etmeden sessizce düzeltirim", "Kaydeder ve belirlenmiş uygunsuzluk sürecini başlatırım", "Rapor teslim edildikten sonra söylerim"], 1,
          "Hata gizlenmez; kayıt altına alınır ve süreç başlatılır.", 75),
    ], critical=True),
    S(4, "2.1", 150, [
        Q("“Cihazın sapmasını tescil edip rapora yazmak” hangisidir?", ["Kalibrasyon", "Ayarlama", "Validasyon"], 0,
          "Kalibrasyon sapmayı ve belirsizliği tespit eder."),
        Q("“Hatalı ölçen göstergeyi fiziksel veya yazılımsal olarak düzeltmek” hangisidir?", ["Kalibrasyon", "Ayarlama", "Validasyon"], 1,
          "Göstergeyi düzeltmek ayarlamadır."),
        Q("Bir cihaz kalibre edildi. Bu, cihazın ayarlandığı anlamına gelir mi?",
          ["Evet, kalibrasyon sırasında otomatik ayarlanır", "Hayır; kalibrasyonda yalnızca nasıl ölçtüğü tescillenir"], 1,
          "Kalibrasyon tamir veya ayarlama işlemi değildir."),
    ]),
    S(5, "2.2", 0, [], note="SI birimleri → Ulusal metroloji enstitüsü / uygun üst seviye referans → Laboratuvar referansı → Müşteri cihazı"),
    S(6, "2.3", 100, [
        Q("Referans 100,00 birim, gösterge 100,12 birim. Gösterge − referans kaç birimdir?", ["+0,12", "−0,12", "0,00"], 0,
          "Gösterge eksi referans = +0,12 birim (hata).", 50),
        Q("Bu örnekte düzeltme kaç birimdir?", ["+0,12", "−0,12", "+100,12"], 1,
          "Düzeltme, hata tahmininin işaretçe tersidir: −0,12 birim.", 50),
    ]),
    S(7, "2.4", 150, [
        Q("Ölçüm belirsizliği nedir?",
          ["Cihazın izin verilen toleransı", "Ölçüm sonucuna atfedilebilecek değerlerin dağılımını tanımlayan nicel parametre", "Teknisyenin yaptığı hata"], 1,
          "Belirsizlik hata payı veya tolerans değildir."),
        Q("Genişletilmiş belirsizlik nasıl bulunur?", ["U = k × u_c", "U = u_c + k", "U = u_c / k"], 0,
          "Birleşik standart belirsizlik, kapsama faktörü k ile çarpılır."),
        Q("Bağımsız 0,10 ve 0,20 birimlik katkıların birleşik standart belirsizliği yaklaşık kaçtır?", ["0,30", "0,224", "0,02"], 1,
          "√(0,10² + 0,20²) ≈ 0,224 birim. (Öğretim amaçlı örnek.)"),
    ]),
    S(8, "2.5", 200, [
        Q("Kalibrasyon sertifikası kendi başına “cihaz kullanıma uygundur” kararı mıdır?",
          ["Evet", "Hayır; ayrıca belirtilmedikçe uygunluk beyanı değildir"], 1, "Sertifika ile uygunluk kararı farklı şeylerdir."),
        Q("Kapsama faktörü k her zaman 2 midir?", ["Evet", "Hayır; rapor veya prosedürden okunmalıdır"], 1, "k = 2 her bağlamda otomatik değildir."),
        Q("Kalibrasyon aralığı hakkında doğru ifade hangisidir?",
          ["Tüm cihazlar için sabit bir yıldır", "Kullanıcı risk, kullanım sıklığı ve geçmiş performansa göre belirler", "Laboratuvar tek başına belirler"], 1,
          "Aralık evrensel sabit bir süre değildir."),
        Q("Aşağıdakilerden hangisi sertifikadaki “kimlik” kontrolüdür?",
          ["Cihaz seri numarasının doğruluğu", "Belirsizlik hesabı", "Referans zinciri"], 0, "Kimlik: müşteri, cihaz, model ve seri numarası."),
    ]),
    S(9, "2.6", 200, [
        Q("Ölçülen değer tolerans içinde ama belirsizlik sınıra taşıyor ve karar kuralı tanımlı değil. Ne yaparsın?",
          ["Otomatik “uygun” yazarım", "Karar kuralını şartname/sözleşme/prosedürden netleştirir, gerekirse teknik sorumluya danışırım", "Müşteriye “muhtemelen uygun” derim"], 1,
          "Belirsizliği görmezden gelip otomatik uygunluk ilan edilmez."),
        Q("Uygunluk değerlendirmesinde ilk netleştirilecek soru hangisidir?",
          ["Hangi özellik ve tolerans sınırı değerlendiriliyor?", "Müşteri kaç yıldır çalışıyor?", "Cihazın markası nedir?"], 0, "Önce değerlendirilen özellik ve sınır belirlenir."),
        Q("Kurala göre sonuç “karar vermek için yetersiz” çıkabilir mi?", ["Evet", "Hayır"], 0,
          "Uygun, uygun değil veya karar vermek için yetersiz sonuçlarından biri çıkar."),
        Q("Karar kuralı neye uygun olmalıdır?",
          ["Teknisyenin kişisel kararına", "Rapor, sözleşme, standart ve laboratuvar prosedürüne", "Müşterinin sözlü isteğine"], 1, "Kural belgelenmiş ve açık olmalıdır."),
    ]),
    S(10, "3.1 / 3.4", 100, [
        Q("Bir hizmetin akreditasyon kapsamında olduğunu nereden doğrularız?",
          ["Eski bir eğitim slaydından", "Güncel TÜRKAK kapsamı ve iş emri/rapor bilgisinden", "Cihazın markasının tanınmış olmasından"], 1,
          "Akreditasyon kapsamı güncel ve kontrollü kaynaktan doğrulanır."),
    ]),
    S(11, "3.2", 150, [
        Q("Rapor yayımlanmadan önce cihaz seri numarasının iş emriyle uyuşmadığını fark ettin. Doğru adım?",
          ["Rapor yine de yayımlanır", "Cihaz kimliği ve iş emri kontrolünde düzeltilir", "Müşteri fark ederse düzeltiriz"], 1,
          "Kimlik ve iş emri kontrolü yayımdan önce yapılır; yayımlandıysa kontrollü düzeltme prosedürü izlenir."),
        Q("Cihaz kabulünde hangi bilgiler kayıt altına alınır?",
          ["Seri numarası, aksesuarlar, hasar durumu, müşteri beyanları", "Yalnızca marka", "Yalnızca teslim saati"], 0, "Cihaz doğru tanımlanır."),
        Q("Ham veri ne zaman kaydedilir?",
          ["Ölçüm sırasında, okunaklı ve izlenebilir biçimde", "Gün sonunda hatırladığım kadarıyla", "Rapor yazarken"], 0, "Ham veri ve koşullar eşzamanlı kaydedilir."),
    ]),
    S(12, "3.3", 100, [
        Q("Bir cihazın sahada sağlanamayan çevre koşullarına ihtiyacı var. Doğru yaklaşım?",
          ["Yine de yerinde yaparım", "Teknik gözden geçirmeyle laboratuvar seçeneğini değerlendiririm", "Müşteriye tahmini sonuç veririm"], 1,
          "Karar teknik gözden geçirme ve iş güvenliği değerlendirmesiyle verilir.", 50),
        Q("“Yerinde hizmet her cihaz ve koşul için uygundur.”", DY, 1, "Yerinde hizmet otomatik olarak her cihaz için uygun değildir.", 50),
    ]),
    S(13, "3.5", 150, [
        Q("Bakım/onarım sonrasında neyin ihtiyacı ayrıca değerlendirilir?", ["Kalibrasyon", "Sertifika rengi", "Fatura türü"], 0,
          "Bakımdan sonra kalibrasyon ihtiyacı ayrıca değerlendirilir."),
        Q("Validasyon nedir?",
          ["Sistemin belirlenmiş kabul ölçütlerini karşıladığının kanıta dayalı değerlendirilmesi", "Göstergeyi düzeltmek", "Referans cihaz satın almak"], 0,
          "Validasyon amaca uygunluğu kanıtlar."),
        Q("Teknik kapsam veya akreditasyon durumu belirsiz. Ne yaparsın?",
          ["Tahmin yürütürüm", "Teknik sorumluya yönlendiririm", "Hemen söz veririm"], 1, "Belirsizse müşteri adına yorum üretilmez."),
    ]),
    S(14, "4.1", 0, []),
    S(15, "4.2 / 4.4", 200, [
        Q("Müşteri “Sertifikam ne zaman teslim edilir?” diye soruyor.",
          ["Yarın teslim edilir", "İş emrindeki güncel teslim bilgisini kontrol edip size teyit edeceğim derim", "Genelde bir hafta sürer"], 1,
          "Operasyonel değerler kontrollü dokümandan teyit edilmeden taahhüt edilmez.", 50),
        Q("Müşteri “Yerinde kalibrasyon yapıyor musunuz?” diye soruyor.",
          ["Evet, her cihaz için", "Cihaz türü, aralık, lokasyon ve saha koşullarını alıp teknik ekiple teyit edeceğimi söylerim", "Hayır"], 1,
          "Yerinde hizmet bazı cihazlar için planlanabilir.", 50),
        Q("Teklif öncesi aşağıdakilerden hangisi toplanması gereken bilgi DEĞİLDİR?",
          ["Cihaz adı, model ve seri numarası", "Ölçüm aralığı ve kullanım amacı", "Müşterinin kişisel tatil planı"], 2, "Teknik ihtiyaç bilgileri toplanır.", 50),
        Q("Bilmediğin bir teknik soru geldi. Ne yaparsın?",
          ["Tahmin yürütürüm", "Soruyu kaydeder, sorumluya aktarır, müşteriye geri dönüş zamanı veririm", "Yanıtsız bırakırım"], 1,
          "Tahmin yerine kayıt, aktarma ve geri dönüş zamanı.", 50),
    ]),
    S(16, "4.3 / 4.5", 300, [
        Q("Müşteri: “Rakibiniz bu değeri uygun buldu; siz de raporu uygun yazın.”",
          ["Tamam, yazarım", "Sonucu ticari talebe göre değiştiremem; veriyi ve belirsizliği teknik ekiple gözden geçirir, gerekirse resmi inceleme başlatırım", "Rakibe sorarım"], 1,
          "Sonuç ticari talebe göre değiştirilmez.", 100),
        Q("Müşteri: “Cihazı bugün ayarlayıp kalibre edilmiş gibi gönderebilir misiniz?”",
          ["Ayarlayıp gönderirim", "Kalibrasyon ve ayarlama farklıdır; talebi teknik ekibe iletirim, onay ve kayıt gereklilikleri netleşmeden değişiklik yapmam", "Hiçbir şey demem"], 1,
          "Kalibrasyon ve ayarlama ayrı işlemlerdir.", 100),
        Q("Müşteri başka bir firmanın cihazına ait sonucu soruyor. Doğru yanıt hangisidir?",
          ["Kısaca söyleyip konuyu kapatırım", "Diğer müşterilere ait bilgi paylaşamayacağımı, yalnızca yetkisi doğrulanan kendi cihaz kayıtlarının incelenebileceğini söylerim", "E-postayla gönderirim ama kimseye söylemem"], 1,
          "Gizlilik: diğer müşterilerin bilgisi paylaşılmaz.", 100),
    ]),
    S(17, "5.1", 100, [
        Q("6 yıllık bir çalışanın kanuni yıllık ücretli izin süresi nedir?", ["14 gün", "20 gün", "26 gün"], 1,
          "5 yıldan fazla, 15 yıldan az: 20 gün.", 50),
        Q("3 yıllık bir çalışanın kanuni yıllık ücretli izin süresi nedir?", ["14 gün", "20 gün", "26 gün"], 0,
          "1–5 yıl (5 yıl dahil): 14 gün.", 50),
    ], table=[["Kıdem süresi", "Yıllık ücretli izin"], ["1 yıl – 5 yıl (5 yıl dahil)", "14 gün"],
              ["5 yıldan fazla – 15 yıldan az", "20 gün"], ["15 yıl ve üzeri", "26 gün"]],
        note="Süreler iş günü değil gündür. 18 yaşından küçük ve 50 yaşından büyük çalışanlarda asgari süre 20 gündür. Bakiye ve özel durumlar için İnsan Kaynakları ve güncel mevzuat esas alınır."),
    S(18, "5.2 / 5.3", 400, [
        Q("Kişisel koruyucu donanım (KKD) neye göre seçilir?",
          ["Herkes için aynıdır", "Görev, risk değerlendirmesi, saha kuralları ve ilgili prosedüre göre", "Rastgele"], 1, "KKD riske göre seçilir."),
        Q("Basınç düzeneğinde emin olmadığın bir adım var. Ne yaparsın?",
          ["Devam eder, işin içinde öğrenirim", "İşe başlamadan durur, alan sorumlusuna danışırım", "Yanımdakini taklit ederim"], 1, "Emin değilsen dur ve danış."),
        Q("Saha öncesi kontrolde ölçüm kablosunda hasar görüyorsun.", SB, 1, "Hasarlı ekipman kullanılmaz.", 100),
        Q("Müşteri sahasında KKD eksik ve talimat belirsiz.", SB, 1, "Belirsiz talimat ve koruyucu eksikliğinde ölçüme başlamadan yetkili kişiye haber verilir.", 100),
    ], critical=True),
    S(19, "6.1", 500, [
        Q("Kontrol 1 · Denetçi: “Çevre koşullarının uygun olduğunu nasıl kanıtlıyorsunuz?”",
          ["Ölçüm anında eşzamanlı alınmış, prosedür sınırlarıyla karşılaştırılmış koşul kaydı", "Sonradan hatırlanarak yazılmış not", "Sözlü beyan"], 0,
          "Koşul kayıtları ölçüm anında alınmalıdır.", 150),
        Q("Kontrol 2 · Denetçi: “Referanslarınızın izlenebilirliğini gösterin.”",
          ["Geçerli kalibrasyon sertifikası ve kesintisiz referans zinciri", "Süresi geçmiş bir sertifika", "Markanın tanınmış olması"], 0,
          "İzlenebilirlik kesintisiz zincirle kanıtlanır.", 150),
        Q("Kontrol 3 · Denetçi: “Sonucun uygunluğunu neye dayandırıyorsunuz?”",
          ["Belirsizliği ve karar kuralını içeren rapor", "Yalnızca ölçülen değer", "Müşterinin onayı"], 0,
          "Sonuç, belirsizlik ve karar kuralı birlikte raporlanır.", 150),
    ], timer=180, bonus=50),
    S(20, "6.3", 400, [
        Q("Müşteri sevkiyat için “uygun” yazmanı istiyor; sonuç tolerans dışında görünüyor. İlk adım?",
          ["Ham veriyi ve cihaz kimliğini doğrularım", "Hemen uygun yazarım", "Müşteriye hak veririm"], 0, "Önce veri ve kimlik doğrulanır.", 100),
        Q("İkinci adım?",
          ["Belirsizliği, müşteri şartnamesini ve karar kuralını birlikte değerlendiririm", "Yalnızca ölçülen değere bakarım", "Rakiple kıyaslarım"], 0, "Karar kuralı belirsizlikle birlikte uygulanır.", 100),
        Q("Üçüncü adım?",
          ["Teknik gözden geçirme ve uygunsuz iş prosedürünü uygular, veriyi değiştirmem", "Veriyi küçük bir düzeltmeyle uyarlarım", "Kaydı silerim"], 0, "Veri asla değiştirilmez.", 100),
        Q("Dördüncü adım?",
          ["Sonucu açık ve tarafsız bir dille iletir, alternatif teknik adımları yetkili sorumlu üzerinden değerlendiririm", "Sonucu müşteriden saklarım", "Müşteriyi suçlarım"], 0,
          "Tarafsız iletişim ve uygun eskalasyon.", 100),
    ], critical=True),
    S(21, "7", 200, [
        Q("Oryantasyonu tamamlayan çalışan bağımsız çalışabilir mi?",
          ["Evet, her yöntemde", "Hayır; gözetimli uygulama, yetkinlik değerlendirmesi ve yetkilendirme gerekir", "Yalnızca rozet kazandıysa"], 1,
          "Oryantasyon tek başına bağımsız çalışma yetkisi vermez.", 100),
        Q("Hesap, birim, belirsizlik ve rapor kontrolleri hangi aşamada yapılır?", ["Ölçüm sonrası", "Ölçüm öncesi", "Hiçbirinde"], 0,
          "Gözetimli uygulama kontrol listesi: sonuç ve rapor kontrolleri ölçüm sonrasında.", 100),
    ], note="Yetkinlik aşamaları: Bilgi edinme → Gözetimli uygulama → Yetkinlik değerlendirmesi → Yetkilendirme → Süreklilik."),
    S(22, "8", 200, [
        Q("Karar kuralı nedir?",
          ["Uygunluk beyanında ölçüm belirsizliğinin nasıl hesaba katılacağını açıklayan kural", "Kalibrasyon aralığı", "Teslim süresi"], 0,
          "Karar kuralı belirsizliğin uygunluk beyanındaki yerini tanımlar.", 100),
        Q("Akreditasyon iddiası ve ölçüm aralığı için hangi kaynağa bakılır?",
          ["Güncel TÜRKAK kapsam eki ve geçerli şirket prosedürü", "Eski bir slayt", "Hafızam"], 0,
          "Güncel, kontrollü kaynak esastır.", 100),
    ]),
    S(23, "6.2", 0, []),
]

LEVELS = [[0, "Çırak Teknisyen"], [1001, "Kalibrasyon Uzmanı"], [2501, "Akredite Baş Metrolojist"]]
BADGES = [
    {"id": "isg", "name": "İSG & Temiz Oda Hijyen Şampiyonu", "screens": [18]},
    {"id": "kutle", "name": "Hassas Tartı & Kütle Ustası", "screens": [6, 7, 8]},
    {"id": "termal", "name": "Termal Haritalama Danışmanı", "screens": [12, 13]},
    {"id": "etik", "name": "Akreditasyon ve Etik Lideri", "screens": [2, 3, 20]},
]


def build():
    screens, total = [], 0
    for n, s in enumerate(SCREENS):
        module, title, bullets, voice = SCENES[s["idx"]]
        if s["no"] == "4.2 / 4.4":
            voice += " İyi bir teklif, iyi sorularla başlar. Cihazı, ölçüm aralığını, toleransı, lokasyonu ve akreditasyon beklentisini baştan netleştirirsen hem müşteri hem laboratuvar zaman kazanır."
        items = s["items"]
        if items:
            per = s["coins"] - s.get("bonus", 0)
            auto = [i for i in items if i["coin"] is None]
            fixed = sum(i["coin"] for i in items if i["coin"] is not None)
            for i in auto:
                i["coin"] = (per - fixed) // len(auto)
            assert sum(i["coin"] for i in items) == per, (s["no"], per)
        total += s["coins"]
        screens.append({
            "id": f"s{n:02d}", "no": s["no"], "module": module, "title": title, "bullets": bullets,
            "voice": voice, "audio": f"audio/s{n:02d}.mp3", "items": items, "coins": s["coins"],
            "note": s.get("note", ""), "table": s.get("table"), "critical": s.get("critical", False),
            "timer": s.get("timer", 0), "bonus": s.get("bonus", 0),
        })
    assert total == 4000, total
    data = {"screens": screens, "levels": LEVELS, "badges": BADGES, "total": total}
    with open(os.path.join(ROOT, "content.js"), "w", encoding="utf-8") as f:
        f.write("window.CONTENT = " + json.dumps(data, ensure_ascii=False, indent=1) + ";\n")
    return screens


async def tts(screens, force):
    os.makedirs(AUDIO, exist_ok=True)
    for sc in screens:
        path = os.path.join(ROOT, sc["audio"])
        stamp = path + ".md5"
        h = hashlib.md5((VOICE + sc["voice"]).encode()).hexdigest()
        if not force and os.path.exists(path) and os.path.exists(stamp) and open(stamp).read() == h:
            continue
        await edge_tts.Communicate(sc["voice"], VOICE, rate="-5%").save(path)
        open(stamp, "w").write(h)
        print("ses:", sc["id"], sc["title"].encode("ascii", "replace").decode())


if __name__ == "__main__":
    scr = build()
    asyncio.run(tts(scr, "--force" in sys.argv))
    print(f"Tamam: {len(scr)} ekran, toplam {sum(s['coins'] for s in scr)} Ece-Coin")
