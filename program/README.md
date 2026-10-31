# Ece Kalibrasyon Oryantasyon Programı

Yeni başlayanlar için interaktif, sesli e-öğrenme programı.

**Açmak için:** `index.html` dosyasını tarayıcıda aç (internet gerekmez; sunucu gerekmez).
Bir web sunucusuna (ör. şirket içi site) klasörü olduğu gibi kopyalamak yeterlidir.

## Yapı
- `index.html`, `style.css`, `app.js`: program (ilerleme tarayıcıda `localStorage`'da saklanır)
- `content.js`: ekranlar, sorular, puanlar (üretilen dosya, elle düzenleme)
- `audio/`: Türkçe seslendirmeler (üretilen dosyalar)
- `build_program.py`: içeriğin kaynağı. Değişiklik için bunu düzenle, sonra çalıştır:
  `python program/build_program.py` (metni değişen seslendirmeler yeniden üretilir; `--force` hepsini yeniler)

## Kurallar
- 24 ekran, 8 modül, toplam 4000 Ece-Coin (betik toplamı doğrular).
- Yanlış yanıtta coin kesilmez; sonraki doğru yanıt yarım coin kazandırır.
- Kritik senaryolar (1.4, 5.2/5.3, 6.3) tüm adımlar doğru olmadan geçilemez.
- Sertifika ekranı yalnızca öğrenme kaydıdır; yetki belgesi değildir.


## Dağıtım (python program/package.py → dist/)
1. **LMS:** `ece-oryantasyon-scorm12.zip` dosyasını LMS'ye SCORM 1.2 paketi olarak yükle. Durum (incomplete/completed),
   puan (Ece-Coin yüzdesi, 0–100), konum ve ilerleme (suspend_data) LMS'ye yazılır; çalışan kaldığı yerden devam eder.
   Başarı kuralını (ör. tamamlama) LMS yöneticisi/kalite birimi belirler.
2. **Şirket içi web sitesi:** `ece-oryantasyon-web.zip` klasörünü sunucuya aç; `index.html` çalışanlara verilir.
   Çalışan sonda "Sonuç dosyasını indir" ile JSON dosyasını yöneticiye iletir.
3. **Yönetici raporu:** `yonetici.html` dosyasını aç, çalışanların sonuç dosyalarını bırak: tablo, KPI'lar,
   en çok zorlanılan ekranlar ve CSV dışa aktarımı. Veri tarayıcıdan çıkmaz.

## Sınırlar
- LMS dışında ilerleme yalnızca çalışanın tarayıcısında tutulur (farklı cihazda devam edilemez).
- Gerçek bir LMS'de henüz denenmedi; yalnızca sahte SCORM 1.2 API'siyle test edildi. Yüklemeden önce LMS'nin test ortamında (ör. SCORM Cloud) deneyin.
