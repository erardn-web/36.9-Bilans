"""templates/neutre.py — Template neutre sans tests prédéfinis"""
from core.bilan_template import BilanTemplate
from core.registry import register_template

NEUTRE = register_template(BilanTemplate(
    template_id = "neutre",
    nom         = "Bilan neutre",
    icone       = "📋",
    description = "Template libre — onglet général uniquement, ajoutez vos tests depuis la bibliothèque",
    tests       = [],
))
