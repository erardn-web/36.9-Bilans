"""templates/cervicalgie.py — Template Cervicalgie"""
from core.bilan_template import BilanTemplate
from core.registry import register_template

from tests.nrs               import NRS
from tests.drapeaux          import Drapeaux
from tests.ndi                import NDI
from tests.psfs               import PSFS
from tests.groc               import GROC
from tests.had                import HAD

CERVICALGIE = register_template(BilanTemplate(
    template_id = "cervicalgie",
    nom         = "Cervicalgie",
    icone       = "🦴",
    description = "Bilan cervicalgie — NRS, drapeaux, NDI, PSFS, HAD, GROC",
    tests       = [
        NRS, Drapeaux, NDI, HAD, PSFS, GROC,
    ],
))
