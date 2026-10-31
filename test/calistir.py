"""Tek komutla tüm doğrulamalar ve testler.

Kullanım:
    python test/calistir.py            # statik doğrulamalar + tüm testler (veritabanı gerekir)
    python test/calistir.py --statik   # yalnızca veritabanı gerektirmeyenler (hızlı, deploy öncesi)
"""
import importlib
import os
import subprocess
import sys
import traceback

TEST_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(TEST_DIR)
sys.path.insert(0, TEST_DIR)

STATIC_CHECKS = ("import_dogrula.py", "cagri_dogrula.py", "template_dogrula.py", "ceviri_dogrula.py")
TEST_MODULES = (
    "test_izolasyon", "test_yetki", "test_regresyon", "test_is_mantigi", "test_egitim", "test_zamanli",
    "test_ekran_duman",
)


def run_static():
    """Statik doğrulama betiklerini çalıştırır; başarısızlık sayısını döndürür."""
    failures = 0
    compiled = subprocess.run([sys.executable, "-m", "compileall", "-q", os.path.join(ROOT, "app"),
                               os.path.join(ROOT, "application.py")])
    failures += compiled.returncode != 0
    for script in STATIC_CHECKS:
        result = subprocess.run([sys.executable, os.path.join(TEST_DIR, script)])
        failures += result.returncode != 0
    return failures


def run_tests():
    """Testleri çalıştırır; önce veritabanına bağlanılabildiğini tek mesajla doğrular."""
    from _ortam import cleanup, database_reachable

    if not database_reachable():
        return 1
    cleanup()  # önceki bir çökmeden artık kalmışsa başlangıçta bir kez toplu temizlik
    failures = 0
    for module_name in TEST_MODULES:
        module = importlib.import_module(module_name)
        for name in sorted(vars(module)):
            if not name.startswith("test_"):
                continue
            try:
                getattr(module, name)()
                print("gecti   {}.{}".format(module_name, name))
            except Exception:  # noqa: BLE001 - her test başarısızlığı raporlanır, koşu sürer
                failures += 1
                print("BASARISIZ {}.{}".format(module_name, name))
                traceback.print_exc()
    return failures


def main():
    """Çalıştırıcı."""
    failures = run_static()
    if "--statik" not in sys.argv:
        failures += run_tests()
    print("\nSonuc:", "BASARISIZ ({})".format(failures) if failures else "tum kontroller gecti")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
