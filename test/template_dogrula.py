"""Tüm Jinja şablonlarının parse/derleme edilebildiğini doğrular (kod-şablon sözleşmesini yakalamaz)."""
import os
import sys

from jinja2 import Environment, FileSystemLoader, TemplateError

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATES = os.path.join(ROOT, "templates")
RUNTIME_FILTERS = ("tarih", "tarih_saat", "sayi")


def main():
    """Şablonları derler; sözdizimi veya tanımsız filtre hatası varsa hata koduyla çıkar."""
    env = Environment(loader=FileSystemLoader(TEMPLATES))
    for name in RUNTIME_FILTERS:
        env.filters[name] = lambda value, *args, **kwargs: value
    errors = []
    for folder, _, files in os.walk(TEMPLATES):
        for name in files:
            if not name.endswith(".html"):
                continue
            relative = os.path.relpath(os.path.join(folder, name), TEMPLATES).replace(os.sep, "/")
            try:
                env.get_template(relative)
            except TemplateError as error:
                errors.append("{}: {}".format(relative, error))
    for error in errors:
        print("HATA", error)
    print("template_dogrula:", "BASARISIZ" if errors else "temiz")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
