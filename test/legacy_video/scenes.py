# Sahne verisi: (modül etiketi, başlık, ekran maddeleri, seslendirme metni)
# Seslendirme metinleri md/projerehberi.md ile uyumludur; sayılar TTS için yazıyla verilmiştir.

SCENES = [
    ("GİRİŞ", "Hassas Metroloji Yolculuğu",
     ["Ece Kalibrasyon Oryantasyon Eğitimi", "Ölçümün ve Güvenin İzinde"],
     "Merhaba! Ece Kalibrasyon ailesine hoş geldin! Laf aramızda kalmasın herkes duysun; son derece hassas, "
     "dikkat isteyen ama bir o kadar da gurur verici bir mesleğe ilk adımını attın. "
     "İki bin on yılından bu yana İstanbul Sancaktepe merkezimiz, Sakarya ve Antalya şubelerimiz, "
     "İzmir ve Muğla-Aydın temsilciliklerimizle sağlık, üretim, yapı ve teknoloji alanlarındaki kuruluşlara hizmet veriyoruz. "
     "Biz burada sadece cihaz ölçmüyoruz; ölçüm sonuçlarına duyulan güveni koruyoruz. Hazırsan ilk görevine başlayalım!"),

    ("MODÜL 1 · KALİTE KÜLTÜRÜ", "ISO 17025 ve Kalite Politikası",
     ["TÜRKAK akreditasyonu · AB-0142-K", "Tarafsızlık", "Gizlilik", "Bağımsızlık"],
     "Ece Kalibrasyon, ISO IEC on yedi bin yirmi beş standardına göre TÜRKAK tarafından akredite edilmiş bir laboratuvardır. "
     "Başarımızın temeli üç esasa dayanır. Bir: tarafsızlık. Ölçüm sonuçlarımız hiçbir ticari veya kişisel baskıdan etkilenmez. "
     "İki: gizlilik. Müşterilerimize ait tüm veriler ve kalibrasyon raporları sır niteliğindedir. "
     "Üç: bağımsızlık. Teknik karar süreçlerimizde sadece bilimsel verileri esas alırız."),

    ("MODÜL 1 · KALİTE KÜLTÜRÜ", "Akreditasyon Ne Söyler, Ne Söylemez?",
     ["Akreditasyon = yayımlanmış kapsamla sınırlı yetkinlik", "Sonuçlar hatasız olduğunun garantisi değildir",
      "Hizmet sunmak ≠ akreditasyon kapsamında olmak", "Kapsam: güncel TÜRKAK eki ve rapordan doğrulanır"],
     "Akreditasyon, laboratuvarın belirlenmiş faaliyetleri yetkinlikle yürütmek için değerlendirilmiş olduğunu gösterir. "
     "Bir hizmeti sunuyor olmamız, o hizmetin otomatik olarak akreditasyon kapsamında olduğu anlamına gelmez. "
     "Teklif ve rapor hazırlarken güncel kapsamı kontrol etmek hepimizin sorumluluğudur."),

    ("MODÜL 1 · KALİTE KÜLTÜRÜ", "Tarafsızlık, Gizlilik ve Veri Bütünlüğü",
     ["Sonucu müşteri talebine göre değiştirme", "Kayıtları iz bırakmadan değiştirme", "Başka müşterinin bilgisini paylaşma",
      "Hata gizlenmez: kaydet, bildir, süreci başlat"],
     "Teslim tarihi ne kadar sıkışık olursa olsun, sonucu değiştirmek bir seçenek değildir. "
     "Ölçümü ve kayıtları olduğu gibi koru, durumu yetkili kişiye bildir, müşteriyle yalnızca doğrulanmış bilgiyi paylaş. "
     "Hata fark edersen gizleme; kaydet ve süreci başlat. Güvenilirlik, laboratuvarın en değerli varlığıdır."),

    ("MODÜL 2 · METROLOJİ", "Kalibrasyon mı, Ayarlama mı?",
     ["Kalibrasyon: referansla karşılaştır, sapmayı ve belirsizliği belirle", "Ayarlama: göstergeyi fiziksel/yazılımsal düzelt",
      "Kalibre etmek, ayarlamak demek değildir"],
     "Günlük dilde sıkça yapılan bir hatayı çözelim: kalibrasyon bir tamir veya ayarlama işlemi değildir! "
     "Kalibrasyon; doğruluğundan emin olunan referans bir cihaz ile müşteri cihazını karşılaştırıp sapmayı ve ölçüm belirsizliğini tespit etme işlemidir. "
     "Cihazın göstergesini düzeltmek ise ayarlamadır. Bir cihaz kalibre edildiğinde ayarlanmış olmaz; sadece ne kadar doğru veya yanlış ölçtüğü tescillenmiş olur."),

    ("MODÜL 2 · METROLOJİ", "Metrolojik İzlenebilirlik Zinciri",
     ["SI birimleri", "Ulusal metroloji enstitüsü / üst seviye referans", "Laboratuvar referansı", "Müşteri cihazı"],
     "Metrolojik izlenebilirlik, bir sonucun belgelenmiş ve kesintisiz bir kalibrasyon zinciriyle bir referansa bağlanabilmesidir. "
     "Zincirdeki her adımın katkısı ve belirsizliği değerlendirilir. "
     "Doğru zincir, ilgili referans sertifikaları ve akreditasyon kapsamı üzerinden takip edilir."),

    ("MODÜL 2 · METROLOJİ", "Ölçüm Sonucu, Hata ve Düzeltme",
     ["Referans: 100,00 birim · Gösterge: 100,12 birim", "Hata = gösterge − referans = +0,12 birim",
      "Düzeltme = −0,12 birim", "Terim ve işaret: raporun açıklamasından doğrula"],
     "Bir örnek: referans değer yüz birim, cihaz yüz virgül on iki birim gösteriyor. "
     "Gösterge eksi referans, artı sıfır virgül on iki birim hata verir; düzeltme ise bunun tersidir, eksi sıfır virgül on iki. "
     "Ama sertifikada hangi terimin ve hangi işaretin kullanıldığını her zaman raporun kendi açıklamasından doğrula."),

    ("MODÜL 2 · METROLOJİ", "Ölçüm Belirsizliğine İlk Bakış",
     ["Belirsizlik ≠ hata payı ≠ tolerans", "Birleşik standart belirsizlik: u_c", "Genişletilmiş belirsizlik: U = k × u_c",
      "Örnek: √(0,10² + 0,20²) ≈ 0,224 birim"],
     "Ölçüm belirsizliği, hata payı ya da cihazın toleransı değildir. Sonuca atfedilebilecek değerlerin dağılımını anlatır. "
     "Bileşenler birleştirilir; sonra kapsama faktörüyle çarpılarak genişletilmiş belirsizlik bulunur. "
     "Kapsama faktörü her raporda yazılıdır, ezbere varsayma."),

    ("MODÜL 2 · METROLOJİ", "Kalibrasyon Sertifikası Nasıl Okunur?",
     ["Kimlik · Kapsam ve yöntem · Koşullar", "Sonuçlar ve birimler", "Belirsizlik ve izlenebilirlik", "Onay, bütünlük, revizyon"],
     "Sertifikayı okurken altı soruyu sor: Kimlik doğru mu? Kapsam ve yöntem uyuyor mu? Koşullar yeterli mi? "
     "Sonuçlar ve birimler açık mı? Belirsizlik ve izlenebilirlik yazılı mı? Onay ve revizyon bilgisi tamam mı? "
     "Unutma, kalibrasyon sertifikası kendi başına kullanıma uygundur demek değildir."),

    ("MODÜL 2 · METROLOJİ", "Uygunluk Kararı ve Tolerans",
     ["Hangi özellik ve tolerans sınırı?", "Belirsizlik nasıl hesaba katılıyor?", "Hangi karar kuralı geçerli?",
      "Sonuç: uygun · uygun değil · karar için yetersiz"],
     "Ölçülen değer tolerans içinde diye otomatik olarak uygun demek doğru değildir. "
     "Önce hangi özelliğin değerlendirildiğine, belirsizliğin nasıl hesaba katılacağına ve hangi karar kuralının geçerli olduğuna bak. "
     "Sonuç, bu kurala göre uygun, uygun değil ya da karar vermek için yetersiz olabilir."),

    ("MODÜL 3 · HİZMETLER VE İŞ AKIŞI", "Hizmetlerimiz ve Akreditasyon Kapsamı",
     ["Sıcaklık, bağıl nem, basınç", "Kütle, terazi, boyutsal · Antalya: beton ve basma test makineleri",
      "Validasyon, haritalama, bakım-onarım, eğitim", "Kapsam her işte güncel ekle eşleştirilir"],
     "Ece Kalibrasyon; sıcaklık, bağıl nem, basınç, kütle, terazi ve boyutsal kalibrasyon hizmetleri sunar. "
     "Antalya şubesinde beton ve basma test makineleri de akreditasyon kapsamındadır. "
     "Temiz oda ve taşıma aracı validasyonları, bakım-onarım ve eğitim gibi başka hizmetler de verilir. "
     "Her işte cihazı, lokasyonu, yöntemi ve akreditasyon durumunu güncel kapsamla eşleştiririz; emin olmadığımız bir aralık veya hizmet için tahminde bulunmayız."),

    ("MODÜL 3 · HİZMETLER VE İŞ AKIŞI", "Hizmet Süreci Baştan Sona",
     ["Talep → Teklif ve kapsam teyidi → Cihaz kabulü", "İş emri ve kimliklendirme → Ölçüm", "Teknik gözden geçirme → Rapor",
      "İade ve geri bildirimden öğrenme"],
     "Her iş aynı yolu izler: talebi anla, yapılabilirliği ve kapsamı teyit et, cihazı doğru tanımla, ölçümü onaylı yöntemle yürüt, "
     "sonucu gözden geçir, işi kapat ve geri bildirimden öğren. Bu zincirin her halkası, raporun güvenilirliğini oluşturur."),

    ("MODÜL 3 · HİZMETLER VE İŞ AKIŞI", "Laboratuvar mı, Yerinde mi?",
     ["Taşıma performansı etkiler mi?", "Nakil sırasında hasar riski var mı?", "Sahada referans, enerji, erişim, güvenlik sağlanır mı?",
      "Karar: teknik gözden geçirme"],
     "Laboratuvarda mı, yerinde mi? Cihaz taşınınca performansı değişebilir mi, nakil riski var mı, "
     "sahada referans, enerji, erişim ve çevre koşulları sağlanabilir mi? "
     "Bu soruların yanıtı teknik gözden geçirmeyle verilir. Yerinde hizmet her cihaz için uygun değildir."),

    ("MODÜL 3 · HİZMETLER VE İŞ AKIŞI", "Kalibrasyon, Validasyon, Bakım, Ayarlama",
     ["Kalibrasyon: ilişki + belirsizlik", "Validasyon: amaca uygunluğun kanıtı", "Bakım/onarım: işlevi korur veya arızayı giderir",
      "Ayarlama: göstergeye müdahale"],
     "Kalibrasyon, referansla cihaz arasındaki ilişkiyi ve belirsizliği belirler. "
     "Validasyon, bir sistemin veya alanın amacına uygunluğunu kabul ölçütleriyle kanıtlar. "
     "Bakım ve onarım işlevi korur veya arızayı giderir. Ayarlama ise göstergeye müdahaledir. "
     "Bunları birbirine karıştırma; emin değilsen teknik sorumluya yönlendir."),

    ("MODÜL 4 · MÜŞTERİ İLETİŞİMİ", "Çözüm Ortağı, Hassas Emanet",
     ["Müşteri → Çözüm ortağı", "Cihaz → Hassas emanet", "Saha → Güvenlik ve kalite mevzisi"],
     "Laboratuvarımıza gelen bir cihaz veya sahada test ettiğimiz bir sistem sadece metal ve elektronikten ibaret değildir. "
     "O cihaz, müşterimizin üretim kalitesine ve kararlarına doğrudan etki eder. "
     "Bu yüzden müşterilerimize çözüm ortağı, cihazlarına ise hassas emanet gözüyle bakarız. "
     "Onların sorularına doğru, anlaşılır ve bilimsel yanıtlar vermek temel ilkemizdir."),

    ("MODÜL 4 · MÜŞTERİ İLETİŞİMİ", "Müşteri Sorularına Doğru Yanıt",
     ["Teslim süresi → iş emrinden teyit et", "Limit dışı sapma → belirsizlik ve karar kuralıyla birlikte incele",
      "Yerinde hizmet → teknik ekiple yapılabilirliği teyit et", "Bilmediğini tahmin etme"],
     "Müşteri sorularında altın kural şudur: bildiğini açık söyle, bilmediğini tahmin etme. "
     "Teslim süresi, uygunluk yorumu ve yerinde hizmet gibi konularda önce kontrollü kaynağı ve teknik sorumluyu devreye al, "
     "sonra müşteriye net bir geri dönüş zamanı ver."),

    ("MODÜL 4 · MÜŞTERİ İLETİŞİMİ", "Zor Görüşmelerde İletişim",
     ["Sonuç ticari talebe göre değişmez", "Başka müşterilerin bilgisi paylaşılmaz", "Kalibrasyon ≠ ayarlama",
      "Çözüm sun: teknik inceleme, resmi süreç"],
     "Zor görüşmelerde sakin, net ve tutarlı kal. Sonucu ticari talebe göre değiştirmeyiz. Başka müşterilerin bilgisini paylaşmayız. "
     "Kalibrasyonla ayarlamayı karıştırmayız. Bunu söylerken de çözüm sun: teknik ekiple birlikte veriyi gözden geçirmeyi ve resmi süreci başlatmayı teklif et."),

    ("MODÜL 5 · ÇALIŞAN REHBERİ VE İSG", "Yıllık Ücretli İzin Hakları",
     ["1–5 yıl (5 dahil): 14 gün", "5 yıldan fazla, 15 yıldan az: 20 gün", "15 yıl ve üzeri: 26 gün",
      "Bakiye ve özel durum: İnsan Kaynakları"],
     "İş Kanunu'na göre yıllık ücretli izin süresi, bir ila beş yıl arasında, beş yıl dahil, on dört gün; "
     "beş yıldan fazla, on beş yıldan az olanlarda yirmi gün; on beş yıl ve üzerinde yirmi altı gündür. "
     "Bakiyeni ve özel durumları İnsan Kaynakları'ndan teyit et."),

    ("MODÜL 5 · ÇALIŞAN REHBERİ VE İSG", "Güvenli Çalışma ve Saha Planı",
     ["Kapsam, saha kuralları, acil durum bilgisi", "Ekipmanı gözle denetle", "Basınç / elektrik düzeneğini güvenle kur",
      "Uygun KKD · Şüphede dur ve danış"],
     "İşe başlamadan önce altı adımı uygula: kapsamı ve saha kurallarını teyit et, riskleri ve acil durum bilgisini kontrol et, "
     "ekipmanı gözle denetle, basınç ve elektrik düzeneğini güvenle kur, uygun koruyucu donanımı giy, "
     "beklenmeyen bir durumda işi durdur ve bildir. Şüphen varsa dur ve danış. Hiçbir ölçüm, bir kazaya değmez."),

    ("MODÜL 6 · FİNAL GÖREVİ", "Akreditasyon Günü",
     ["Kontrol 1: Çevre koşulları kayıtları", "Kontrol 2: Referansların geçerli izlenebilirliği", "Kontrol 3: Sonuç, belirsizlik, karar kuralı",
      "İddiayı kanıtla destekle"],
     "TÜRKAK denetçisi kapıda! Panik yok. Her kontrol noktasında iddiayı kanıtla destekle: "
     "koşul kayıtlarını, referansların izlenebilirliğini, sonuç, belirsizlik ve karar kuralını göster. "
     "Denetim, hazırlıklı ve dürüst bir laboratuvar için bir fırsattır."),

    ("MODÜL 6 · FİNAL GÖREVİ", "Final Vaka: Uygun Olmayan Sonuç",
     ["Ham veri ve kimliği doğrula", "Belirsizlik + şartname + karar kuralı", "Teknik gözden geçirme · veriyi değiştirme",
      "Sonucu tarafsız bir dille ilet"],
     "Sevkiyat yaklaşıyor, müşteri sabırsız, ama sonuç tolerans dışında görünüyor. "
     "Doğru yol bellidir: ham veriyi ve kimliği doğrula, belirsizliği ve karar kuralını birlikte değerlendir, "
     "teknik gözden geçirmeyi başlat ve sonucu tarafsız bir dille ilet. Veriyi asla değiştirme."),

    ("MODÜL 7 · YETKİNLİK", "Oryantasyondan Yetkilendirmeye",
     ["Bilgi edinme", "Gözetimli uygulama", "Yetkinlik değerlendirmesi", "Yetkilendirme · Süreklilik"],
     "Bu oryantasyonu tamamlamak, tek başına bir ölçüm yönteminde bağımsız çalışma yetkisi vermez. "
     "Yetkinlik beş aşamada kazanılır: bilgi edinme, gözetimli uygulama, yetkinlik değerlendirmesi, yetkilendirme ve süreklilik. "
     "Her aşamada eğitici ve yönetici sana destek olur."),

    ("MODÜL 8 · TERİMLER VE KAYNAKLAR", "Ortak Dilimiz ve Doğru Kaynak",
     ["Metroloji · Kalibrasyon · Ayarlama", "Doğrulama · Validasyon · Belirsizlik", "İzlenebilirlik · Akreditasyon kapsamı · Karar kuralı",
      "Emin değilsen kontrollü dokümana başvur"],
     "Son durak: terimler ve kaynaklar. Metroloji, kalibrasyon, ayarlama, doğrulama, validasyon, belirsizlik, izlenebilirlik, "
     "akreditasyon kapsamı ve karar kuralı; bunlar ortak dilimiz. "
     "Bilgiden emin olmadığında güncel kontrollü dokümana, TÜRKAK kapsam ekine veya doküman sahibine başvur."),

    ("KAPANIŞ", "Tebrikler! Görev Tamamlandı",
     ["Bu eğitim temel kavramları tanıtır", "Bağımsız çalışma yetkisi vermez", "Gözetimli uygulama ve yetkinlik değerlendirmesi ayrıca yapılır",
      "Güvenli, tarafsız ve dikkatli çalışmalar!"],
     "Tebrikler, oryantasyon öğrenme yolculuğunu tamamladın. Bu eğitim temel kavramları ve doğru eskalasyon adımlarını tanıtır; "
     "bağımsız çalışma yetkisi vermez. Her yöntem için gerekli gözetimli uygulama ve yetkinlik değerlendirmesi ayrıca tamamlanır. "
     "Laboratuvarda ve sahada güvenli, tarafsız ve dikkatli çalışmalar dileriz."),
]
