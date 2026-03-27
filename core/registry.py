"""
core/registry.py — Registre central de tous les tests et templates.

Importer un test = l'enregistrer automatiquement dans le registre.
"""

# ── Registre des tests ────────────────────────────────────────────────────────

_TESTS: dict = {}      # {test_id: TestClass}
_TEMPLATES: dict = {}  # {template_id: BilanTemplate}


def register_test(test_cls):
    """
    Enregistre un test dans le registre global.
    Utilisé comme décorateur ou appelé manuellement.

    Usage:
        @register_test
        class HAD(BaseTest): ...

        # ou dans tests/__init__.py :
        from tests.questionnaires.had import HAD
        register_test(HAD)
    """
    tid = test_cls.meta()["id"]
    _TESTS[tid] = test_cls
    return test_cls


def register_template(template):
    """Enregistre un template dans le registre global."""
    _TEMPLATES[template.template_id] = template
    return template


def get_test(test_id: str):
    """Retourne la classe d'un test par son ID."""
    return _TESTS.get(test_id)


def get_template(template_id: str):
    """Retourne un template par son ID."""
    return _TEMPLATES.get(template_id)


def all_tests() -> dict:
    """Retourne tous les tests enregistrés."""
    return dict(_TESTS)


def all_templates() -> dict:
    """Retourne tous les templates enregistrés."""
    return dict(_TEMPLATES)


def tests_by_category() -> dict:
    """Retourne les tests groupés par catégorie."""
    result = {}
    for tid, cls in _TESTS.items():
        cat = cls.meta().get("categorie", "autre")
        result.setdefault(cat, []).append(cls)
    return result
