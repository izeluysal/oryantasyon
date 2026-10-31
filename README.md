# Ece Kalibrasyon Oryantasyon

Yeni başlayan çalışanlar için sesli ve interaktif oryantasyon eğitim platformu. Flask, PostgreSQL ve Bootstrap ile
yazılmıştır; çok kiracılıdır (platform yöneticisi, işletmeler, işletme kullanıcıları).

Eğitim içeriği ve tasarım dokümanı: `md/oryantasyon/oryantasyon.md`. Uyulan yazılım standartları:
`md/softwarestandarts.md`.

## Geliştirme ortamı

```bash
python -m venv .venv
.venv\Scripts\Activate.ps1          # Windows PowerShell (Linux: source .venv/bin/activate)
pip install -r requirements.txt
cp config.example.json config.json  # kendi veritabanı bilgilerinizle düzenleyin
python test/migration_uygula.py md/oryantasyon/01_panel_schema.sql
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
depoya girmez.
