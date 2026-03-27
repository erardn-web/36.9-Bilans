"""
core/bilan_template.py — Définition d'un template de bilan.

Un BilanTemplate est une liste ordonnée de tests avec métadonnées.
Il sert de base pour créer des bilans patients (snapshots).
"""


class BilanTemplate:
    """
    Représente un template de bilan — SHV, Lombalgie, Équilibre, BPCO, etc.

    Attributes:
        template_id  : identifiant unique snake_case (ex: "shv")
        nom          : nom affiché (ex: "Syndrome d'Hyperventilation")
        icone        : emoji (ex: "🫁")
        description  : texte court
        tests        : liste ordonnée de classes BaseTest
    """

    def __init__(self, template_id: str, nom: str, icone: str,
                 description: str, tests: list):
        self.template_id = template_id
        self.nom         = nom
        self.icone       = icone
        self.description = description
        self.tests       = tests  # liste de classes (pas d'instances)

    def test_ids(self) -> list:
        """Retourne la liste des IDs de tests dans l'ordre."""
        return [t.test_id() for t in self.tests]

    def fields(self) -> list:
        """Retourne tous les champs GSheets nécessaires pour ce template."""
        seen = set()
        result = []
        for test_cls in self.tests:
            for f in test_cls.fields():
                if f not in seen:
                    seen.add(f)
                    result.append(f)
        return result

    def get_test(self, test_id: str):
        """Retourne la classe du test par son ID."""
        for t in self.tests:
            if t.test_id() == test_id:
                return t
        return None

    def snapshot(self) -> dict:
        """
        Crée un snapshot du template au moment de la création d'un bilan.
        Stocké dans la colonne 'template_snapshot' du bilan.

        Retourne : {
            "template_id": "shv",
            "nom": "SHV",
            "tests": ["had", "sf12", "bolt", ...],
        }
        """
        return {
            "template_id": self.template_id,
            "nom":         self.nom,
            "tests":       self.test_ids(),
        }

    def __repr__(self):
        return f"BilanTemplate({self.template_id}, {len(self.tests)} tests)"
