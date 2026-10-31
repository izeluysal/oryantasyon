"""Proje içi `from app... import X` ifadelerinin hedefinin gerçekten tanımlı olduğunu AST ile doğrular."""
import ast
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def python_files():
    """Taranacak Python dosyalarını döndürür."""
    result = [os.path.join(ROOT, "application.py")]
    for folder, _, files in os.walk(os.path.join(ROOT, "app")):
        result.extend(os.path.join(folder, name) for name in files if name.endswith(".py"))
    return result


def module_path(module):
    """Modül adını dosya (veya paket __init__) yoluna çevirir; yoksa None."""
    base = os.path.join(ROOT, *module.split("."))
    if os.path.isfile(base + ".py"):
        return base + ".py"
    if os.path.isfile(os.path.join(base, "__init__.py")):
        return os.path.join(base, "__init__.py")
    return None


def defined_names(path):
    """Modül düzeyinde tanımlı isimleri (def, class, atama, import) döndürür."""
    with open(path, encoding="utf-8") as source:
        tree = ast.parse(source.read())
    names = set()
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            names.add(node.name)
        elif isinstance(node, (ast.Assign, ast.AnnAssign)):
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            for target in targets:
                if isinstance(target, ast.Name):
                    names.add(target.id)
        elif isinstance(node, (ast.Import, ast.ImportFrom)):
            for alias in node.names:
                names.add((alias.asname or alias.name).split(".")[0])
    return names


def main():
    """Tüm dosyaları tarar; çözümlenemeyen import varsa hata koduyla çıkar."""
    errors = []
    for path in python_files():
        with open(path, encoding="utf-8") as source:
            tree = ast.parse(source.read())
        for node in ast.walk(tree):
            if not isinstance(node, ast.ImportFrom) or not node.module or node.module.split(".")[0] != "app":
                continue
            target = module_path(node.module)
            if target is None:
                errors.append("{}:{} modül yok: {}".format(os.path.relpath(path, ROOT), node.lineno, node.module))
                continue
            names = defined_names(target)
            for alias in node.names:
                if alias.name in names or module_path(node.module + "." + alias.name):
                    continue
                errors.append("{}:{} {} içinde '{}' tanımlı değil".format(
                    os.path.relpath(path, ROOT), node.lineno, node.module, alias.name))
    for error in errors:
        print("HATA", error)
    print("import_dogrula:", "BASARISIZ" if errors else "temiz")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
