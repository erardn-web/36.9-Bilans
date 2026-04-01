"""templates/cervicalgie.py — Template Cervicalgie"""
from core.bilan_template import BilanTemplate
from core.registry import register_template

from tests.tests_cliniques.nrs               import NRS
from tests.tests_cliniques.drapeaux          import Drapeaux
from tests.questionnaires.ndi                import NDI
from tests.questionnaires.psfs               import PSFS
from tests.questionnaires.groc               import GROC
from tests.questionnaires.had                import HAD

CERVICALGIE = register_template(BilanTemplate(
    template_id = "cervicalgie",
    nom         = "Cervicalgie",
    icone       = "🦴",
    description = "Bilan cervicalgie — NRS, drapeaux, NDI, PSFS, HAD, GROC",
    tests       = [
        NRS, Drapeaux, NDI, HAD, PSFS, GROC,
    ],
))
