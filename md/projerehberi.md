# ECE KALİBRASYON - İNTERAKTİF E-ÖĞRENME ORYANTASYON EĞİTİMİ
## "Hassas Metroloji Yolculuğu: Ölçümün ve Güvenin İzinde"
### Kapsamlı Tasarım, Konu Anlatımı, Seslendirme Scriptleri ve Oyunlaştırma Mimari Dokümanı

---

## İÇİNDEKİLER

1. [PROJE GENEL BAKIŞI VE KURUMSAL KİMLİK](#bolum-1)
2. [OYUNLAŞTIRMA (GAMIFICATION) VE HİKAYE MİMARİSİ](#bolum-2)
3. [MODÜL 1: AİLEYE HOŞ GELDİN VE KALİTE KÜLTÜRÜ](#modul-1)
4. [MODÜL 2: METROLOJİ, KALİBRASYON VE BELİRSİZLİK](#modul-2)
5. [MODÜL 3: HİZMETLER, AKREDİTASYON VE İŞ AKIŞI](#modul-3)
6. [MODÜL 4: MÜŞTERİ İLETİŞİMİ VE MESLEKİ ETİK](#modul-4)
7. [MODÜL 5: ÇALIŞAN REHBERİ, İSG VE SAHA GÜVENLİĞİ](#modul-5)
8. [MODÜL 6: UYGULAMALI FİNAL GÖREVİ](#modul-6)
9. [MODÜL 7: İŞBAŞI ÖĞRENME VE YETKİNLİK](#modul-7)
10. [MODÜL 8: TERİMLER, KAYNAKLAR VE BİLGİ GÜNCELLEME](#modul-8)
11. [LMS YÖNETİMİ, SCORM VE TEKNİK UYARLAMA](#lms)

---

<a id="bolum-1"></a>

## 1. PROJE GENEL BAKIŞI VE KURUMSAL KİMLİK

### 1.1 Ece Kalibrasyon Kurumsal Profili
* **Ticari unvan:** Ece Kalibrasyon Validasyon Ölçüm Hizmetleri ve Otomotiv Sanayi Ticaret Limited Şirketi.
* **Kuruluş:** 2010, İstanbul.
* **Merkez laboratuvar:** Meclis Mah. Atatürk Cd. No: 51/2-3, 34785 Sancaktepe / İstanbul.
* **Şubeler:** Sakarya (Adapazarı) ve Antalya (Muratpaşa).
* **Temsilcilikler:** Muğla–Aydın ve İzmir (Karşıyaka).
* **Akreditasyon:** TÜRKAK tarafından TS EN ISO/IEC 17025:2017 standardına göre akredite kalibrasyon laboratuvarı; numara `AB-0142-K`. İlk akreditasyon tarihi 15.07.2015, paylaşılan geçerlilik tarihi 16.11.2027'dir.
* **Akreditasyon kapsamı:** Sıcaklık, bağıl nem, basınç, kütle, terazi ve boyutsal kalibrasyonlar; Antalya şubesinde beton ve basma test makineleri. Güncel ve bağlayıcı kapsam için [TÜRKAK kapsam kaydı](https://ecekalibrasyon.com.tr/akreditasyon-kapsami) kontrol edilmelidir.
* **Diğer hizmetler:** Yazılım, ilaç taşıma aracı ve kutusu, sıcaklık-nem haritalaması ve temiz oda validasyonları; ölçüm cihazı bakım ve tamiri; kalibrasyon ve metroloji eğitimi. Bir hizmetin sunuluyor olması tek başına o hizmetin akreditasyon kapsamında olduğu anlamına gelmez.
* **Uluslararası tanınma:** TÜRKAK'ın EA ve ILAC karşılıklı tanıma düzenlemeleri, akreditasyon kapsamındaki sonuçların tanınmasını destekler. Sertifikanın kapsamını ve kullanım koşullarını her zaman rapor ve güncel akreditasyon eki üzerinden doğrula.

### 1.2 Misyon ve Vizyon
* **Misyon:** Sağlık, teknoloji, yapı, üretim, satış ve Ar-Ge gibi alanlarda faaliyet gösteren kuruluşlara; eğitimli kadroyla, standartlara ve prosedürlere uygun hizmet vermek ve müşteri memnuniyetini yüksek tutmak.
* **Vizyon:** Türkiye'de ve dünyada güvenilirliği ve ölçüm doğruluğuyla öne çıkan bir kalibrasyon laboratuvarı olmak; eğitimlerle kalibrasyon bilincini yaygınlaştırmak ve gençlere iş olanakları sağlamak.

### 1.3 Kurumsal Bilginin Kullanımı
Bu eğitimde adresler, hizmetler, kapsam ve geçerlilik tarihleri kurumsal kaynaklardan alınmıştır. Teklif, müşteri yanıtı veya teknik rapor hazırlarken ezberlenmiş eğitim metni yerine güncel akreditasyon kapsamını, şirket prosedürlerini ve yetkili birimlerin duyurularını kontrol et. Özellikle ölçüm aralıkları, teslim süreleri, çalışma koşulları ve personel hakları gibi operasyonel değerler kontrollü dokümandan teyit edilmeden taahhüt edilmemelidir.

---

<a id="bolum-2"></a>

## 2. OYUNLAŞTIRMA (GAMIFICATION) VE HİKAYE MİMARİSİ

Eğitim, düz metin aktarımı yerine çalışanın aktif rol aldığı bir simülasyon olarak tasarlanmıştır.

### 2.1 Oyunlaştırma Bileşenleri
* **Para Birimi:** `Ece-Coin` (Her doğru soru ve etkileşimli görevde kazanılır. Toplam bütçe: $4000\text{ Ece-Coin}$).
* **Rehber Avatar (Metroli):** Uzman, yardımsever ve samimi bir kıdemli metroloji mühendisi.
* **Oyuncu Profil Seviyeleri:**
  * $0 - 1000\text{ Ece-Coin}$: Çırak Teknisyen
  * $1001 - 2500\text{ Ece-Coin}$: Kalibrasyon Uzmanı
  * $2501 - 4000\text{ Ece-Coin}$: Akredite Baş Metrolojist
* **Kazanılabilir Dijital Rozetler:**
  * *İSG & Temiz Oda Hijyen Şampiyonu*
  * *Hassas Tartı & Kütle Ustası*
  * *Termal Haritalama Danışmanı*
  * *Akreditasyon ve Etik Lideri*

### 2.2 Ece-Coin Dağılım Tablosu (Toplam 4000)

| Bölüm | Kazanım | Ece-Coin |
|---|---|---|
| Modül 1 | 1.1 başlangıç (100), 1.3 üç kart (3×50), 1.4 senaryo (150) | 400 |
| Modül 2 | 2.1 (150), 2.3 (100), 2.4 (150), 2.5 (200), 2.6 (200) | 800 |
| Modül 3 | 3.2 (150), 3.3 (100), 3.4 (100), 3.5 (150) | 500 |
| Modül 4 | 4.2 (100), 4.3 (200), 4.4 (100), 4.5 (100) | 500 |
| Modül 5 | 5.1 (100), 5.2 (200), 5.3 (200) | 500 |
| Modül 6 | 6.1 simülasyon (500), 6.3 final vaka (400) | 900 |
| Modül 7 | 7.2 kontrol listesi eşleştirme | 200 |
| Modül 8 | 8.1 sözlük eşleştirme (100), 8.2 kaynak kontrolü (100) | 200 |
| **Toplam** | | **4000** |

* **Kural:** Yanlış yanıtta coin düşülmez; ilgili öğrenme kartı tekrar gösterilir ve ikinci denemede coin yarıya iner.
* **Kritik senaryolar (1.4, 5.3, 6.3):** Coin kazanmak yeterli değildir; kritik adımların tamamı doğru olmadan modül tamamlanmış sayılmaz.

### 2.3 Rozet Kazanma Koşulları

| Rozet | Koşul |
|---|---|
| İSG & Temiz Oda Hijyen Şampiyonu | 5.2 ve 5.3'ün tüm adımlarının doğru tamamlanması |
| Hassas Tartı & Kütle Ustası | 2.3, 2.4 ve 2.5'in ilk denemede doğru tamamlanması (ölçüm sonucu, belirsizlik, sertifika okuma) |
| Termal Haritalama Danışmanı | 3.3 ve 3.5'in doğru tamamlanması (saha/laboratuvar kararı, validasyon ayrımı) |
| Akreditasyon ve Etik Lideri | 1.3, 1.4 ve 6.3'ün doğru tamamlanması |

> Not: Rozet adları motivasyon amaçlıdır; eğitim, adı geçen alanlarda yetkinlik veya yetkilendirme sağlamaz (bkz. Modül 7).

---

<a id="modul-1"></a>

## MODÜL 1: AİLEYE HOŞ GELDİN VE KALİTE KÜLTÜRÜ

### Ekran 1.1: Karşılama ve Samimi Giriş
* **Ekran Türü:** Video / Animasyon & Karşılama Popup'ı
* **Görsel Tasarım:** Şehrin ortasında yükselen modern Ece Kalibrasyon Akredite Laboratuvar binası. Ön planda neşeli Metroli avatarı.

```text
+-------------------------------------------------------------------+
|  ECE KALİBRASYON ORYANTASYON EĞİTİMİ                             |
|  Bölüm 1: Metroloji Dünyasına Yolculuk                            |
+-------------------------------------------------------------------+
|                                                                   |
|   Laf aramızda kalmasın herkes duysun;                             |
|   zor ama gurur verici bir mesleğe ilk adımını attın!             |
|                                                                   |
|   [ YOLCULUĞA BAŞLA (+100 Ece-Coin) ]                             |
+-------------------------------------------------------------------+
```

* **Seslendirme (Voice-Over Transkripti):**
  > *"Merhaba! Ece Kalibrasyon ailesine hoş geldin! Laf aramızda kalmasın herkes duysun; son derece hassas, dikkat isteyen ama bir o kadar da gurur verici bir mesleğe ilk adımını attın.
  > 2010 yılından bu yana İstanbul Sancaktepe merkezimiz, Sakarya ve Antalya şubelerimiz, İzmir ve Muğla-Aydın temsilciliklerimizle sağlık, üretim, yapı ve teknoloji alanlarındaki kuruluşlara hizmet veriyoruz.
  > Biz burada sadece cihaz ölçmüyoruz; ölçüm sonuçlarına duyulan güveni koruyoruz. Hazırsan ilk görevine başlayalım!"*

---

### Ekran 1.2: ISO 17025 Standartları ve Kalite Politikası
* **Ekran Türü:** Etkileşimli Kart Açma
* **Görsel Tasarım:** TÜRKAK `AB-0142-K` akreditasyon logosu ve 3 ana kalite sütunu.

```text
                       [ TS EN ISO/IEC 17025 ]
                                  |
        +-------------------------+-------------------------+
        |                         |                         |
  [ TARAFSIZLIK ]           [ GİZLİLİK ]            [ BAĞIMSIZLIK ]
```

* **Seslendirme (Voice-Over Transkripti):**
  > *"Ece Kalibrasyon, TS EN ISO/IEC 17025:2017 standardına göre TÜRKAK tarafından akredite edilmiş bir laboratuvardır. Başarımızın temeli 3 esasa dayanır:
  > **1. Tarafsızlık:** Ölçüm sonuçlarımız hiçbir ticari veya kişisel baskıdan etkilenmez.
  > **2. Gizlilik:** Müşterilerimize ait tüm veriler ve kalibrasyon raporları sır niteliğindedir.
  > **3. Bağımsızlık:** Teknik karar alma süreçlerimizde sadece bilimsel verileri esas alırız."*

### Ekran 1.3: Akreditasyon Ne Söyler, Ne Söylemez?
* **Ekran Türü:** Doğru / yanlış kartları
* **Öğrenme hedefi:** Akreditasyonun laboratuvarın yetkinliğine ve tanımlı kapsama ilişkin olduğunu; her cihazı veya her hizmeti otomatik olarak kapsamadığını açıklamak.

**Kart 1:** “Laboratuvar akrediteyse yaptığı her ölçüm akreditasyon kapsamındadır.”
* **Yanıt:** Yanlış. Akreditasyon, yayımlanmış kapsamda belirtilen ölçüm türü, aralık, yöntem ve ilgili lokasyonla sınırlıdır.

**Kart 2:** “Akreditasyon, her bir ölçüm sonucunun hatasız olduğu garantisidir.”
* **Yanıt:** Yanlış. Yetkinlik ve kalite sistemi için güvence sağlar; sonuçlar yine belirsizlik, yöntem, koşullar ve olası hata kaynaklarıyla değerlendirilir.

**Kart 3:** “Şirketin sunduğu her validasyon veya bakım hizmeti akredite hizmettir.”
* **Yanıt:** Yanlış. Hizmet sunumu ile akreditasyon kapsamı farklı kavramlardır. Kapsam iddiası, güncel TÜRKAK eki ve ilgili rapor üzerinden doğrulanır.

* **Seslendirme:**
  > *"Akreditasyon, laboratuvarın belirlenmiş faaliyetleri yetkinlikle yürütmek için değerlendirilmiş olduğunu gösterir. Bir hizmeti sunuyor olmamız, o hizmetin otomatik olarak akreditasyon kapsamında olduğu anlamına gelmez. Teklif ve rapor hazırlarken güncel kapsamı kontrol etmek hepimizin sorumluluğudur."*

### Ekran 1.4: Tarafsızlık, Gizlilik ve Veri Bütünlüğü
* **Ekran Türü:** Senaryo seçimi

**Senaryo:** Bir müşteri, teslim tarihine yetişmek için ölçüm sonucu uygun değilken rapordaki sonucu değiştirmeyi istiyor.
* **Doğru yaklaşım:** Sonucu değiştirmeyi reddet; ölçümü ve kayıtları olduğu gibi koru; durumu yetkili yöneticiye/kalite sorumlusuna bildir; müşteriyle yalnızca doğrulanmış teknik bilgiyi paylaş.

**Günlük davranış örnekleri:**
* Gerçekleşmeyen bir ölçümü yapılmış gibi kaydetme; kayıtları geriye dönük ve iz bırakmadan değiştirme.
* Müşteri cihazı, ölçüm sonucu, üretim süreci ve raporunu yetkisiz kişilerle paylaşma.
* Hediye, ticari baskı, yakınlık ilişkisi veya kişisel çıkar tarafsızlığı etkileyebilecekse işi tek başına sürdürme; çıkar çatışmasını bildir.
* Hata veya uygunsuzluk fark edildiğinde gizleme; kayıt altına al ve belirlenmiş süreci başlat.

* **Mini kontrol:** “Müşterinin istediği şekilde raporu düzenlemek müşteri memnuniyetidir.” **Yanlış.** Müşteri memnuniyeti, tarafsız ve güvenilir hizmetin yerine geçmez.

* **Seslendirme:**
  > *"Teslim tarihi ne kadar sıkışık olursa olsun, sonucu değiştirmek bir seçenek değildir. Ölçümü ve kayıtları olduğu gibi koru, durumu yetkili kişiye bildir, müşteriyle yalnızca doğrulanmış bilgiyi paylaş. Hata fark edersen gizleme; kaydet ve süreci başlat. Güvenilirlik, laboratuvarın en değerli varlığıdır."*

---

<a id="modul-2"></a>

## MODÜL 2: METROLOJİ, KALİBRASYON VE BELİRSİZLİK

### Ekran 2.1: Kalibrasyon Nedir, Ne Değildir? (Hayati Ayrım)
* **Ekran Türü:** Sürükle-Bırak (Drag and Drop) Simülasyonu
* **Görsel Tasarım:** Bir tarafta rapora sapma yazan teknisyen, diğer tarafta tornavidayla cihazı sıfırlayan teknisyen.

```text
  [ KAVRAM KARTLARI ]                     [ HEDEF KUTULAR ]
  +---------------------------------+     +---------------------------------+
  | 1. Cihazın sapmasını tescil edip| --> | KALİBRASYON (Calibration)       |
  |    rapora yazmak                |     +---------------------------------+
  +---------------------------------+
  | 2. Hatalı ölçen göstergeyi      | --> | AYARLAMA (Adjustment)           |
  |    fiziksel/yazılımsal düzeltmek|     +---------------------------------+
```

* **Seslendirme (Voice-Over Transkripti):**
  > *"Günlük dilde sıkça yapılan bir hatayı çözelim: **Kalibrasyon bir tamir veya ayarlama işlemi değildir!**
  > Kalibrasyon; doğruluğundan emin olunan referans bir cihaz ile müşteri cihazını karşılaştırıp sapmayı ve ölçüm belirsizliğini tespit etme işlemidir. Cihazın göstergesini düzeltmek ise 'Ayarlama'dır. Bir cihaz kalibre edildiğinde ayarlanmış olmaz; sadece ne kadar doğru veya yanlış ölçtüğü tescillenmiş olur."*

---

### Ekran 2.2: Metrolojik İzlenebilirlik Zinciri
* **Ekran Türü:** İnteraktif Piramit
* **Görsel Tasarım:** SI Birimlerinden başlayıp Müşteri Cihazına uzanan hiyerarşi piramidi.

$$\text{SI birimleri} \longrightarrow \text{Ulusal metroloji enstitüsü / uygun üst seviye referans} \longrightarrow \text{Laboratuvar referansı} \longrightarrow \text{Müşteri cihazı}$$

* **Seslendirme (Voice-Over Transkripti):**
  > *"Metrolojik izlenebilirlik, bir sonucun belgelenmiş ve kesintisiz bir kalibrasyon zinciriyle bir referansa bağlanabilmesidir. Zincirdeki her adımın katkısı ve belirsizliği değerlendirilir. TÜRKAK laboratuvarları akredite eder; izlenebilirlik zincirindeki üst seviye kalibrasyon hizmetini veren kuruluşla aynı rolü üstlenmez. Bu nedenle doğru zincir, ilgili referans sertifikaları ve akreditasyon kapsamı üzerinden takip edilir."*

### Ekran 2.3: Ölçüm Sonucu, Hata ve Düzeltme
* **Ekran Türü:** Örnek veri kartı

**Örnek (temsili):** Referans değer `100,00 birim`, cihaz göstergesi `100,12 birim` olsun.
* Gösterge hatası, kullanılan tanıma göre gösterge ile referans değer arasındaki farktır. Bu örnekte gösterge eksi referans `+0,12 birim` olur.
* Düzeltme, bu hata tahmininin işaretçe tersidir: `-0,12 birim`.
* Sertifikada “hata”, “düzeltme”, “sapma” veya başka bir terim kullanılabilir. Terimi ve işaret konvansiyonunu raporun kendi açıklamasından doğrula; alışkanlığa dayanarak yorumlama.

**Önemli ayrım:** Ölçüm hatası tek bir ölçüm için bilinemez; çünkü referans değerin de belirsizliği vardır. Sertifikadaki ölçüm sonucu ve belirsizlik, cihaz performansının değerlendirilmesine yardımcı olur; tüm kullanım koşullarını tek başına temsil etmez.

* **Seslendirme:**
  > *"Bir örnek: referans değer yüz birim, cihaz yüz virgül on iki birim gösteriyor. Gösterge eksi referans, artı sıfır virgül on iki birim hata verir; düzeltme ise bunun tersidir, eksi sıfır virgül on iki. Ama sertifikada hangi terimin ve hangi işaretin kullanıldığını her zaman raporun kendi açıklamasından doğrula."*
* **Etkileşim:** Katılımcı hata ve düzeltme değerlerini sürükleyerek doğru kutulara yerleştirir.

### Ekran 2.4: Ölçüm Belirsizliğine İlk Bakış
* **Ekran Türü:** Katkı bileşenlerini birleştirme etkileşimi

Ölçüm belirsizliği, ölçüm sonucuna atfedilebilecek değerlerin dağılımını tanımlayan nicel bir parametredir. Tek bir “hata payı” veya cihazın izin verilen toleransı değildir.

* **Standart belirsizlik:** Bir bileşenin standart sapma biçiminde ifade edilmesi.
* **Birleşik standart belirsizlik (`u_c`):** Ölçüm modeline göre belirsizlik bileşenlerinin birleştirilmiş hali. Bağımsız bileşenlerin kareleri toplamının karekökü sık kullanılan bir örnektir; korelasyon varsa model bunu da hesaba katmalıdır.
* **Genişletilmiş belirsizlik (`U`):** Birleşik standart belirsizliğin kapsama faktörü `k` ile çarpımıdır: `U = k × u_c`. `k` ve kapsama bilgisi rapor/prosedürden okunmalıdır; `k = 2` her bağlamda otomatik bir garanti değildir.

**Temsili hesap:** Bağımsız olduğu varsayılan `0,10` ve `0,20` birimlik iki standart belirsizlik katkısı için `u_c = √(0,10² + 0,20²) ≈ 0,224 birim`. Bu yalnızca kareler toplamı yaklaşımını öğretmek için hazırlanmış örnektir; gerçek sertifika hesabı değildir.

* **Seslendirme:**
  > *"Ölçüm belirsizliği, hata payı ya da cihazın toleransı değildir. Sonuca atfedilebilecek değerlerin dağılımını anlatır. Bileşenler birleştirilir; sonra kapsama faktörüyle çarpılarak genişletilmiş belirsizlik bulunur. Kapsama faktörü her raporda yazılıdır, ezbere varsayma."*
* **Etkileşim:** Katılımcı 0,10 ve 0,20 birimlik iki katkıyı birleştirir; doğru sonuç yaklaşık 0,224 birimdir.

### Ekran 2.5: Kalibrasyon Sertifikası Nasıl Okunur?
* **Ekran Türü:** Sertifika üzerinde işaretleme

Bir raporu incelerken sırayla şunları kontrol et:
1. **Kimlik:** Müşteri, cihaz, üretici/model, seri numarası ve varsa cihazın bulunduğu yer doğru mu?
2. **Kapsam ve yöntem:** Yapılan iş talep edilen ölçüm noktaları, aralık ve yöntemle uyuşuyor mu? Akreditasyon iddiası varsa kapsamla eşleşiyor mu?
3. **Koşullar:** Sonucu etkileyebilecek çevre koşulları ve raporlanan bilgiler yeterli mi?
4. **Sonuçlar:** Referans değeri, cihaz göstergesi, hata/düzeltme tanımı, birim ve çözünürlük açık mı?
5. **Belirsizlik ve izlenebilirlik:** Belirsizlik, kapsama faktörü ve referans zinciri raporda belirtilmiş mi?
6. **Yetkilendirme ve bütünlük:** Raporun onayı, sayfa bütünlüğü ve revizyon bilgisi prosedüre uygun mu?

**Dikkat:** Kalibrasyon sertifikası, ayrıca belirtilmedikçe cihazın “kullanıma uygundur” kararı veya uygunluk beyanı ile aynı şey değildir. Kalibrasyon aralığı da her cihaz için sabit ve evrensel bir süre değildir; kullanıcı risk, kullanım sıklığı, geçmiş performans ve kalite sistemi gerekliliklerine göre belirlemelidir.

* **Seslendirme:**
  > *"Sertifikayı okurken altı soruyu sor: Kimlik doğru mu? Kapsam ve yöntem uyuyor mu? Koşullar yeterli mi? Sonuçlar ve birimler açık mı? Belirsizlik ve izlenebilirlik yazılı mı? Onay ve revizyon bilgisi tamam mı? Unutma, kalibrasyon sertifikası kendi başına 'kullanıma uygundur' demek değildir."*

### Ekran 2.6: Uygunluk Kararı ve Tolerans
* **Ekran Türü:** İki sonuçlu karar simülasyonu

Bir ölçüm sonucunu teknik şartnameyle karşılaştırırken aşağıdakileri netleştir:
* Hangi özellik ve tolerans sınırı değerlendiriliyor?
* Belirsizlik hesaba katılacak mı, nasıl hesaba katılacak?
* Hangi karar kuralı uygulanıyor ve bu kural müşteriyle/şartnamede nasıl belirlenmiş?
* Sonuç, kullanılan kural uyarınca uygun, uygun değil veya karar vermek için yetersiz mi?

**Kural:** Belirsizliği görmezden gelip yalnızca ölçülen değer toleransın içinde diye otomatik uygunluk ilan etme. Karar kuralı rapor, sözleşme, standart ve laboratuvar prosedürüne uygun olmalı; müşteri iletişimi de bu kuralı açıkça belirtmelidir.

* **Seslendirme:**
  > *"Ölçülen değer tolerans içinde diye otomatik olarak uygun demek doğru değildir. Önce hangi özelliğin değerlendirildiğine, belirsizliğin nasıl hesaba katılacağına ve hangi karar kuralının geçerli olduğuna bak. Sonuç, bu kurala göre uygun, uygun değil ya da karar vermek için yetersiz olabilir."*
* **Etkileşim:** İki örnek ölçüm, belirsiz karar kuralıyla birlikte sunulur; katılımcı her biri için "uygun / uygun değil / karar için yetersiz" seçer.

---

<a id="modul-3"></a>

## MODÜL 3: HİZMETLER, AKREDİTASYON VE İŞ AKIŞI

### Ekran 3.1: İnteraktif Çift Sayfalı Cihaz Kataloğu
* **Ekran Türü:** 3D Kitap Çevirme Etkileşimi (Visual Showcase)
* **Görsel Tasarım:** Sol tarafta Laboratuvar Kalibrasyonları, sağ tarafta Saha Validasyonları ve Biyomedikal Cihazlar.

```text
+------------------------------------------+------------------------------------------+
| ECE KALİBRASYON LABORATUVAR KAPSAMI      | SAHA VALİDASYON VE BİYOMEDİKAL           |
+------------------------------------------+------------------------------------------+
| Sıcaklık ve bağıl nem kalibrasyonu       | Biyomedikal cihaz hizmetleri              |
|    (Kapsam ve aralık güncel ekte kontrol)|    (Hizmet/yöntem iş emrinden doğrulanır) |
|                                          |                                          |
| Basınç kalibrasyonu                      | Temiz oda validasyon hizmetleri           |
|    (Kapsam ve aralık güncel ekte kontrol)|    (Plan ve protokol kapsamı doğrulanır)  |
|                                          |                                          |
| Kütle, terazi ve boyutsal kalibrasyon    | Taşıma aracı/kutusu ve haritalama         |
|    (Antalya: beton/basma test makineleri)|    (Hizmet kapsamı iş emrinden doğrulanır)|
+------------------------------------------+------------------------------------------+
```

* **Seslendirme (Voice-Over Transkripti):**
  > *"Ece Kalibrasyon; sıcaklık, bağıl nem, basınç, kütle, terazi ve boyutsal kalibrasyon hizmetleri sunar. Paylaşılan kurum bilgisine göre Antalya şubesinde beton ve basma test makineleri de akreditasyon kapsamındadır. Temiz oda ve taşıma aracı validasyonları, bakım-onarım ve eğitim gibi başka hizmetler de verilir. Her işte cihazı, lokasyonu, yöntemi ve akreditasyon durumunu güncel kapsamla eşleştiririz; emin olmadığımız bir aralık veya hizmet için tahminde bulunmayız."*

---

### Ekran 3.2: Hizmet Süreci Baştan Sona
* **Ekran Türü:** Akış şeması ve karar noktaları

`Talep alma → Teknik gözden geçirme → Teklif ve kapsam teyidi → Cihaz kabulü / saha planı → İş emri ve kimliklendirme → Kalibrasyon/validasyon → Teknik gözden geçirme → Raporlama → İade ve takip`

1. **Talebi anla:** Cihazın neyi ölçtüğünü, aralık ve noktaları, kullanım amacını, toleransını, lokasyonunu ve istenen hizmeti sor.
2. **Yapılabilirliği teyit et:** Yöntem, referans, personel yetkinliği, kapasite, çevre şartları, süre ve akreditasyon kapsamını kontrol et.
3. **Cihazı doğru tanımla:** Seri numarası, aksesuarlar, arıza/hasar durumu, teslim alınan parçalar ve müşteri beyanları kayıt altına alınır.
4. **Ölçümü kontrollü yürüt:** Onaylı yöntem/prosedürü ve geçerli ekipmanı kullan; ham veriyi ve gerekli koşulları eşzamanlı kaydet.
5. **Sonucu gözden geçir:** Hesapları, birimleri, cihaz kimliğini, belirsizliği, kapsamı ve rapor bütünlüğünü kontrol et.
6. **Kapat ve öğren:** Cihazı güvenle iade et; uygunsuzluk veya müşteri geri bildirimi varsa kayıt ve iyileştirme sürecini başlat.

* **Seslendirme:**
  > *"Her iş aynı yolu izler: talebi anla, yapılabilirliği ve kapsamı teyit et, cihazı doğru tanımla, ölçümü onaylı yöntemle yürüt, sonucu gözden geçir, işi kapat ve geri bildirimden öğren. Bu zincirin her halkası, raporun güvenilirliğini oluşturur."*
* **Etkileşim:** Katılımcı “cihazın seri numarası raporda uyuşmuyor” kartını doğru adıma sürükler. Beklenen yanıt: rapor yayımlanmadan önce kimlik ve iş emri kontrolünde fark edilir; yayımlandıysa kontrollü düzeltme/yeniden yayımlama prosedürü izlenir.

### Ekran 3.3: Laboratuvar Kalibrasyonu mu, Yerinde Hizmet mi?
* **Ekran Türü:** Karar ağacı

* Cihazın taşınması performansını etkileyebilir mi?
* Laboratuvara nakil sırasında hasar veya ayar değişikliği riski var mı?
* Müşteri sahasında gerekli referans, enerji, erişim, güvenlik ve çevresel koşullar sağlanabiliyor mu?
* Sahadaki koşullar ölçüm belirsizliğini veya yöntemin uygulanmasını etkiliyor mu?

**Öğrenme notu:** Yerinde hizmet her cihaz ve koşul için otomatik olarak uygun değildir. Karar teknik gözden geçirme, müşteri ihtiyacı, yöntem ve iş güvenliği değerlendirmesiyle verilir.

* **Seslendirme:**
  > *"Laboratuvarda mı, yerinde mi? Cihaz taşınınca performansı değişebilir mi, nakil riski var mı, sahada referans, enerji, erişim ve çevre koşulları sağlanabilir mi? Bu soruların yanıtı teknik gözden geçirmeyle verilir. Yerinde hizmet her cihaz için uygun değildir."*
* **Etkileşim:** Üç cihaz kartı karar ağacında "laboratuvar" veya "yerinde" yoluna yönlendirilir.

### Ekran 3.4: Pekiştirme Quizi (Micro-Quiz)
* **Ekran Türü:** İnteraktif Soru Ekranı & Maskot Animasyonu

```text
+-------------------------------------------------------------------+
|  PEKİŞTİRME SORUSU                                                |
+-------------------------------------------------------------------+
|  Soru: Bir hizmetin akreditasyon kapsamında olduğunu nereden     |
|  doğrularız?                                                     |
|                                                                   |
|  ( ) A) Eski bir eğitim slaydından                               |
|  (*) B) Güncel TÜRKAK kapsamı ve iş emri/rapor bilgisinden       |
|  ( ) C) Cihazın markasının tanınmış olmasından                    |
|                                                                   |
|  [ YANITLA ]                                                      |
+-------------------------------------------------------------------+
```

* **Doğru Yanıt Bildirimi (Popup):**
  > **"Doğru! Akreditasyon kapsamı güncel ve kontrollü kaynaktan doğrulanır. +100 Ece-Coin"**

### Ekran 3.5: Validasyon, Kalibrasyon ve Bakım Farkı
* **Ekran Türü:** Kavram eşleştirme

* **Kalibrasyon:** Belirli koşullarda cihaz göstergesi ile referanslar arasındaki ilişkiyi ve ilgili belirsizliği belirleme faaliyeti.
* **Validasyon:** Bir sistemin, prosesin, alanın veya taşıma çözümünün belirlenmiş amaç ve kabul ölçütlerini karşıladığını kanıta dayalı değerlendirme. Protokol, ölçüm planı, koşullar, kabul ölçütleri ve rapor birlikte ele alınır.
* **Bakım/onarım:** Cihazın işlevini korumaya veya arızayı gidermeye yönelik faaliyettir; sonrasında kalibrasyon ihtiyacı ayrıca değerlendirilir.
* **Ayarlama:** Cihazın göstergesini veya davranışını değiştirmeye yönelik müdahaledir; kalibrasyonla aynı işlem değildir.

**Kural:** Teknik kapsam, kabul ölçütü veya akreditasyon durumu belirsizse müşteri adına yorum üretme; ilgili teknik sorumluya yönlendir.

* **Seslendirme:**
  > *"Kalibrasyon, referansla cihaz arasındaki ilişkiyi ve belirsizliği belirler. Validasyon, bir sistemin veya alanın amacına uygunluğunu kabul ölçütleriyle kanıtlar. Bakım ve onarım işlevi korur veya arızayı giderir. Ayarlama ise göstergeye müdahaledir. Bunları birbirine karıştırma; emin değilsen teknik sorumluya yönlendir."*
* **Etkileşim:** Dört kavram kartı, dört tanımla eşleştirilir.

---

<a id="modul-4"></a>

## MODÜL 4: MÜŞTERİ İLETİŞİMİ VE MESLEKİ ETİK

### Ekran 4.1: "Müşteri Değil Çözüm Ortağı, Cihaz Değil Emanet"
* **Ekran Türü:** Kültürel Dönüşüm & Transkript Ekranı
* **Görsel Tasarım:** Sahada müşteriye güler yüzle cihaz teslim eden Ece Kalibrasyon teknisyeni.

```text
+-------------------------------------------------------------------+
|  ECE KALİBRASYON HİZMET KÜLTÜRÜ                                   |
+-------------------------------------------------------------------+
|  Müşteri  -->  "ÇÖZÜM ORTAĞI"                                     |
|  Cihaz    -->  "HASSAS EMANET"                                    |
|  Saha     -->  "GÜVENLİK VE KALİTE MEVZİSİ"                       |
+-------------------------------------------------------------------+
```

* **Seslendirme (Voice-Over Transkripti):**
  > *"Laboratuvarımıza gelen bir cihaz veya sahada test ettiğimiz bir sistem sadece metal ve elektronikten ibaret değildir. O cihaz, müşterimizin üretim kalitesine ve kararlarına doğrudan etki eder.
  > Bu yüzden müşterilerimize 'Çözüm Ortağı', cihazlarına ise 'Hassas Emanet' gözüyle bakarız. Onların sorularına doğru, anlaşılır ve bilimsel yanıtlar vermek temel ilkemizdir."*

---

### Ekran 4.2: Sıkça Sorulan Müşteri Soruları Simülasyonu
* **Ekran Türü:** Tıklamalı Konuşma Baloncukları

```text
 Müşteri: "Sertifikam ne zaman teslim edilir?"
 Yanıt:   "Süre; hizmet türü, iş yoğunluğu ve teknik gözden geçirmeye bağlıdır. İş emrinizdeki güncel teslim bilgisini kontrol edip size teyit edeceğim."

 Müşteri: "Sertifikadaki sapma değeri limit dışı ise ne yapmalıyız?"
 Yanıt:   "Önce rapordaki sonuç tanımını, belirsizliği ve varsa karar kuralını birlikte inceleyelim. Uygunluk yorumu için şartname/tolerans bilginiz de gerekli; teknik değerlendirme yapmadan tek bir değere bakarak karar vermek doğru olmaz."

 Müşteri: "Yerinde kalibrasyon yapıyor musunuz?"
 Yanıt:   "Bazı cihaz ve sistemler için yerinde hizmet planlanabilir. Cihaz türü, ölçüm aralığı, lokasyon, erişim ve saha koşullarını alıp teknik ekibimizle yapılabilirliği teyit edelim."
```

* **Seslendirme:**
  > *"Müşteri sorularında altın kural şudur: bildiğini açık söyle, bilmediğini tahmin etme. Teslim süresi, uygunluk yorumu ve yerinde hizmet gibi konularda önce kontrollü kaynağı ve teknik sorumluyu devreye al, sonra müşteriye net bir geri dönüş zamanı ver."*

### Ekran 4.3: Zor Görüşmelerde İletişim
* **Ekran Türü:** Diyalog simülasyonu

**Müşteri:** “Rakibiniz bu değeri uygun buldu; siz de raporu uygun yazın.”
* **Uygun yanıt:** “Sonucu herhangi bir ticari talebe göre değiştiremeyiz. Ölçüm verisini, rapordaki belirsizliği ve sizin kabul ölçütlerinizi teknik ekiple birlikte gözden geçirebilirim. Gerekirse resmi inceleme sürecini başlatalım.”

**Müşteri:** “Başka bir müşterinin cihazında ne sonuç çıktı?”
* **Uygun yanıt:** “Diğer müşterilere ait bilgi ve raporları paylaşamam. Kendi cihazınıza ait kayıtları yetkiniz doğrulandıktan sonra inceleyebilirim.”

**Müşteri:** “Cihazı bugün ayarlayıp kalibre edilmiş gibi gönderebilir misiniz?”
* **Uygun yanıt:** “Kalibrasyon ve ayarlama farklı işlemlerdir. Talebinizi teknik ekibe ileteyim; onayınız, uygulanabilirlik ve kayıt gereklilikleri netleşmeden cihaz üzerinde değişiklik yapmayız.”

* **Seslendirme:**
  > *"Zor görüşmelerde sakin, net ve tutarlı kal. Sonucu ticari talebe göre değiştirmeyiz. Başka müşterilerin bilgisini paylaşmayız. Kalibrasyonla ayarlamayı karıştırmayız. Bunu söylerken de çözüm sun: teknik ekiple birlikte veriyi gözden geçirmeyi ve resmi süreci başlatmayı teklif et."*

### Ekran 4.4: Müşteri İhtiyacını Doğru Anlama
* **Ekran Türü:** Soru kartı sıralama

Teklif veya yönlendirme öncesinde şu bilgileri topla:
* Cihazın adı, üreticisi/modeli ve seri numarası.
* Ölçülen büyüklük, istenen aralık/noktalar ve kullanım amacı.
* Müşterinin toleransı, şartnamesi ve uygunluk beyanı isteyip istemediği.
* Laboratuvar veya saha tercihi; saha adresi, erişim ve güvenlik koşulları.
* İstenen teslim tarihi, cihazın arıza/hasar durumu ve ilgili aksesuarlar.
* Akreditasyon şartı varsa talep edilen ölçümün ve lokasyonun kapsamla eşleşmesi.

**Sınır:** Bilinmeyen teknik soruda tahmin yürütmek yerine soruyu kaydet, sorumluya aktar ve müşteriye geri dönüş zamanı ver.

* **Seslendirme:**
  > *"İyi bir teklif, iyi sorularla başlar. Cihazı, ölçüm aralığını, toleransı, lokasyonu ve akreditasyon beklentisini baştan netleştirirsen hem müşteri hem laboratuvar zaman kazanır."*

### Ekran 4.5: Modül 4 Pekiştirme Quizi
* **Ekran Türü:** Çoktan seçmeli
* **Soru:** Müşteri başka bir firmanın cihazına ait sonucu soruyor. Doğru yanıt hangisidir?
  * A) Kısaca söyleyip konuyu kapatırım.
  * **B) Diğer müşterilere ait bilgi paylaşamayacağımı, yalnızca yetkisi doğrulanan kendi cihaz kayıtlarının incelenebileceğini söylerim.** ✔
  * C) Sonucu e-postayla gönderirim ama kimseye söylemem.
* **Geri bildirim:** Doğru yanıtta "+100 Ece-Coin"; yanlış yanıtta Ekran 4.3 öğrenme kartına yönlendirme ve tekrar deneme.

---

<a id="modul-5"></a>

## MODÜL 5: ÇALIŞAN REHBERİ, İSG VE SAHA GÜVENLİĞİ

### Ekran 5.1: Özlük Hakları ve İzin Tablosu
* **Ekran Türü:** İnteraktif Bilgi Tablosu

```text
+-------------------------------------------------------------------+
| YILLIK ÜCRETLİ İZİN HAKLARI TABLOSU                              |
+-------------------------------------------------------------------+
| Kıdem Süresi                             | Yıllık ücretli izin (gün) |
+------------------------------------------+------------------------+
| 1 yıl - 5 yıl (5 yıl dahil)              | 14 gün                  |
| 5 yıldan fazla - 15 yıldan az            | 20 gün                  |
| 15 yıl ve üzeri                          | 26 gün                  |
+-------------------------------------------------------------------+
```

* **Seslendirme:**
  > *"İş Kanunu'na göre yıllık ücretli izin süresi, bir ila beş yıl arasında, beş yıl dahil, on dört gün; beş yıldan fazla, on beş yıldan az olanlarda yirmi gün; on beş yıl ve üzerinde yirmi altı gündür. Bakiyeni ve özel durumları İnsan Kaynakları'ndan teyit et."*
* **Etkileşim:** Üç kıdem senaryosu, doğru izin süresiyle eşleştirilir.
* **Not:** On sekiz yaşından küçük ve elli yaşından büyük çalışanlar için asgari süre yirmi gündür; kişisel durum için İnsan Kaynakları esas alınır.
* **Önemli:** Kanuni yıllık ücretli izin süreleri iş günü değil gündür; hafta tatili ve ulusal bayram/genel tatil günlerinin hesaba katılması ilgili mevzuata tabidir. Bu özet, kişisel durum veya güncel mevzuat için hukuki görüş değildir. İzin bakiyesi, kıdem hesabı ve şirket uygulaması için İnsan Kaynakları ve güncel mevzuat esas alınmalıdır.

---

### Ekran 5.2: Laboratuvar ve Saha İSG Kuralları
* **Ekran Türü:** Sürükle-Eşleştir Ekranı
* **Görsel Tasarım:** Teknisyen avatarının üzerine giydirilecek Koruyucu Ekipmanlar (PPE).

```text
     [ TEKNİSYEN AVATARI ]               [ RİSKE GÖRE SEÇİLEN KKD ]
       [O]                            Önlük / iş kıyafeti
        ||                            İş ayakkabısı
       /  \                            Göz koruyucu
                                      Temiz oda kıyafeti / galoş
```

* **Seslendirme (Voice-Over Transkripti):**
  > *"Güvenli çalışma, işe başlamadan önce riskleri fark etmekle başlar. Kullanılacak kişisel koruyucu donanım; görev, risk değerlendirmesi, saha kuralları ve ilgili prosedüre göre seçilir. Basınç, elektrik, kaldırma-taşıma, sıcak yüzey ve temiz oda işleri farklı tehlikeler içerir. Emin değilsen işe başlamadan dur, alan sorumlusuna danış."*

### Ekran 5.3: Saha Öncesi Güvenli İş Planı
* **Ekran Türü:** “Başla / durdur” senaryosu

İşe başlamadan önce:
1. İş kapsamını, görev paylaşımını ve müşteri saha kurallarını teyit et.
2. Risk değerlendirmesi, izin/izolasyon gereklilikleri ve acil durum bilgisini kontrol et.
3. Kullanılacak cihaz, kablo, adaptör, yük ve referansları gözle kontrol et; hasarlı ekipmanı kullanma.
4. Basınç veya elektrik enerjisi içeren düzeneğin güvenli kurulumu ve enerjisiz bırakma adımlarını yetkin sorumluya göre uygula.
5. Uygun KKD'yi giy; çalışma alanını sınırla ve yetkisiz kişileri tehlikeden uzak tut.
6. Beklenmeyen durum, ramak kala veya yaralanmada işi güvenli biçimde durdur ve bildir.

**Durdur ve danış:** Uygun olmayan ortam koşulu, koruyucu eksikliği, hasarlı ekipman, belirsiz talimat veya yetkinlik dışı iş varsa ölçüme başlamadan yetkili kişiye haber ver.

* **Seslendirme:**
  > *"İşe başlamadan önce altı adımı uygula: kapsamı ve saha kurallarını teyit et, riskleri ve acil durum bilgisini kontrol et, ekipmanı gözle denetle, basınç ve elektrik düzeneğini güvenle kur, uygun koruyucu donanımı giy, beklenmeyen bir durumda işi durdur ve bildir. Şüphen varsa dur ve danış. Hiçbir ölçüm, bir kazaya değmez."*
* **Etkileşim:** Üç saha senaryosunda katılımcı "başla" veya "durdur ve danış" kararı verir. Hasarlı kablo, eksik KKD ve belirsiz talimat durumlarında doğru karar "durdur"dur.
* **Kritik senaryo:** Doğru karar verilmeden modül tamamlanmış sayılmaz.

---

<a id="modul-6"></a>

## MODÜL 6: UYGULAMALI FİNAL GÖREVİ

### Ekran 6.1: Akreditasyon Günü Simülasyonu
* **Ekran Türü:** Zaman Karşı Yarış Mini-Oyunu
* **Görsel Tasarım:** TÜRKAK Denetçisi laboratuvara girer. Ekranda 3 denetim kontrol noktası yanıp söner.

```text
+-------------------------------------------------------------------+
| AKREDİTASYON HAZIRLIĞI ÖĞRENME SİMÜLASYONU                       |
+-------------------------------------------------------------------+
| [!] Kontrol 1: İlgili prosedüre göre çevre koşulları kayıtları   |
| [!] Kontrol 2: Kullanılan referansların geçerli izlenebilirliği   |
| [!] Kontrol 3: Sonuç, belirsizlik ve karar kuralı                 |
|                                                                   |
|  Her kontrol noktasını kanıtla ve bulguları doğru yönlendir.      |
|  [ GÖREVİ TAMAMLA ]                                               |
+-------------------------------------------------------------------+
```

* **Oyun mekaniği:** Süre 3 dakikadır. Denetçi her kontrol noktasında bir soru sorar; katılımcı üç kanıt kartından doğru olanı seçer.
  * **Kontrol 1 (çevre koşulları):** Doğru kanıt, ölçüm anında eşzamanlı alınmış ve prosedürdeki sınırlarla karşılaştırılmış koşul kaydıdır. Sonradan hatırlanarak yazılmış not yanlıştır.
  * **Kontrol 2 (izlenebilirlik):** Doğru kanıt, geçerli kalibrasyon sertifikası ve kesintisiz referans zinciridir. Süresi geçmiş veya zinciri belirsiz referans yanlıştır.
  * **Kontrol 3 (sonuç ve karar kuralı):** Doğru kanıt, belirsizliği ve kararın dayandığı kuralı içeren rapordur.
* **Puanlama:** Her kontrol 150 Ece-Coin; süre bitmeden üçünü de tamamlayana 50 Ece-Coin ek puan. Toplam 500 Ece-Coin.
* **Süre dolarsa:** Eksik kalan kontrol, doğru yanıt gösterilerek tekrar edilir; coin yarıya iner.
* **Seslendirme:**
  > *"TÜRKAK denetçisi kapıda! Panik yok. Her kontrol noktasında iddiayı kanıtla destekle: koşul kayıtlarını, referansların izlenebilirliğini, sonuç, belirsizlik ve karar kuralını göster. Denetim, hazırlıklı ve dürüst bir laboratuvar için bir fırsattır."*

---

### Ekran 6.2: Görev Tamamlandı ve Kapanış
* **Ekran Türü:** Kutlama Ekranı & Sertifika Üretimi

```text
+-------------------------------------------------------------------+
|                                                                   |
|                 TEBRİKLER! GÖREV TAMAMLANDI                      |
|                                                                   |
|        TÜM ÖĞRENME ADIMLARINI BAŞARIYLA TAMAMLADIN.                 |
|        Bu simülasyon gerçek denetim sonucu veya yetki belgesi değildir. |
|                                                                   |
|                  PUAN: LMS değerlendirme kuralına göre             |
|                  TAMAMLAMA: Oryantasyon öğrenme kaydı              |
|                                                                   |
|   [ ORYANTASYON SERTİFİKASINI İNDİR (PDF) ]                      |
|   [ ŞİRKET İÇİ DOKÜMANLARA GİT ]                                 |
|                                                                   |
+-------------------------------------------------------------------+
```

* **Seslendirme (Voice-Over Transkripti):**
  > *"Tebrikler, oryantasyon öğrenme yolculuğunu tamamladın. Bu eğitim temel kavramları ve doğru eskalasyon adımlarını tanıtır; bağımsız çalışma yetkisi vermez. Her yöntem için gerekli gözetimli uygulama ve yetkinlik değerlendirmesi ayrıca tamamlanır. Laboratuvarda ve sahada güvenli, tarafsız ve dikkatli çalışmalar dileriz."*

### Ekran 6.3: Final Vaka - Uygun Olmayan Sonuç ve Müşteri Baskısı
**Durum:** Müşteri cihazı üretim toleransının dışında görünüyor; müşteri sevkiyatını geciktirmemek için “uygun” ifadesi istiyor.

Katılımcı şu adımları seçmelidir:
1. Ham veriyi ve cihaz kimliğini doğrula; hesabı ve rapor tanımlarını gözden geçir.
2. Ölçüm belirsizliği ile müşteri şartnamesini ve önceden belirlenmiş karar kuralını birlikte değerlendir.
3. Teknik gözden geçirme ve uygunsuz iş prosedürünü uygula; veriyi değiştirme.
4. Sonucu ve varsa karar kuralını açık, tarafsız bir dille müşteriye ilet; alternatif teknik adımları yetkili sorumlu üzerinden değerlendir.

* **Başarı ölçütü:** Sonucu baskıya göre değiştirmemek, belirsizliği dikkate almak, kayıtları korumak ve uygun eskalasyon yapmak.
* **Puanlama:** Dört adımın her biri 100 Ece-Coin; toplam 400. Veriyi veya sonucu değiştirmeyi seçen katılımcı vakayı yeniden oynar ve coin kazanamaz.
* **Seslendirme:**
  > *"Sevkiyat yaklaşıyor, müşteri sabırsız, ama sonuç tolerans dışında görünüyor. Doğru yol bellidir: ham veriyi ve kimliği doğrula, belirsizliği ve karar kuralını birlikte değerlendir, teknik gözden geçirmeyi başlat ve sonucu tarafsız bir dille ilet. Veriyi asla değiştirme."*

---

<a id="modul-7"></a>

## MODÜL 7: İŞBAŞI ÖĞRENME VE YETKİNLİK
* **Seslendirme:**
  > *"Bu oryantasyonu tamamlamak, tek başına bir ölçüm yönteminde bağımsız çalışma yetkisi vermez. Yetkinlik beş aşamada kazanılır: bilgi edinme, gözetimli uygulama, yetkinlik değerlendirmesi, yetkilendirme ve süreklilik. Her aşamada eğitici ve yönetici sana destek olur."*
* **Etkileşim (7.2):** Yedi kontrol listesi maddesi, "ölçüm öncesi / ölçüm sırası / ölçüm sonrası" sütunlarına sürüklenir. Toplam 200 Ece-Coin.

### 7.1 Oryantasyondan Yetkilendirmeye
Bu e-öğrenmeyi tamamlamak, tek başına bir ölçüm yönteminde bağımsız çalışma yetkisi vermez. Yetkinlik; eğitim, gözetimli uygulama, gözlem/ölçme, kayıt ve yetkilendirme adımlarıyla ilgili görev için ayrı ayrı doğrulanır.

| Aşama | Çalışan | Eğitici / yönetici |
|---|---|---|
| Bilgi edinme | Prosedür ve temel kavramları inceler | Güncel dokümanı ve hedefleri sağlar |
| Gözetimli uygulama | İş akışını uygular, soru sorar | Gözlemler, geri bildirim ve kayıt verir |
| Yetkinlik değerlendirmesi | Uygulamayı bağımsız biçimde gösterir | Önceden belirlenmiş ölçütle değerlendirir |
| Yetkilendirme | Yetki sınırlarını bilir | Kapsamı ve tarihi kayıt altına alır |
| Süreklilik | Değişiklikleri ve hataları bildirir | İzleme, yeniden değerlendirme ve eğitim planlar |

### 7.2 Gözetimli Uygulama Kontrol Listesi
* Cihaz ve referans kimliklerini doğru eşleştirme.
* Kullanılan yöntem ve geçerli doküman revizyonunu belirleme.
* Ölçüm öncesi koşulları ve ekipmanın durumunu kontrol etme.
* Ham veriyi okunaklı, izlenebilir ve zamanında kaydetme.
* Hesap, birim, belirsizlik ve rapor kontrollerini yapma.
* Sonuç ve kapsamla ilgili soruları yetki sınırları içinde yanıtlama.
* Uygunsuzluk veya beklenmedik durumda işi durdurup bildirme.

<a id="modul-8"></a>

## MODÜL 8: TERİMLER, KAYNAKLAR VE BİLGİ GÜNCELLEME
* **Seslendirme:**
  > *"Son durak: terimler ve kaynaklar. Metroloji, kalibrasyon, ayarlama, doğrulama, validasyon, belirsizlik, izlenebilirlik, akreditasyon kapsamı ve karar kuralı; bunlar ortak dilimiz. Bilgiden emin olmadığında güncel kontrollü dokümana, TÜRKAK kapsam ekine veya doküman sahibine başvur."*
* **Etkileşim:** 8.1'de dokuz terim tanımlarıyla eşleştirilir (100 Ece-Coin); 8.2'de "bu bilgiyi hangi kaynaktan doğrularsın?" kartları eşleştirilir (100 Ece-Coin).

### 8.1 Kısa Terimler Sözlüğü
* **Metroloji:** Ölçüm ve uygulamalarını kapsayan ölçüm bilimi.
* **Kalibrasyon:** Belirli koşullarda referanslar ile cihaz göstergeleri arasındaki ilişkiyi belirleyip sonuçları ve belirsizliği ortaya koyan faaliyet.
* **Ayarlama:** Ölçüm sistemini belirli bir gösterge/performansa getirmek için yapılan müdahale.
* **Doğrulama:** Belirtilen şartların karşılandığına ilişkin nesnel kanıt sağlama.
* **Validasyon:** Kullanım amacı için belirlenmiş şartların karşılandığını kanıtla gösterme.
* **Ölçüm belirsizliği:** Ölçüm sonucuna atfedilebilecek değerlerin dağılımını tanımlayan parametre.
* **İzlenebilirlik:** Sonucun belgelenmiş kesintisiz bir kalibrasyon zinciriyle bir referansa bağlanabilme özelliği.
* **Akreditasyon kapsamı:** Akreditasyonun geçerli olduğu faaliyet, yöntem, aralık ve ilgili lokasyonların kontrollü tanımı.
* **Karar kuralı:** Uygunluk beyanında ölçüm belirsizliğinin nasıl hesaba katılacağını açıklayan kural.

### 8.2 Eğitimde Kullanılan Bilginin Kontrolü
* Kurum profili, hizmet listesi ve akreditasyon numarası için şirketin güncel kurumsal kaynaklarını kullan.
* Akreditasyon iddiası ve ölçüm aralığı için güncel TÜRKAK kapsam eki ile geçerli şirket prosedürünü kontrol et.
* Mevzuat, izin, çalışma koşulu, teslim süresi ve saha gereklilikleri için ilgili güncel dokümanın sahibine danış.
* Bu rehberdeki örnek sayıların ve senaryoların öğretim amaçlı olduğunu unut; iş talimatı, teklif veya gerçek rapor yerine kullanma.
* Doküman sahibi, gözden geçirme tarihi, revizyon numarası ve değişiklik geçmişi LMS/doküman yönetim sisteminde tutulmalıdır.

---

<a id="lms"></a>

## LMS YÖNETİMİ, SCORM VE TEKNİK UYARLAMA

### 9.1 Teknik Yayın Standartları
* **Paket formatı:** Kurumun LMS'si ve raporlama ihtiyacına göre SCORM 1.2, SCORM 2004 veya xAPI seçilir; tek bir seçenek tüm LMS'lerle uyumlu varsayılmaz.
* **Uygulanan çözüm:** Program (`program/`) SCORM 1.2 olarak paketlenmiştir (durum, 0–100 puan, konum ve `suspend_data`); LMS yoksa şirket içi web sitesi ve `yonetici.html` raporuyla kullanılır. Gerçek LMS'de pilot doğrulama gereklidir.
* **Görüntüleme:** Duyarlı HTML5 içerik; masaüstü, tablet ve telefon ekranlarında test edilir.
* **Uyumluluk:** Kullanılacak yazarlama aracı ve LMS sürümü, gerçek test ortamında paket yükleme ve kayıt senaryolarıyla doğrulanır.
* **Ses:** Seslendirme için kullanılan format ve kalite, yazarlama aracının/LMS'nin gereksinimine göre belirlenir; tüm seslere senkronize metin dökümü veya altyazı sağlanır.

### 9.2 Başarı Metrikleri
* **Başarı kuralı:** Kurumun LMS yöneticisi ve kalite birimi belirler. Öneri olarak modül sonlarında en az %80; kritik İSG ve etik senaryolarında ise kritik adımların tamamının doğru yapılması kullanılabilir.
* **Süre:** İçeriğin pilot uygulamasından sonra ölçülür; modüler ve duraklatılabilir tasarlanır.
* **Takip edilen veriler:** Başlama/tamamlama zamanı, modül ilerlemesi, quiz sonucu, tekrar sayısı ve içerik revizyonu. SCORM'da ilgili `cmi.*` alanları seçilen sürüme göre uygulanır.
* **Geri bildirim:** Yanlış yanıtta doğru seçeneği göstermekle kalma; katılımcıyı ilgili öğrenme kartına geri yönlendir ve tekrar deneme sun.
* **Erişilebilirlik:** Klavye ile kullanım, yeterli kontrast, ekran okuyucuya uygun etiketler, altyazı/transkript ve mobil uyum test edilir.
* **Güncelleme:** Akreditasyon kapsamı, mevzuat, hizmet, adres veya şirket prosedürü değiştiğinde içerik sahibi inceleme başlatır; eski sürümler yürürlükten kaldırılır.

### Önerilen Uygulama Ölçütleri
* Eğitim tamamlama ve modül terk oranı.
* İlk denemede başarı ve tekrar sonrası başarı.
* Kritik hata senaryolarında doğru eskalasyon oranı.
* Eğitim sonrası ilk gözetimli uygulamada kontrol listesi başarısı.
* İçerik revizyonu bekleyen maddelerin sayısı ve açık kaldığı süre.

Bu metrikler çalışan performansını tek başına puanlamak için değil, eğitimin anlaşılırlığını ve iyileştirme ihtiyacını görmek için kullanılmalıdır.
