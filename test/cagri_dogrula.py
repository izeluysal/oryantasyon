"""`Sinif.metot(kw=...)` çağrılarında, proje içi sınıfın metodunun o parametreyi kabul ettiğini doğrular."""
import ast
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from import_dogrula import ROOT, python_files  # noqa: E402


def collect_signatures():
    """Proje sınıflarının metot imzalarını toplar: {sınıf: {metot: (parametreler, **kwargs var mı)}}."""
    signatures = {}
    for path in python_files():
        with open(path, encoding="utf-8") as source:
            tree = ast.parse(source.read())
        for node in ast.walk(tree):
            if not isinstance(node, ast.ClassDef):
                continue
            methods = signatures.setdefault(node.name, {})
            for item in node.body:
                if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    args = item.args
                    names = {arg.arg for arg in args.args + args.kwonlyargs}
                    methods[item.name] = (names, args.kwarg is not None)
    return signatures


def main():
    """Anahtar kelimeli çağrıları imzalarla karşılaştırır."""
    signatures = collect_signatures()
    errors = []
    for path in python_files():
        with open(path, encoding="utf-8") as source:
            tree = ast.parse(source.read())
        for node in ast.walk(tree):
            if not (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
                    and isinstance(node.func.value, ast.Name)):
                continue
            method = signatures.get(node.func.value.id, {}).get(node.func.attr)
            if method is None or method[1]:
                continue
            for keyword in node.keywords:
                if keyword.arg and keyword.arg not in method[0]:
                    errors.append("{}:{} {}.{}() '{}' parametresini kabul etmiyor".format(
                        os.path.relpath(path, ROOT), node.lineno, node.func.value.id, node.func.attr, keyword.arg))
    for error in errors:
        print("HATA", error)
    print("cagri_dogrula:", "BASARISIZ" if errors else "temiz")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
