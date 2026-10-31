"""Numaralı şema dosyalarını config.json'daki veritabanına olduğu gibi uygular.

Kullanım:
    python test/migration_uygula.py md/oryantasyon/01_panel_schema.sql [...]

Otomatik migration çalıştırıcı değildir: hangi dosyanın uygulanacağına geliştirici karar verir.
"""
import json
import os
import sys

import psycopg2

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def main(paths):
    """Verilen SQL dosyalarını sırayla uygular; ilk hatada durur."""
    with open(os.path.join(ROOT, "config.json"), encoding="utf-8") as config_file:
        settings = json.load(config_file)["postgres"]
    connection = psycopg2.connect(
        host=settings["host"],
        port=settings["port"],
        user=settings["user"],
        password=settings["password"],
        dbname=settings["database"],
    )
    connection.autocommit = True
    try:
        for path in paths:
            with open(path, encoding="utf-8") as sql_file:
                sql = sql_file.read()
            with connection.cursor() as cursor:
                cursor.execute(sql)
            print("uygulandi:", path)
    finally:
        connection.close()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit("Kullanim: python test/migration_uygula.py <dosya.sql> [...]")
    main(sys.argv[1:])
