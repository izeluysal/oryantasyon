# Proje Rehberi - Ece Kalibrasyon Oryantasyon Programı

Bu doküman projenin kısa tanıtımı ve kullanım rehberidir. Ayrıntılı iş kuralları için
[oryantasyon.md](oryantasyon/oryantasyon.md), geliştirme kuralları için
[softwarestandarts.md](softwarestandarts.md) dosyasına bakın.

## 1. Proje nedir

Ece Kalibrasyon'a yeni başlayan çalışanların işe uyumunu sağlayan, tarayıcıdan kullanılan bir eğitim
uygulamasıdır. Çalışan 24 eğitim ekranını sırayla izler, her ekranın sorularını yanıtlar ve Ece-Coin
kazanır. Tüm eğitim bitince sertifika alır. Yöneticiler ilerlemeyi raporlardan takip eder.

- Teknoloji: Flask, PostgreSQL, Bootstrap (yerel dosyalar), Docker.
- Yapı: çok kiracılı (işletme bazlı veri ayrımı).
- Eğitim: 24 ekran, 55 soru, toplam 4000 Ece-Coin; her ekranda sesli slayt videosu.

## 2. Hangi adrese girilir

| Nereden | Adres |
|---------|-------|
| Bu bilgisayardan | http://localhost:5123 |
| Aynı ağdaki diğer cihazlardan | http://192.168.0.14:5123 |

Uygulama bilgisayarda çalışırken açıktır. Bilgisayar kapanırsa PostgreSQL ve uygulama da kapanır; yeniden
açılışta ikisi de başlatılmalıdır (bkz. bölüm 7). Kalıcı kullanım için Docker ile bir sunucuya kurulmalıdır.

## 3. İlk giriş

| Alan | Değer |
|------|-------|
| E-posta | basar@ecesoft.com.tr |
| Parola | Test1234! |

Bu platform yöneticisi hesabıdır. Girişten sonra parolayı mutlaka değiştirin.

## 4. Roller ve ne yapabilecekleri

| Rol | Yetki |
|-----|-------|
| Yönetici (platform) | İşletme açar, işletmeye "simülasyonla" girer, eğitim içeriğini inceler. Eğitimi alamaz. |
| İşletme yöneticisi | Kendi işletmesinin kullanıcılarını yönetir, eğitimi alır, rapor ve içeriği görür. |
| İşletme kullanıcısı | Eğitimi alır; Ece-Coin, seviye ve rozet kazanır. |
| Denetim | Salt okunur izleme. Eğitimi alamaz. |

## 5. Deneme akışı

Eğitimi öğrenci gözüyle denemek için:

1. Yönetici hesabıyla girin ve soldaki menüden **İşletmeler** ekranına gidin.
2. Yeni bir işletme ekleyin (örneğin "Deneme İşletmesi").
3. İşletmeye simülasyonla girin ve **Ayarlar > Kullanıcılar** sekmesinden bir işletme kullanıcısı ekleyin.
4. Çıkış yapıp yeni kullanıcıyla girin. Menüde **Eğitim** görünür.
5. Ekranları sırayla izleyin, soruları yanıtlayın. Bir ekran bitmeden sonraki açılmaz.
6. 24 ekran bitince **Sertifika** alınır.

Eğitim içeriğini (video, madde, soru ve doğru cevaplar) puan kazanmadan görmek için yönetici hesabıyla
**Eğitim İçeriği** menüsünü kullanın.

## 6. Menü

| Menü | Kim görür | Amaç |
|------|-----------|------|
| Panel | Herkes | Özet ve öğrenci ilerleme kartı |
| Eğitim | Öğrenci rolleri | 24 ekranlı eğitim, sertifika |
| Eğitim İçeriği | Yönetici, işletme yöneticisi, denetim | Eğitimin salt okunur önizlemesi |
| Eğitim Raporu | Yönetici, işletme yöneticisi, denetim | Kim nerede, puan, zorlanılan ekranlar, Excel |
| İşletmeler | Platform yöneticisi | İşletme yönetimi |
| Silinme Raporu | Yönetici rolleri | Silinen kayıtlar ve geri alma |
| Ayarlar | Yönetici rolleri | Kullanıcılar, işlem ve hata kayıtları, güvenlik, tema |

## 7. Çalıştırma (geliştirici)

Gerekli: Python 3.11, PostgreSQL 16, `config.json` (örnek: `config.example.json`).

```
# PostgreSQL (yerel taşınabilir kurulum)
C:\Users\pc\pgdev\bin\pg_ctl.exe start -D C:\Users\pc\pgdev\data

# Uygulama
.venv\Scripts\python.exe application.py

# Testler
.venv\Scripts\python.exe test\calistir.py
```

Docker ile kurulum: `docker-compose.yml` ve `test/deploy.sh` kullanılır.

## 8. Klasör yapısı

| Yol | İçerik |
|-----|--------|
| `application.py`, `Dockerfile`, `requirements.txt` | Çalışma dosyaları |
| `app/` | Flask uygulaması (routes, models, helpers, çeviriler) |
| `templates/`, `static/` | Arayüz; videolar `static/video`, sesler `static/audio` |
| `test/` | Testler, video üretim aracı, dağıtım betiği |
| `md/` | Dokümanlar ve SQL şemaları |
| `version.txt` | Sürüm numarası (her commit'te artar) |

## 9. Eğitim videolarını yeniden üretmek

Metinler değiştiğinde videolar şu araçla yeniden üretilir:

```
python test\build_training_videos.py            # tümü
python test\build_training_videos.py --only 6   # yalnızca bir ekran
```

Anlatım Microsoft edge-tts ile seslendirilir; internet bağlantısı gerekir.

## 10. Henüz yapılmayanlar

Yardım penceresi, bildirim zili, iki adımlı doğrulama, ince ayarlı yetki penceresi, KVKK ekranı, REST API,
Excel ile içe aktarma, e-posta daveti ve çoklu dil (yalnızca Türkçe var). Docker kurulumu bu bilgisayarda
denenmemiştir.
