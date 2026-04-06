"""
fix_imports.py — Script de migration des imports pour la réorganisation tests/
À exécuter UNE SEULE FOIS à la racine du repo : python fix_imports.py

Remplace :
  tests.tests_cliniques.xxx  →  tests.xxx
  tests.questionnaires.xxx   →  tests.xxx
dans tous les fichiers .py du projet.
"""
import re, os, pathlib

ROOT = pathlib.Path(__file__).parent

PATTERNS = [
    (r'tests\.tests_cliniques\.(\w+)', r'tests.\1'),
    (r'tests\.questionnaires\.(\w+)',  r'tests.\1'),
]

EXCLUDE_DIRS = {'.git', '__pycache__', '.venv', 'venv', 'node_modules'}

changed_files = []
errors = []

for py_file in sorted(ROOT.rglob("*.py")):
    # Ignorer les dossiers exclus
    if any(part in EXCLUDE_DIRS for part in py_file.parts):
        continue
    # Ignorer ce script lui-même
    if py_file.name == "fix_imports.py":
        continue

    try:
        original = py_file.read_text(encoding="utf-8")
        updated  = original
        for pattern, replacement in PATTERNS:
            updated = re.sub(pattern, replacement, updated)

        if updated != original:
            py_file.write_text(updated, encoding="utf-8")
            # Compter les remplacements
            n = sum(len(re.findall(p, original)) for p, _ in PATTERNS)
            changed_files.append((str(py_file.relative_to(ROOT)), n))
            print(f"✅ {py_file.relative_to(ROOT)}  ({n} remplacement(s))")
    except Exception as e:
        errors.append((str(py_file.relative_to(ROOT)), str(e)))
        print(f"❌ {py_file.relative_to(ROOT)}: {e}")

print(f"\n{'='*50}")
print(f"✅ {len(changed_files)} fichier(s) mis à jour")
if errors:
    print(f"❌ {len(errors)} erreur(s)")
    for f, e in errors:
        print(f"   {f}: {e}")
else:
    print("Aucune erreur.")
print("\nN'oublie pas de faire un Reboot app après le push !")
