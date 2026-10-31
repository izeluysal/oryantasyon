# Ece Kalibrasyon Oryantasyon

Yeni başlayan çalışanlar için sesli ve interaktif oryantasyon eğitim platformu. Flask, PostgreSQL ve Bootstrap ile
yazılmıştır; çok kiracılıdır (platform yöneticisi, işletmeler, işletme kullanıcıları).

Eğitim içeriği ve tasarım dokümanı: `md/oryantasyon/oryantasyon.md`. Uyulan yazılım standartları:
`md/softwarestandarts.md`.

## Özellikler

- 24 ekran, 8 modül, 55 pekiştirme sorusu, Türkçe seslendirme; toplam 4000 Ece-Coin, 3 seviye, 4 rozet.
- Puan, seviye ve rozet kararları sunucuda verilir; ekranlar sırayla açılır; zamanlı final simülasyonu.
- Tamamlama kaydı (yazdırılabilir) ve yöneticiler için Eğitim Raporu (filtre, Excel, zorlanılan ekranlar).
- İşletme (kiracı) yönetimi, kullanıcılar, işlem/hata logları, giriş koruması, Silinme Raporu ve geri yükleme.

## Geliştirme ortamı

```bash
python -m venv .venv
.venv\Scripts\Activate.ps1          # Windows PowerShell (Linux: source .venv/bin/activate)
pip install -r requirements.txt
cp config.example.json config.json  # kendi veritabanı bilgilerinizle düzenleyin
for f in md/oryantasyon/[0-9]*.sql; do python test/migration_uygula.py "$f"; done
python application.py
```

İlk açılışta varsayılan platform yöneticisi oluşturulur; ilk girişten sonra şifresini değiştirin.

## Testler

```bash
python test/calistir.py            # statik doğrulamalar + tüm testler (veritabanı gerekir)
python test/calistir.py --statik   # yalnızca veritabanı gerektirmeyenler
```

## Dağıtım

Ubuntu + Docker üzerinde `test/deploy.sh` ile yapılır. Gizli değerler sunucudaki `config.json` dosyasındadır ve
depoya girmez. Zamanlanmış görevler (hata günlüğü aktarımı, giriş denemesi retention'ı, aylık log arşivi) uygulama
içinde çalışır; birden fazla worker olsa da yalnızca biri çalıştırır.

## Eski statik sürüm

`test/legacy_program` ve `test/legacy_video`, bu uygulamaya taşınan ilk statik programın ve video üretim
betiklerinin arşividir; `test/export_training_content.py` içeriği buradan okur.
